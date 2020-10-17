import importlib
from tabulate import tabulate
from services.config import Configuration
from services.filters import get_instances_from_filters
from services.logger import print_red_and_exit
from models.instances import Account, Host


class Load(object):
    def __init__(self, account, region, cloud, filters):

        self.account = account
        self.region = region
        self.cloud = cloud
        self.filters = filters
        self.conf = Configuration()

        self.backend = importlib.import_module("backends." + self.conf.backend)

    def load_state(self):
        """Will read state data from specified backend."""

        fp = self.backend.Backend(self.account, self.cloud, self.conf.backend_path)
        return Account.parse_obj(fp.read_state())

    def load_host(self, instance_id: str) -> Host:
        """Will read state data from specified backend."""

        fp = self.backend.Backend(self.account, self.cloud, self.conf.backend_path)
        return Host.parse_obj(fp.read_host(instance_id))

    def print(self, account_obj: Account):
        """
        """

        data = list()

        self.validate(account_obj)

        filtered_instances = get_instances_from_filters(self.account_obj, self.filters)

        for vm in self.account_obj.vms:
            vm.instanceId in filtered_instances and data.append(
                [
                    vm.instanceId,
                    next((tag['Value'] for tag in vm.tags if tag['Key'] == 'Name'), None),
                    vm.publicIp,
                    vm.privateIp,
                    vm.key,
                    '\n'.join([tag['Key'] + ": " + tag['Value'] for tag in vm.tags])
                ]
            )

        print(tabulate(
            data,
            headers=["instanceId", "Name", "publicIp", "privateIp", "SSH Key", "tags"],
            tablefmt="rst"
        ))

    def validate(self, account_obj):
        """Checks if state_file_content is a proper Account object or exits."""

        isinstance(account_obj, Account) or \
            print_red_and_exit('Something wrong with your state file, you should refresh.')
