import time
from functools import wraps


# # https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry

#
# @retry(Exception, tries=3, delay=5)
# def test_fail(text):
#     raise Exception("Fail")
#

# test_fail("it works!")

#
# def retry(retry_count=5, delay=5, allowed_exceptions=()):
#     def decorator(f):
#         @functools.wraps(f)
#         async def wrapper(*args, **kwargs):
#             result = None
#             last_exception = None
#             for _ in range(retry_count):
#                 try:
#                     result = func(*func_args, **kwargs)
#                     if result: return result
#                 except allowed_exceptions as e:
#                     last_exception = e
#                 log.debug("Waiting for %s seconds before retrying again")
#                 await asyncio.sleep(delay)
#
#             if last_exception is not None:
#                 raise type(last_exception) from last_exception
#                 # Python 2
#                 # import sys
#                 # raise type(last_exception), type(last_exception)(last_exception), sys.exc_info()[2]
#
#             return result
#
#         return wrapper
#
#     return decorator
