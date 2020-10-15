import configparser


class Configuration(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    @property
    def backend(self) -> str:
        return self.config['default'].get('backend')

    @property
    def backend_path(self) -> str:
        return self.config['default'].get('backend_path')

    @property
    def usernames(self) -> list:
        users = self.config['default'].get('usernames') or 'root'
        return users.split(',')

    @property
    def ssh_key_path(self) -> str:
        return self.config['default'].get('ssh_key_path')
