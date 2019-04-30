import functools
import os
import requests


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


def GodaddyApi(**kwargs):
    def decorator(cls):
        def __init__(self):
            self._requests = JsonRequests(auth=GodaddyAuth(GODADDY_KEY, GODADDY_SECRET))
            self.__dict__.update(kwargs)
        cls.__init__ = __init__
        return cls
    return decorator


@GodaddyApi(_base='https://api.godaddy.com/v1/domains')
class GodaddyDomains(object):
    def list(self):
        return self._requests.get(f'{self._base}')

    def domain(self, domain):
        return self._requests.get(f'{self._base}/{domain}')

    def records(self, domain, type, name, **kwargs):
        return self._requests.get(f'{self._base}/{domain}/records/{type}/{name}', params=kwargs)

    def available(self, domain):
        return self._requests.get(f'{self._base}/available', params={ 'domain': domain })

    def suggest(self, query, **kwargs):
        return self._requests.get(f'{self._base}/suggest', params={ 'query': query, **kwargs })

    def tlds(self):
        return self._requests.get(f'{self._base}/tlds')


@GodaddyApi(_base='https://api.godaddy.com/v1/subscriptions')
class GodaddySubscriptions(object):
    def list(self, **kwargs):
        return self._requests.get(f'{self._base}', params=kwargs)

    def products(self):
        return self._requests.get(f'{self._base}/productGroups')


@GodaddyApi(_base='https://api.godaddy.com/v1/orders')
class GodaddyOrders(object):
    def list(self, **kwargs):
        return self._requests.get(f'{self._base}', params=kwargs)

    def order(self, order_id):
        return self._requests.get(f'{self._base}/{order_id}')
