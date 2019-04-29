import json
import os
import requests
import click
from dotenv import load_dotenv


load_dotenv()


GODADDY_KEY = os.getenv('GODADDY_KEY')
GODADDY_SECRET = os.getenv('GODADDY_SECRET')


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
    def available(self, domain):
        response = requests.get('https://api.godaddy.com/v1/domains/available', params={ 'domain': domain }, auth=GodaddyAuth(GODADDY_KEY, GODADDY_SECRET))
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
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))
