import hashlib
from .. import config
from . import api_info, exceptions, util
from datetime import timedelta, datetime
import time
from functools import wraps
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
from iteration_utilities import deepflatten


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


class PaladinApi:
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

        success = await self.__send_request(url)
        print(success)
        msg = success['ret_msg']

        if msg == 'Approved':
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

        try:
            for task in tasks:
                async with self.rate_limiter:
                    new_task = asyncio.create_task(task)
                    requests.append(new_task)
                    await asyncio.sleep(0)

            finished_requests = await asyncio.gather(*requests)
        except:
            finished_requests = []
        finally:
            await self.client_session.close()
            self.client_session = None

        return finished_requests

    async def __send_request(self, url):
        if self.client_session:
            async with self.client_session.get(url) as resp:
                response = await resp.json()
        else:
            async with aiohttp.request('GET', url, json=True) as resp:
                response = await resp.json()
        return response

    @staticmethod
    async def get_response_message(response):
        if isinstance(response, list):
            msg = response[0]['ret_msg']
        else:
            msg = response['ret_msg']

        return msg

    @retry(Exception, total_tries=3)
    async def __make_request(self, method, optional_args=None):

        try:
            url = self.__create_url(method, optional_args)

            response = await self.__send_request(url)
            msg = await self.get_response_message(response)

        except ValueError:
            return error_message("Invalid Input", optional_args)
        except IndexError:
            return error_message("Not Found", optional_args)

        if msg == "Error while comparing Server and Client timestamp":
            raise exceptions.ServerAndClientTimeMismatch("Error with client and server timestamps")
        if msg == 'Exception - Timestamp' or msg == 'Invalid session id.':
            print("Session is invalid, attempting to make a new one, one sec...")
            await self.create_session()
            return await self.__make_request(method, optional_args)

        if msg == "dailylimit (7500 requests reached)/404":
            raise exceptions.RateLimitReached("You have reached the maximum number of requests")

        return response

    async def test_session(self):
        response = await self.__make_request('testsession')
        return response

    async def get_server_status(self):
        server_status = await self.__make_request('gethirezserverstatus')
        return server_status

    async def get_leaderboard(self, queue, tier, season):
        leaderboard = await self.__make_request('getleagueleaderboard', '{}/{}/{}'.format(queue, tier, season))
        return leaderboard

    async def get_seasons(self, queue):
        seasons = await self.__make_request('getleagueseasons', queue)
        return seasons

    async def get_patch_info(self):
        patch_info = await self.__make_request('getpatchinfo')
        return patch_info

    def __generate_signature(self, method):
        signature = hashlib.md5((self.dev_id + method + self.auth_key + util.time_stamp()).encode())
        return signature.hexdigest()

    async def get_live_match_details(self, match_id):
        live_match = await self.__make_request('getmatchplayerdetails', match_id)
        return live_match

    async def get_match_details(self, match_id):
        match_details = await self.__make_request('getmatchdetails', match_id)
        return match_details

    async def get_matches_batch(self, match_ids):
        batch_details = await self.__make_request('getmatchdetailsbatch', match_ids)
        return batch_details

    async def get_matchid_by_queue(self, queue, date, hour):
        match_ids = await self.__make_request('getmatchidsbyqueue', '{}/{}/{}'.format(queue, date, hour))
        return match_ids

    async def pro_matches_details(self):
        esport_details = await self.__make_request('getesportsproleaguedetails')
        return esport_details

    async def get_demo_details(self, match_id):
        demo_details = await self.__make_request('getdemodetails', match_id)
        return demo_details

    async def get_player_status(self, player):
        player_status = self.__make_request('getplayerstatus', player)
        return await player_status

    async def get_player(self, player):
        player_info = await self.__make_request('getplayer', player)
        return player_info

    async def get_queue_stats(self, player_name, queue):
        player = await self.search_player(player_name)

        try:
            player_id = player['player_id']
            queue_stats = await self.__make_request('getqueuestats', '{}/{}'.format(player_id, queue))
            return queue_stats
        except KeyError:
            raise exceptions.NotFound

    async def search_player(self, player):
        """ The searchplayers function returns any players names that contain the 'players' parameter passed in """

        matching_players = await self.__make_request('searchplayers', player)
        print(matching_players)

        if isinstance(matching_players, list):
            for player_object in matching_players:
                if player_object['Name'].lower() == player.lower():
                    return player_object
        else:
            if matching_players['ret_msg'] == 'Not Found':
                raise exceptions.NotFound

        return matching_players

    async def get_player_loadouts(self, player, language='1'):
        player_loadouts = await self.__make_request('getplayerloadouts', '{}/{}'.format(player, language))
        return player_loadouts

    async def get_player_details(self, player):
        player_details = await self.__make_request('getplayer', player)
        return player_details

    async def get_match_history(self, player):
        match_history = await self.__make_request('getmatchhistory', player)
        return match_history

    async def get_champion_ranks(self, player_name):
        champion_ranks = await self.__make_request("getchampionranks", player_name)
        return champion_ranks

    async def get_friends(self, player_name):
        friends = await self.__make_request('getfriends', player_name)
        return friends

    async def get_all_champions(self, language='1'):
        all_champions = await self.__make_request('getchampions', language)
        return all_champions

    async def get_champion_skins(self, champion_id, language='1'):
        all_champion_skins = await self.__make_request('getchampionskins', '{}/{}'.format(champion_id, language))
        return all_champion_skins

    async def get_all_items(self, language='1'):
        items = await self.__make_request('getitems', language)
        return items

    async def check_data_used(self):
        data_usage = await self.__make_request('getdataused')
        return data_usage

    async def get_match_ids_by_hour(self, queue, date, hour, time_format=('00', '10', '20', '30', '40', '50')):
        """ Get all matches for any given hour. All matches are returned using 6 requests in an attempt
            to avoid timing out the connection
        """
        tasks = []
        for interval in time_format:
            tasks.append((self.get_matchid_by_queue(queue, date, '{hr},{min}'.format(hr=hour, min=interval))))

        match_ids = await self.fetch(tasks)

        ids = []
        try:
            ids = [match_id['Match'] for match_id in list(deepflatten(match_ids, ignore=dict))]
        except (KeyError, TypeError):
            print("Match Ids not found")

        return ids

    async def get_matches(self, match_ids):
        """ Get 10 matches at a time to avoid going over data.json limits using the get_matches_batch function
            Args:
                match_ids: type list
        """

        tasks = []
        match_batch = 10
        i = 0
        num_matches = len(match_ids)
        start = time.time()

        while i < num_matches:
            if i + match_batch > num_matches:
                match_batch = num_matches - i

            matches = ','.join(match_ids[i:i+match_batch])
            tasks.append(self.get_matches_batch(matches))
            i += match_batch

        match_data = await self.fetch(tasks)
        print('total time: {}'.format(time.time()-start))
        if match_data:
            match_data = list(deepflatten(match_data, ignore=dict))
        return match_data
