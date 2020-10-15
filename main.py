import click
from commands.refresh import Refresh
from commands.show import FetchVM
from commands.ssh import Connect


@click.group()
@click.option('-a', '--account', default='default')
@click.option('-r', '--region', default='eu-west-1')
@click.option('-c', '--cloud', default='aws')
@click.pass_context
def cli(ctx, account, region, cloud):
    ctx.ensure_object(dict)
    ctx.obj['account'] = account
    ctx.obj['region'] = region
    ctx.obj['cloud'] = cloud
    #ctx.obj['filters'] = list() if filters is None else filters.split(',')


@cli.command()
@click.option('-f', '--filters', default=None, help='filter output with list of string, such as -f f1,f2')
@click.pass_context
def show(ctx, filters):
    """Show local state of account"""
    filters = list() if filters is None else filters.split(',')

    FetchVM(ctx.obj['account'], ctx.obj['region'], ctx.obj['cloud'], filters).show()


@cli.command()
@click.pass_context
def refresh(ctx):
    """Refresh state file for account"""
    Refresh(ctx.obj['account'], ctx.obj['region'], ctx.obj['cloud']).instances()


@cli.command()
@click.option('-f', '--filters', default=None, help='filter output with list of string, such as -f f1,f2')
@click.option('-b', '--bounce', is_flag=True, help='Tries to bounce on a bastion')
@click.pass_context
def ssh(ctx, filters, bounce):
    """Tries to connect to account with filtered output"""
    filters = list() if filters is None else filters.split(',')

    Connect(ctx.obj['account'], ctx.obj['region'], ctx.obj['cloud'], filters, bounce).ssh()


if __name__ == '__main__':
    cli(obj={})
