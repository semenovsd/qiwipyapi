from qiwipyapi.errors import main_exception, QiwiError


def response(response):
    if response.status_code in [200, 201]:
        try:
            response_json = response.json()
            return response_json
        except AttributeError:
            return response
    else:
        e = main_exception(response)
        raise QiwiError(e, response.text)
