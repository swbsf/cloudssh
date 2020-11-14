
import importlib
from services.save import Save


class Refresh:
    def __init__(self, account, region, cloud):
        cp = importlib.import_module("cloud_providers." + cloud)
        self.vm = cp.VMInstancesFetch(account, region)

        self.account = account
        self.region = region
        self.cloud = cloud

    def instances(self):
        Save(
            self.account,
            self.region,
            self.cloud,
            self.vm.get_list()
        ).on_refresh()
