import sys
import json
from os import environ
from pathlib import Path
from services.logger import print_red
from services.save import SaveType
from models.interfaces.iBackend import iBackend


class Backend(iBackend):
    def __init__(self, account, cloud, backend_path=None):

        _backend_path = environ['HOME'] if backend_path is None else backend_path
        self._backend_path = _backend_path + "/.cloudssh/" + cloud + "/" + account

        try:
            Path(self._backend_path).mkdir(parents=True, exist_ok=True)
        except Exception:
            print_red('Config Error: backend_path must be a absolute path directory')
            sys.exit(1)

    def write(self, content: dict, save_type: SaveType):
        """Writes to backend_path/.cloudssh_state refreshed content.
        Parameters:
            content: instance of models.instances.VirtualMachines object
        Returns:
            content_changed: boolean, if state has changed
        """
        if not isinstance(save_type, SaveType):
            raise TypeError("Wrong value for save_type")

        filename = self._get_dst_path(content, save_type)

        content_changed = self.read(filename) != content.dict()

        if content_changed:
            with open(filename, 'w') as f:
                f.write(content.json(indent=4))

        return content_changed

    def read(self, path: str) -> dict:
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            Path(path).touch()
            return dict()
        except json.JSONDecodeError:
            print_red('State file is corrupt, removing.')
            Path(path).unlink()
            Path(path).touch()
            return dict()

    def _get_dst_path(self, content, save_type: SaveType) -> str:

        if save_type == SaveType.STATE:
            return self._backend_path + "/state.json"
        else:
            return self._backend_path + "/" + content.keys()[0]
