import functools
import json
import os
import requests
import click
from dotenv import load_dotenv


load_dotenv()


GODADDY_KEY = os.getenv('GODADDY_KEY')
GODADDY_SECRET = os.getenv('GODADDY_SECRET')


class JsonRequests(object):
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __getattr__(self, attr_name):
        attr = getattr(requests, attr_name)
        if not callable(attr):
            return attr
        @functools.wraps(attr)
        def attrwrapper(*args, **kwargs):
            result = attr(*args, **{ **self._kwargs, **kwargs })
            if not isinstance(result, requests.models.Response):
                return result
            result.raise_for_status()
            return result.json()
        return attrwrapper


class GodaddyAuth(requests.auth.AuthBase):
    def __init__(self, key, secret):
        self._credentials = {
            'scheme': 'sso-key',
            'key': key,
            'secret': secret,
        }

    def __call__(self, r):
        r.headers['Authorization'] = '{scheme} {key}:{secret}'.format(**self._credentials)
        return r


def GodaddyApi(cls):
    def init(self):
        self._requests = JsonRequests(auth=GodaddyAuth(GODADDY_KEY, GODADDY_SECRET))
    cls.__init__ = init
    return cls


@GodaddyApi
class GodaddyDomains(object):
    def list(self):
        return self._requests.get('https://api.godaddy.com/v1/domains')

    def domain(self, domain):
        return self._requests.get(f'https://api.godaddy.com/v1/domains/{domain}')

    def records(self, domain, type, name, **kwargs):
        return self._requests.get(f'https://api.godaddy.com/v1/domains/{domain}/records/{type}/{name}', params=kwargs)

    def available(self, domain):
        return self._requests.get('https://api.godaddy.com/v1/domains/available', params={ 'domain': domain })

    def suggest(self, query, **kwargs):
        return self._requests.get('https://api.godaddy.com/v1/domains/suggest', params={ 'query': query, **kwargs })

    def tlds(self):
        return self._requests.get('https://api.godaddy.com/v1/domains/tlds')


@GodaddyApi
class GodaddySubscriptions(object):
    def list(self, **kwargs):
        return self._requests.get('https://api.godaddy.com/v1/subscriptions', params=kwargs)


def printjson(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(json.dumps(result, indent=2))
    return wrapper


@click.group()
def main():
    pass


@main.group()
@click.pass_context
def domains(ctx):
    ctx.obj = GodaddyDomains()


@domains.command()
@click.pass_obj
@printjson
def list(godaddy):
    return godaddy.list()


@click.argument('domain')
@domains.command()
@click.pass_obj
@printjson
def domain(godaddy, domain):
    return godaddy.domain(domain)


@click.argument('domain')
@click.option('--type', required=True)
@click.option('--name', required=True)
@click.option('--limit')
@click.option('--offset')
@domains.command()
@click.pass_obj
@printjson
def records(godaddy, domain, type, name, **kwargs):
    return godaddy.records(domain, type, name, **kwargs)


@click.argument('domain')
@domains.command()
@click.pass_obj
@printjson
def available(godaddy, domain):
    return godaddy.available(domain)


@click.argument('query')
@click.option('--country')
@click.option('--limit')
@domains.command()
@click.pass_obj
@printjson
def suggest(godaddy, query, **kwargs):
    return godaddy.suggest(query, **kwargs)


@domains.command()
@click.pass_obj
@printjson
def tlds(godaddy):
    return godaddy.tlds()


@main.group()
@click.pass_context
def subscriptions(ctx):
    ctx.obj = GodaddySubscriptions()


@click.option('--limit')
@click.option('--offset')
@subscriptions.command()
@click.pass_obj
@printjson
def list(godaddy, **kwargs):
    return godaddy.list(**kwargs)
