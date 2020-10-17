import json
from os import environ
from pathlib import Path
from services.logger import print_red
from models.instances import Account, Host
from models.interfaces.iBackend import iBackend


class Backend(iBackend):
    def __init__(self, account, cloud, backend_path):

        self.ph = PathHandler(account, cloud, backend_path)

    def write_state(self, content=Account()) -> bool:
        """Writes state file."""
        path = self.ph.state_path

        return self._do_write(path, content)

    def write_host(self, content: Host) -> bool:
        """Writes host file."""
        path = self.ph.get_host_path(content.instanceId)

        return self._do_write(path, content)

    def _do_write(self, path: str, content: dict):
        """Writes a dict to file.
        Parameters:
            path: str. Full path of file to write.
            content: dict.
        """
        content_changed = self.read(path) != content.dict()

        if content_changed:
            with open(path, 'w') as f:
                f.write(content.json(indent=4))

        return content_changed

    def read_state(self) -> dict:

        path = self.ph.state_path
        return self.read(path)

    def read_host(self, instance_id) -> dict:

        path = self.ph.get_host_path(instance_id)
        return self.read(path)

    def read(self, path: str) -> dict:

        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Path(path).touch()
            return dict()
        except json.JSONDecodeError:
            print_red('State file is corrupt, removing.')
            Path(path).unlink()
            Path(path).touch()
            return dict()


class PathHandler(object):
    def __init__(self, account, cloud, backend_path=None):

        backend_path = environ['HOME'] if backend_path is None else backend_path
        self._backend_path = backend_path + "/.cloudssh/" + cloud + "/" + account

        try:
            Path(self._backend_path).mkdir(parents=True, exist_ok=True)
        except Exception:
            print_red('Config Error: backend_path must be a absolute path directory')
            exit(1)

    @property
    def backend_path(self):
        return self._backend_path

    @property
    def state_path(self):
        return self._backend_path + "/state.json"

    def get_host_path(self, instance_id: str):
        return self._backend_path + "/" + instance_id
