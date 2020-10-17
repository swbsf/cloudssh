from typing import List
from pydantic import BaseModel


class Host(BaseModel):
    instanceId: str = None
    tags: List[dict] = list()
    key: str = None
    publicIp: str = None
    privateIp: str = None
    username: str = None
    bounce_host: str = None


class Account(BaseModel):
    name: str = str()
    vms: List[Host] = list()
