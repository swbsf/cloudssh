import click
import os
import sys

import subprocess
from tabulate import tabulate

from services.load import Load
from services.save import Save
from services.errors import HostNotFound
from services.config import Configuration
from services.filters import get_instances_from_filters, get_tags_from_instanceIds
from services.logger import print_orange, print_light_grey
from models.instances import Host


class DoConnect(object):
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

        selected_vm = self.get_vm_from_instance_id(self.select_dst(self.filters))

        try:  # host file found
            self.connect_with_host_data(selected_vm.instanceId)
        except HostNotFound:  # host file not found
            try:
                self.connect_without_host_data(selected_vm.instanceId)
            except ConnectionError:  # could not connect at all.
                print_orange("Failed connecting.")
        except ConnectionError:  # could not connect with host file
            self.connect_without_host_data(selected_vm.instanceId)
            print_orange("Failed connecting.")
        # dst_ip = selected_vm.privateIp if self.bounce else selected_vm.publicIp

    def _do_connect(self, host: Host):

        if host.username:
            self._do_ssh_and_save(host)
        else:
            for user in self.conf.usernames:
                host.username = user
                host.publicIp = host.privateIp if host.publicIp is None else host.publicIp
                self._do_ssh_and_save(host)

        raise ConnectionError

    def _do_ssh_and_save(self, host: Host):

        with open(os.devnull, 'w') as FNULL:
            ssh = self._build_commands(host)

            print_light_grey('Trying: ' + ' '.join(ssh))
            proc = subprocess.run(ssh, text=True)

            if proc.returncode == 0:
                Save(
                    self.account,
                    self.region,
                    self.cloud,
                    host
                ).on_successful_connexion()
                FNULL.close()
                sys.exit(0)

    def _build_commands(self, host: Host) -> list:
        if not self.bounce:
            return [
                '/usr/bin/ssh',
                '-o', 'ConnectTimeout=2',
                '-i', self.conf.ssh_key_path + host.key + '.pem',
                host.username + '@' + host.publicIp
            ]
        else:
            try:
                bhost = self.content.load_host(self.select_dst(filters=[self.conf.bounce_host]))

                return [
                    '/usr/bin/ssh',
                    '-o', 'ConnectTimeout=2',
                    '-o', 'ProxyCommand=/usr/bin/ssh -W %h:%p -i ' +
                          self.conf.ssh_key_path + bhost.key +
                          '.pem ' + bhost.username +
                          '@' + bhost.publicIp,
                    '-i', self.conf.ssh_key_path + host.key + '.pem',
                    host.username + '@' + host.privateIp
                ]
            except Exception as e:
                print(e)

    def select_dst(self, filters: list) -> str:

        results = get_instances_from_filters(self.account_obj, filters)

        if len(results) > 1:
            return self.prompt_dst(results, get_tags_from_instanceIds(self.account_obj, list(results)))

        elif len(results) == 0:
            print_orange('No instance found, please change filters.')
            sys.exit(1)

        else:
            return results.pop()

    def prompt_dst(self, results: set, flattened_tags: dict) -> str:
        """
        If selector gets more then one answer, then we are prompting user to choose destination.
        Parameters:
            results: set (of str) of all filtered instanceId.
            flattened_tags: dict of all instanceId with a list of all their respective tags.
        Returns:
            str: instance Id of destination.
        """

        print_orange("Ambigous filter. Please refine.")

        data = list()
        for c, inst_id in enumerate(results):
            data.append([c, inst_id, '\n'.join([tag['Key'] + ": " + tag['Value'] for tag in flattened_tags[inst_id]])])

        data.append([c+1, "Exit."])

        print(tabulate(
            data,
            headers=["Id", "instanceId", "tags"],
            tablefmt="fancy_grid"
        ))

        value = click.prompt('Please choose destination', type=int)
        if value == (c + 1):
            exit(0)

        return list(results)[value]

    def get_vm_from_instance_id(self, instance_id: str) -> Host:
        for i, vm in enumerate(self.account_obj.vms):
            if vm.instanceId == instance_id:
                return self.account_obj.vms[i]

    def connect_with_host_data(self, instance_id: str):
        host_obj = self.content.load_host(instance_id)

        if host_obj.instanceId:
            print_light_grey('Found host data, trying to connect...')
            self._do_connect(host_obj)
        else:
            raise HostNotFound

    def connect_without_host_data(self, instance_id: str):
        print_light_grey('Host data not found, trying to find a connection path...')

        host_obj = self.get_vm_from_instance_id(instance_id)
        self._do_connect(host_obj)
