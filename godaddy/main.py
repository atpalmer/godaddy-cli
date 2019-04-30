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

    def mine(self):
        response = self._requests.get('https://api.godaddy.com/v1/domains')
        return response

    def available(self, domain):
        response = self._requests.get('https://api.godaddy.com/v1/domains/available', params={ 'domain': domain })
        return response


@click.group()
def main():
    pass


@main.group()
def domains():
    pass


@click.argument('domain')
@domains.command()
def available(domain):
    godaddy = GodaddyDomains()
    response = godaddy.available(domain)
    print(json.dumps(response, indent=2))


@domains.command()
def mine():
    godaddy = GodaddyDomains()
    response = godaddy.mine()
    print(json.dumps(response, indent=2))
