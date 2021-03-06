from services.load import Load


class FetchVM:
    def __init__(self, account, region, cloud, filters):

        self.account = account
        self.region = region
        self.cloud = cloud
        self.filters = filters

    def show(self):
        obj = Load(self.account, self.region, self.cloud, self.filters)
        state_obj = obj.load_state()
        obj.print(state_obj)
