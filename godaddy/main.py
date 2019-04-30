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


class GodaddyDomains(object):
    def __init__(self):
        self._requests = JsonRequests(auth=GodaddyAuth(GODADDY_KEY, GODADDY_SECRET))

    def list(self):
        response = self._requests.get('https://api.godaddy.com/v1/domains')
        return response

    def domain(self, domain):
        response = self._requests.get(f'https://api.godaddy.com/v1/domains/{domain}')
        return response

    def available(self, domain):
        response = self._requests.get('https://api.godaddy.com/v1/domains/available', params={ 'domain': domain })
        return response

    def suggest(self, query, **kwargs):
        response = self._requests.get('https://api.godaddy.com/v1/domains/suggest', params={ 'query': query, **kwargs })
        return response

    def tlds(self):
        response = self._requests.get('https://api.godaddy.com/v1/domains/tlds')
        return response


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
