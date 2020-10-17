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
from models.instances import Host, Account


class DoConnect(object):
    def __init__(self, account, region, cloud, filters, bounce):

        self.account = account
        self.region = region
        self.cloud = cloud
        self.filters = filters
        self.bounce = bounce

        self.conf = Configuration()

    def connect(self):
        """Will actually run the computed SSH command."""

        account_obj, instance_id = self.select_dst()
        selected_vm = self.get_vm_from_instance_id(account_obj, instance_id)

        try:
            self.connect_with_host_data(selected_vm.instanceId)
        except HostNotFound:
            self.connect_without_host_data(selected_vm.instanceId)

        # dst_ip = selected_vm.privateIp if self.bounce else selected_vm.publicIp

    def _do_connect(self, host: Host):

        if host.username:
            self._do_ssh_and_save(host)
        else:
            for user in self.conf.usernames:
                host.username = user
                self._do_ssh_and_save(host)

    def _do_ssh_and_save(self, host: Host):
        FNULL = open(os.devnull, 'w')

        ssh = [
            '/usr/bin/ssh',
            '-o', 'ConnectTimeout=2',
            '-i', self.conf.ssh_key_path + host.key + '.pem',
            host.username + '@' + host.publicIp
        ]

        print_light_grey('Trying: ' + ' '.join(ssh))
        proc = subprocess.Popen(ssh, stderr=FNULL)
        proc.communicate()

        if proc.returncode == 0:
            Save(
                self.account,
                self.region,
                self.cloud,
                host
            ).on_successful_connexion()
            FNULL.close()
            sys.exit(0)

        FNULL.close()
        print_orange("Failed connecting.")

    def select_dst(self) -> str:
        self.content = Load(self.account, self.region, self.cloud, self.filters)
        account_obj = self.content.load_state()
        self.content.validate(account_obj)

        results = get_instances_from_filters(account_obj, self.filters)

        if len(results) > 1:
            return account_obj, self.prompt_dst(results, get_tags_from_instanceIds(account_obj, list(results)))

        elif len(results) == 0:
            print_orange('No instance found, please change filters.')
            return None, None

        else:
            return account_obj, results.pop()

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
            tablefmt="rst"
        ))

        value = click.prompt('Please choose destination', type=int)
        if value == (c + 1):
            exit(0)

        return list(results)[value]

    def get_vm_from_instance_id(self, account_obj: Account, instance_id: str) -> Host:
        for i, vm in enumerate(account_obj.vms):
            if vm.instanceId == instance_id:
                return account_obj.vms[i]

    def connect_with_host_data(self, instance_id: str):
        host_obj = self.content.load_host(instance_id)

        if host_obj.instanceId:
            print_light_grey('Found host data, trying to connect...')
            self._do_connect(host_obj)
        else:
            raise HostNotFound

    def connect_without_host_data(self, instance_id: str):
        print_light_grey('Host data not found, trying to find a connection path...')

        account_obj = self.content.load_state()
        host_obj = self.get_vm_from_instance_id(account_obj, instance_id)
        self._do_connect(host_obj)

    def _create_connection_path_obj(self, instanceId: str, dstIp: str, key: str, username: str) -> dict:
        """Creates an object with all necessary informations to connect to host"""
        return {
            instanceId: {
                "username": username,
                "dstIp": dstIp,
                "key": key
            }
        }
