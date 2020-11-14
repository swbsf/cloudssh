
from services.ssh import ConnectionManager


class Connect:
    def __init__(self, account, region, cloud, filters, bounce):

        self.account = account
        self.region = region
        self.cloud = cloud
        self.filters = filters
        self.bounce = bounce

    def ssh(self):
        ConnectionManager(
            self.account,
            self.region,
            self.cloud,
            self.filters,
            self.bounce
        ).connect()
