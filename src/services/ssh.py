import sys


from services.load import Load
from services.errors import HostNotFound
from services.config import Configuration
from services.logger import print_orange, print_light_grey
from services.helpers.selectors import Selector
from services.helpers.connection import DoConnectAndSave
from services.helpers.discovery import DiscoverHost
from models.instances import Host


class ConnectionManager(object):
    def __init__(self, account, region, cloud, filters, bounce):

        self.account = account
        self.region = region
        self.cloud = cloud
        self.filters = filters
        self.bounce = bounce

        self.conf = Configuration()

        self.content = Load(self.account, self.region, self.cloud, self.filters)
        self.account_obj = self.content.load_state()
        self.content.validate(self.account_obj)

    def connect(self):
        """Will actually run the computed SSH command."""

        # Get destination Host object
        selected_vm = Selector(self.account_obj, self.filters).select_host_from_state_file()

        try:  # host file found
            self.connect_with_host_data(selected_vm)
        except HostNotFound:  # host file not found
            try:
                self.connect_without_host_data(selected_vm, bounce=self.bounce)
            except ConnectionError:  # could not connect at all.
                print_orange("Failed connecting.")

    def get_vm_from_instance_id(self, instance_id: str) -> Host:
        for i, vm in enumerate(self.account_obj.vms):
            if vm.instanceId == instance_id:
                return self.account_obj.vms[i]

    def connect_with_host_data(self, host: Host):
        """
        Try to open host file and bounce host file, connect if exists.
        """
        host_obj = self.content.load_host(host.instanceId)

        if host_obj.connectionString:
            print_light_grey('Found host data, trying to connect...')

            # Has a bounce host.
            if host_obj.connectionString.bounce_host:
                bounce_host = DiscoverHost(self.account_obj, bounce=True).get_bounce()

                if not DoConnectAndSave(host_obj, self.account_obj).bounce_regular_connect(bounce_host):
                    sys.exit(0)
            else:
                if not DoConnectAndSave(host_obj, self.account_obj).regular_connect():
                    sys.exit(0)

            print_orange('Found host data is obsolete, trying to find a new path...')

        raise HostNotFound

    def connect_without_host_data(self, host: Host, bounce: bool):
        """
        Host has no host file, so we will try to find a way to get to it.
        """
        print_light_grey('Host data not found, trying to find a connection path...')

        if bounce:
            bounce_host = DiscoverHost(self.account_obj, bounce=True).get_bounce()
            host = DiscoverHost(self.account_obj, bounce=True).discover_host(host, bounce_host)

            if not DoConnectAndSave(host, self.account_obj).bounce_regular_connect(bounce_host):
                sys.exit(0)
        else:
            host = DiscoverHost(self.account_obj, bounce=False).discover_host(host)

            if not DoConnectAndSave(host, self.account_obj).regular_connect():
                sys.exit(0)
