import importlib
from services.config import Configuration
from services.logger import print_green, print_orange
from models.instances import Account


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

        fp = self.backend.Backend(self.account, self.cloud, self.conf.backend_path)
        content_changed = fp.write_state(self.content)

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
        fp.write_host(self.content)
