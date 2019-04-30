from .misc import GodaddyApi


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
