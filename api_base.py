import hashlib
import util, config, api_info, exceptions
from datetime import timedelta, datetime
import time
from functools import wraps
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter


class SessionManager:
    def __init__(self, max_requests, max_sessions, session_duration, session_id=None):
        self.max_requests = max_requests
        self.max_sessions = max_sessions
        self.session_duration = session_duration
        self.session_id = session_id
        self.session_timer = None
        self.requests_made = 0
        self.session_used = 0

    def set_session(self, session_id, session_timestamp):
        self.session_id = session_id
        self.session_timer = session_timestamp

    def session_expired(self):
        if self.session_id:
            return (datetime.utcnow() - self.session_timer) / timedelta(minutes=1) >= self.session_duration

        return -1

    def made_request(self):
        self.requests_made += 1

    def created_session(self):
        self.session_used += 1

    def requests_limit_reached(self):
        return self.requests_made >= self.max_requests

    def sessions_limit_reached(self):
        return self.session_used >= self.max_sessions

    def session_exists(self):
        return self.session_id is not None and not self.session_expired()

    def get_session(self):
        return self.session_id


def retry(exception, total_tries=4, initial_wait=0.5, backoff_factor=2):
    """
    calling the decorated function applying an exponential backoff.
    Args:
        exceptions: Exeption(s) that trigger a retry, can be a tuble
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier (e.g. value of 2 will double the delay each retry).
        logger: logger to be used, if none specified print
    """
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries + 1, initial_wait
            while _tries > 1:
                try:
                    return f(*args, **kwargs)
                except exception as e:
                    _tries -= 1
                    print("remaining tries: {}".format(_tries))
                    print("exception:", e)
                    if _tries == 1:
                        print("Api call was unsuccessful: {}".format(e))

                    time.sleep(_delay)
                    _delay *= backoff_factor

        return func_with_retries
    return retry_decorator


def error_message(message, search_id):
    return {'ret_msg': message, 'id': search_id}


class BaseApi:
    def __init__(self, dev_id=None, auth_key=None):
        if dev_id is None and auth_key is None:
            self.dev_id = config.dev_id
            self.auth_key = config.auth_id
        else:
            self.dev_id = dev_id
            self.auth_key = auth_key

        self.session_manager = SessionManager(api_info.DAILY_REQUEST_LIMIT, api_info.DAILY_SESSION_LIMIT,
                                              api_info.SESSION_DURATION)
        self.endpoint = "http://api.paladins.com/paladinsapi.svc/"
        self.refreshing = False
        self.client_session = None
        self.rate_limiter = AsyncLimiter(1, 1)

    async def start_client_session(self):
        self.client_session = aiohttp.ClientSession()

    async def create_session(self):
        if not self.refreshing:
            self.refreshing = True

        url = self.__create_url("createsession")
        print("Going to make a new session")
        async with aiohttp.request('GET', url, json=True) as resp:
            success = await resp.json()
            print(success)
        msg = success['ret_msg']

        if msg == 'Approved':
            print("session approved")
            self.session_manager.set_session(success['session_id'], datetime.utcnow())
            self.refreshing = False

        return msg == 'Approved'

    def __create_url(self, method, optional_args=None):
        # creating a new session
        if method == 'createsession':
            sig_and_timestamp = '{}/{}'.format(self.__generate_signature(method), util.time_stamp())
        elif optional_args is None:
            sig_and_timestamp = '{}/{}/{}'.format(self.__generate_signature(method), self.session_manager.get_session(),
                                                  util.time_stamp())
        else:
            sig_and_timestamp = '{}/{}/{}/{args}'.format(self.__generate_signature(method), self.session_manager.get_session(),
                                                         util.time_stamp(), args=optional_args)

        base_path = '{}{}/{}/'.format(self.endpoint, method + 'Json', self.dev_id)
        return base_path + sig_and_timestamp

    async def fetch(self, tasks):
        if not self.session_manager.session_exists():
            if not await self.create_session():
                print("Could not create a session ")
                return

        # create Session Manager
        await self.start_client_session()

        requests = []

        for task in tasks:
            async with self.rate_limiter:
                temp = asyncio.create_task(task)
                requests.append(temp)
                await asyncio.sleep(0)

        stuff = await asyncio.gather(*requests)

        await self.client_session.close()
        return stuff

    @retry(Exception, total_tries=3)
    async def _make_request(self, method, optional_args=None):
        try:
            url = self.__create_url(method, optional_args)

            async with self.client_session.get(url) as resp:
                try:
                    response = await resp.json()
                    print('after request {}'.format(url))
                except:
                    return

            msg = response[0]['ret_msg']
        except ValueError:
            return error_message("Invalid Input", optional_args)
        except IndexError:
            return error_message("Not Found", optional_args)

        if msg == "Error while comparing Server and Client timestamp":
            raise exceptions.ServerAndClientTimeMismatch("Error with client and server timestamps")
        if msg == 'Exception - Timestamp' or msg == 'Invalid session id.':
            print("Session is invalid, attempting to make a new one, one sec...")
            await self.limiter.pause_tasks()
            await self.create_session()
            await self.limiter.resume_tasks()
            return await self._make_request(method, optional_args)

        if msg == "dailylimit (7500 requests reached)/404":
            raise exceptions.RateLimitReached("You have reached the maximum number of requests")

        return response

    def test_session(self):
        response = self._make_request('testsession')
        return response

    def get_server_status(self):
        server_status = self._make_request('gethirezserverstatus')
        return server_status

    def get_leaderboard(self, queue, tier, season):
        leaderboard = self._make_request('getleagueleaderboard', '{}/{}/{}'.format(queue, tier, season))
        return leaderboard

    def get_seasons(self, queue):
        seasons = self._make_request('getleagueseasons', queue)
        return seasons

    def get_patch_info(self):
        patch_info = self._make_request('getpatchinfo')
        return patch_info

    def ping(self):
        return self.session.get(self.endpoint+'pingJson').json()

    def __generate_signature(self, method):
        signature = hashlib.md5((self.dev_id + method + self.auth_key + util.time_stamp()).encode())
        return signature.hexdigest()

