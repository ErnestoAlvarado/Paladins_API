import requests
import hashlib
import util
import config
from datetime import timedelta, datetime
import api_info
import exceptions
import time
from functools import wraps


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

        self.session = requests.Session()
        self.session_manager = SessionManager(api_info.DAILY_REQUEST_LIMIT, api_info.DAILY_SESSION_LIMIT,
                                              api_info.SESSION_DURATION)
        self.endpoint = "http://api.paladins.com/paladinsapi.svc/"

    def create_session(self):

        url = self.__create_url("createsession")
        success = self.session.get(url, timeout=5).json()
        msg = success['ret_msg']

        if msg == 'Approved':
            self.session_manager.set_session(success['session_id'], datetime.utcnow())

        return msg

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

    @retry(Exception, total_tries=3)
    def _make_request(self, method, optional_args=None):

        try:
            url = self.__create_url(method, optional_args)
            response = self.session.get(url, timeout=5).json()
            msg = response[0]['ret_msg']
        except ValueError:
            return error_message("Invalid Input", optional_args)
        except IndexError:
            return error_message("Not Found", optional_args)

        if msg == "Error while comparing Server and Client timestamp":
            raise exceptions.ServerAndClientTimeMismatch("Error with client and server timestamps")
        if msg == 'Exception - Timestamp' or msg == 'Invalid session id.':
            print("Session is invalid, attempting to make a new one, one sec...")
            if self.create_session() == 'Approved':
                print("session was created successfully!!!")
                return self._make_request(method, optional_args)
            raise exceptions.InvalidSession("Failed to create session, server and client timestamps not matching")
        if msg == "dailylimit (7500 requests reached)/404":
            raise exceptions.RateLimitReached("You have reached the maximum number of requests")

        return response

    def test_session(self):
        response = self._make_request('testsession')
        return response

    def get_server_status(self):
        server_status = self._make_request('gethirezserverstatus')
        return server_status

    def check_data_used(self):
        data_usage = self._make_request('getdataused')
        return data_usage

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

