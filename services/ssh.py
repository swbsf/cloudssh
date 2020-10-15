import click
import os

import subprocess
from tabulate import tabulate

from services.load import Load
from services.save import Save
from services.config import Configuration
from services.filters import get_instances_from_filters, get_tags_from_instanceIds
from services.logger import print_orange, print_light_grey
from models.instances import VirtualMachine


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

        selected_vm = self.get_vm_from_instance_id(self.select_dst())

        FNULL = open(os.devnull, 'w')

        # dst_ip = selected_vm.privateIp if self.bounce else selected_vm.publicIp

        for user in self.conf.usernames:
            if selected_vm.publicIp:
                ssh = [
                    '/usr/bin/ssh',
                    '-o', 'ConnectTimeout=2',
                    '-i', self.conf.ssh_key_path + selected_vm.key + '.pem',
                    user + '@' + selected_vm.publicIp
                ]

                print_light_grey('Trying: ' + ' '.join(ssh))
                proc = subprocess.Popen(ssh, stderr=FNULL)
                proc.communicate()

                if proc.returncode == 0:
                    fp = Save(
                        self.account,
                        self.region,
                        self.cloud,
                        self._create_connection_path_obj(
                            selected_vm.publicIp,
                            self.conf.ssh_key_path + selected_vm.key + '.pem',
                            user
                        )
                    )
                    fp.on_successful_connexion()

                    FNULL.close()
                    exit()

        FNULL.close()
        print_orange("Failed connecting.")

    def select_dst(self) -> str:
        self.content = Load(self.account, self.region, self.cloud, self.filters)
        self.content.load()
        self.content.validate()

        results = get_instances_from_filters(self.content.account_obj, self.filters)

        if len(results) > 1:
            return self.prompt_dst(results, get_tags_from_instanceIds(self.content.account_obj, list(results)))

        elif len(results) == 0:
            print_orange('No instance found, please change filters.')

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
            tablefmt="rst"
        ))

        value = click.prompt('Please choose destination', type=int)
        if value == (c + 1):
            exit(0)

        return list(results)[value]

    def get_vm_from_instance_id(self, instance_id) -> VirtualMachine:
        for i, vm in enumerate(self.content.account_obj.vms):
            if vm.instanceId == instance_id:
                return self.content.account_obj.vms[i]

    def _create_connection_path_obj(instanceId: str, dstIp: str, key: str, username: str) -> dict:
        """Creates an object with all necessary informations to connect to host"""
        return {
            instanceId: {
                "username": username,
                "dstIp": dstIp,
                "key": key
            }
        }
