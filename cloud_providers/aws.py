
import boto3
from os import environ
from models.interfaces.iProvider import iInstancesFetch
from models.instances import VirtualMachine, Account


class VMInstancesFetch(iInstancesFetch):
    def __init__(self, profile, region):
        environ['AWS_DEFAULT_REGION'] = region
        environ['AWS_PROFILE'] = profile
        self.ec2 = boto3.client('ec2')

    def get_list(self):
        """
        Parameters:
        None

        Returns:
        Instance of model.instances.VirtualMachines object
        """

        self._get_running_instances()

        return self.extract_metadata()

    def _get_running_instances(self):
        """Stores EC2 instances with 'running' state."""

        self.running_instances = self.ec2.describe_instances(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]
        )

    def extract_metadata(self):
        """Extract metadata listed in models.instances.VirtualMachine from
        running_instances object"""

        vm_list = Account(name=environ['AWS_PROFILE'])

        for group in self.running_instances['Reservations']:
            for inst in group['Instances']:
                vm_list.vms.append(
                    VirtualMachine(
                        instanceId=inst['InstanceId'],
                        tags=inst.get('Tags') if inst.get('Tags') else list(),
                        key=inst.get('KeyName'),
                        publicIp=inst.get('PublicIpAddress'),
                        privateIp=inst.get('PrivateIpAddress')
                    )
                )

        return vm_list
