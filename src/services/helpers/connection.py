import subprocess

from models.instances import Host, Account
from services.logger import print_light_grey
from services.save import Save


class DoConnectAndSave(object):
    def __init__(self, host: Host, account_obj: Account):
        self.host = host
        self.account_obj = account_obj

    def lazy_connect(self):
        """
        Will just try to connect and run a simple command.
        """
        cmd = [
            '/usr/bin/ssh',
            '-o', 'ConnectTimeout=2',
            '-i', self.host.connectionString.keyPath,
            self.host.connectionString.username + '@' + self.host.connectionString.connectionIP,
            'true'
        ]

        with ConnectAndSave(cmd, self.host, self.account_obj) as connStatus:
            return connStatus

    def bounce_lazy_connect(self, bounce_host: Host):
        """
        Will just try to connect through a bounce host and run a simple command.
        """
        cmd = [
            '/usr/bin/ssh',
            '-o', 'ConnectTimeout=2',
            '-o', 'ProxyCommand=/usr/bin/ssh -W %h:%p -i ' +
                  bounce_host.connectionString.keyPath + ' ' + bounce_host.connectionString.username +
                  '@' + bounce_host.connectionString.connectionIP,
            '-i', self.host.connectionString.keyPath,
                  self.host.connectionString.username +
                  '@' + self.host.connectionString.connectionIP,
            'true'
        ]

        with ConnectAndSave(cmd, self.host, self.account_obj) as connStatus:
            return connStatus

    def regular_connect(self):
        """
        Will run a proper connection, no bounce.
        """
        cmd = [
            '/usr/bin/ssh',
            '-o', 'ConnectTimeout=2',
            '-i', self.host.connectionString.keyPath,
            self.host.connectionString.username + '@' + self.host.connectionString.connectionIP,
        ]

        with ConnectAndSave(cmd, self.host, self.account_obj) as connStatus:
            return connStatus

    def bounce_regular_connect(self, bounce_host: Host):
        """
        Will run a proper connection, with bounce.
        """
        cmd = [
            '/usr/bin/ssh',
            '-o', 'ConnectTimeout=2',
            '-o', 'ProxyCommand=/usr/bin/ssh -W %h:%p -i ' +
                  bounce_host.connectionString.keyPath + ' ' + bounce_host.connectionString.username +
                  '@' + bounce_host.connectionString.connectionIP,
            '-i', self.host.connectionString.keyPath,
                  self.host.connectionString.username +
                  '@' + self.host.connectionString.connectionIP
        ]

        with ConnectAndSave(cmd, self.host, self.account_obj) as connStatus:
            return connStatus


class ConnectAndSave():
    def __init__(self, command: list, host: Host, account_obj: Account):
        self.command = command
        self.host = host
        self.account_obj = account_obj

    def __enter__(self):
        self.proc = simpleconnect(self.command)
        return self.proc.returncode

    def __exit__(self, type, value, traceback):
        if self.proc.returncode == 0:
            Save(
                account=self.account_obj.name,
                region=None,
                cloud=self.account_obj.cloud,
                content=self.host
            ).on_successful_connexion()


def simpleconnect(command: list) -> int:
    print_light_grey('Trying: ' + ' '.join(command))
    return subprocess.run(command, text=True)
