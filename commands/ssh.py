
from services.ssh import DoConnect


class Connect:
    def __init__(self, account, region, cloud, filters, bounce):

        self.account = account
        self.region = region
        self.cloud = cloud
        self.filters = filters
        self.bounce = bounce

    def ssh(self):
        DoConnect(
            self.account,
            self.region,
            self.cloud,
            self.filters,
            self.bounce
        ).connect()
