import functools
import json
import click
from .core import GodaddyDomains, GodaddySubscriptions, GodaddyOrders


def printjson(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(json.dumps(result, indent=2))
    return wrapper


def groupcommand(group):
    def decorator(func):
        @group.command()
        @click.pass_obj
        @printjson
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


@click.group()
def main():
    pass


@main.group()
@click.pass_context
def domains(ctx):
    ctx.obj = GodaddyDomains()


@groupcommand(domains)
def list(godaddy):
    return godaddy.list()


@click.argument('domain')
@groupcommand(domains)
def domain(godaddy, domain):
    return godaddy.domain(domain)


@click.argument('domain')
@click.option('--type', required=True)
@click.option('--name', required=True)
@click.option('--limit')
@click.option('--offset')
@groupcommand(domains)
def records(godaddy, domain, type, name, **kwargs):
    return godaddy.records(domain, type, name, **kwargs)


@click.argument('domain')
@groupcommand(domains)
def available(godaddy, domain):
    return godaddy.available(domain)


@click.argument('query')
@click.option('--country')
@click.option('--limit')
@groupcommand(domains)
def suggest(godaddy, query, **kwargs):
    return godaddy.suggest(query, **kwargs)


@groupcommand(domains)
def tlds(godaddy):
    return godaddy.tlds()


@main.group()
@click.pass_context
def subscriptions(ctx):
    ctx.obj = GodaddySubscriptions()


@click.option('--limit')
@click.option('--offset')
@groupcommand(subscriptions)
def list(godaddy, **kwargs):
    return godaddy.list(**kwargs)


@groupcommand(subscriptions)
def products(godaddy):
    return godaddy.products()


@main.group()
@click.pass_context
def orders(ctx):
    ctx.obj = GodaddyOrders()


@click.option('--limit')
@click.option('--offset')
@groupcommand(orders)
def list(godaddy, **kwargs):
    return godaddy.list(**kwargs)


@click.argument('order-id')
@groupcommand(orders)
def order(godaddy, order_id):
    return godaddy.order(order_id)
