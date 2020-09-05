import requests
from requests import RequestException


def request(method, request_url, **kwargs):
    try:
        response = requests.Session().request(method=method, url=request_url, headers=kwargs.get('headers'),
                                              params=kwargs.get('params'), data=kwargs.get('data'),
                                              json=kwargs.get('json'))
    except RequestException as e:
        raise RequestException(e, method, request_url, kwargs)
    else:
        return response
