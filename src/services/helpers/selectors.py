import click
import sys
from tabulate import tabulate

from models.instances import Host, Account
from services.load import Load
from services.logger import print_orange
from services.filters import get_instances_from_filters, get_tags_from_instanceIds


class Selector(object):
    def __init__(self, account_obj: Account, filters):
        self.account_obj = account_obj
        self.filters = filters
        self.load = Load(account_obj.name, account_obj.region, account_obj.cloud, filters)

    def select_host_from_state_file(self) -> Host:
        results = get_instances_from_filters(self.account_obj, self.filters)

        if len(results) > 1:
            dst_instance = self.prompt_dst(results, get_tags_from_instanceIds(self.account_obj, list(results)))
            return self.get_host_from_instance_id(dst_instance)

        elif len(results) == 0:
            print_orange('No instance found, please change filters.')
            sys.exit(1)

        else:
            return self.get_host_from_instance_id(results.pop())

    def select_host_from_host_file(self) -> Host:
        results = get_instances_from_filters(self.account_obj, self.filters)

        if len(results) > 1:
            dst_instance = self.prompt_dst(results, get_tags_from_instanceIds(self.account_obj, list(results)))
            return self.load.load_host(dst_instance)

        elif len(results) == 0:
            print_orange('No instance found, please change filters.')
            sys.exit(1)

        else:
            return self.load.load_host(results.pop())

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

    def get_host_from_instance_id(self, instance_id: str) -> Host:
        for i, vm in enumerate(self.account_obj.vms):
            if vm.instanceId == instance_id:
                return self.account_obj.vms[i]
