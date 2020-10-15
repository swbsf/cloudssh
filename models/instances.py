from typing import List
from pydantic import BaseModel


class VirtualMachine(BaseModel):
    instanceId: str
    tags: List[dict] = list()
    key: str = None
    publicIp: str = None
    privateIp: str = None


class Account(BaseModel):
    name: str
    vms: List[VirtualMachine] = list()
