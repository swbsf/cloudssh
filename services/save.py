import importlib
from services.config import Configuration
from services.logger import print_green, print_orange
from models.instances import Account
from enum import Enum


class SaveType(Enum):
    HOST = "host"
    STATE = "state"


class Save(object):
    def __init__(self, account, region, cloud, content):

        self.account = account
        self.region = region
        self.cloud = cloud
        self.conf = Configuration()
        self.content = content

        self.backend = importlib.import_module("backends." + self.conf.backend)

    def on_refresh(self):
        """Will write refreshed account data to specified backend."""

        # state_object = self._build_state_object()

        fp = self.backend.Backend(self.account, self.cloud, self.conf.backend_path)
        content_changed = fp.write(self.content, SaveType.STATE)

        if content_changed:
            print_orange('State changed.')
        else:
            print_green('State already up-to-date.')

    def _build_state_object(self):
        """Builds the final state file such as:
        [{"provider":]
        """
        return Account(
            name=self.account,
            vms=self.content
        )

    def on_successful_connexion(self):
        fp = self.backend.Backend(self.account, self.cloud, self.conf.backend_path)
        content_changed = fp.write(self.content, SaveType.HOST)
