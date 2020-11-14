from typing import List
from pydantic import BaseModel


class ConnectionString(BaseModel):
    username: str = str()
    connectionIP: str = str()
    keyPath: str = str()
    bounce_host: str = str()


class Host(BaseModel):
    instanceId: str = None
    tags: List[dict] = list()
    key: str = str()
    publicIp: str = str()
    privateIp: str = str()
    connectionString: ConnectionString = None


class Account(BaseModel):
    name: str = str()
    cloud: str = str()
    region: str = str()
    vms: List[Host] = list()
