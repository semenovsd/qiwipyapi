from functools import partial
import random # producing random errors for this example

from tenacity import retry, stop_after_delay, wait_fixed, retry_if_exception_type

# Custom error type for this example
class CommunicationError(Exception):
    pass

# Define shorthand decorator for the used settings.
retry_on_communication_error = partial(
    retry,
    stop=stop_after_delay(10),  # max. 10 seconds wait.
    wait=wait_fixed(0.4),  # wait 400ms
    retry=retry_if_exception_type(CommunicationError),
)()


@retry_on_communication_error
def do_something_unreliable(i):
    if random.randint(1, 5) == 3:
        print('Run#', i, 'Error occured. Retrying.')
        raise CommunicationError()




import time
from functools import wraps

# https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
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
                except ExceptionToCheck, e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print msg
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


@retry(Exception, tries=4)
def test_fail(text):
    raise Exception("Fail")

test_fail("it works!")


import functools
import asyncio

def retry(retry_count=5, delay=5, allowed_exceptions=()):
    def decorator(f):
        @functools.wraps(f)
        async def wrapper(*args, **kwargs):
            result = None
            last_exception = None
            for _ in range(retry_count):
                try:
                    result = func(*func_args, **kwargs)
                    if result: return result
                except allowed_exceptions as e:
                    last_exception = e
                log.debug("Waiting for %s seconds before retrying again")
                await asyncio.sleep(delay)

            if last_exception is not None:
                raise type(last_exception) from last_exception
                # Python 2
                # import sys
                # raise type(last_exception), type(last_exception)(last_exception), sys.exc_info()[2]

            return result

        return wrapper
    return decorator


## C
# https://docs.microsoft.com/en-us/azure/architecture/patterns/retry#example
private int retryCount = 3;
private readonly TimeSpan delay = TimeSpan.FromSeconds(5);

public async Task OperationWithBasicRetryAsync()
{
  int currentRetry = 0;

  for (;;)
  {
    try
    {
      // Call external service.
      await TransientOperationAsync();

      // Return or break.
      break;
    }
    catch (Exception ex)
    {
      Trace.TraceError("Operation Exception");

      currentRetry++;

      // Check if the exception thrown was a transient exception
      // based on the logic in the error detection strategy.
      // Determine whether to retry the operation, as well as how
      // long to wait, based on the retry strategy.
      if (currentRetry > this.retryCount || !IsTransient(ex))
      {
        // If this isn't a transient error or we shouldn't retry,
        // rethrow the exception.
        throw;
      }
    }

    // Wait to retry the operation.
    // Consider calculating an exponential delay here and
    // using a strategy best suited for the operation and fault.
    await Task.Delay(delay);
  }
}

// Async method that wraps a call to a remote service (details not shown).
private async Task TransientOperationAsync()
{
  ...
}