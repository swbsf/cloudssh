import sys

from models.instances import Host
from services.config import Configuration
from services.logger import print_orange
from .selectors import Selector
from .connection import DoConnectAndSave


class DiscoverHost(object):
    def __init__(self, account_obj, bounce=False):

        self.account_obj = account_obj
        self.bounce = bounce
        self.conf = Configuration()

    def get_bounce(self):
        bounce_host = Selector(self.account_obj, filters=[self.conf.bounce_host]).select_host_from_host_file()

        # If no host file, then get it from state file
        if bounce_host.connectionString is None:
            bounce_host = Selector(self.account_obj, filters=[self.conf.bounce_host]).select_host_from_state_file()
            bounce_host = self.discover_bounce(bounce_host)

        return bounce_host

    def get_host(self):
        host = Selector(self.account_obj, filters=[self.conf.bounce_host]).select_host_from_state_file()

        if host.connectionString is None:
            host = self.discover_bounce(host)

        return host

    def discover_bounce(self, host: Host) -> Host:
        for user in self.conf.usernames:
            host.connectionString.username = user
            host.connectionString.connectionIP = host.privateIp if host.publicIp is None else host.publicIp
            host.connectionString.keyPath = self.conf.ssh_key_path + host.key + '.pem'

            # Means return code = 0, which is a success
            if not DoConnectAndSave(host, self.account_obj).lazy_connect():
                return host

        print_orange('Failed finding a connection path for host, exiting.')
        sys.exit(1)

    def discover_host(self, host: Host, bounce_host=Host()) -> Host:
        host.connectionString.keyPath = self.conf.ssh_key_path + host.key + '.pem'

        for user in self.conf.usernames:
            host.connectionString.username = user

            if self.bounce:
                host.connectionString.connectionIP = host.privateIp
                host.connectionString.bounce_host = bounce_host.instanceId

                # Means return code = 0, which is a success
                if not DoConnectAndSave(host, self.account_obj).bounce_lazy_connect(bounce_host):
                    return host

            else:
                host.connectionString.connectionIP = host.privateIp if host.publicIp is None else host.publicIp

                if not DoConnectAndSave(host, self.account_obj).lazy_connect():
                    return host

        print_orange('Failed finding a connection path for host, exiting.')
        sys.exit(1)
