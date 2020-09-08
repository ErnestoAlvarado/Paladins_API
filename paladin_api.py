from paladin_stats.paladin_wrapper.api_base import BaseApi
from iteration_utilities import deepflatten
import asyncio
import aiohttp
import time


class PaladinAPI(BaseApi):

    def get_live_match_details(self, match_id):
        live_match = self._make_request('getmatchplayerdetails', match_id)
        return live_match

    def get_match_details(self, match_id):
        match_details = self._make_request('getmatchdetails', match_id)
        return match_details

    def get_matches_batch(self, match_ids):
        batch_details = self._make_request('getmatchdetailsbatch', match_ids)
        return batch_details

    async def get_matchid_by_queue(self, queue, date, hour):
        match_ids = self._make_request('getmatchidsbyqueue', '{}/{}/{}'.format(queue, date, hour))
        return await match_ids

    def pro_matches_details(self):
        esport_details = self._make_request('getesportsproleaguedetails')
        return esport_details

    def get_demo_details(self, match_id):
        demo_details = self._make_request('getdemodetails', match_id)
        return demo_details

    async def get_player_status(self, player):
        player_status = await self._make_request('getplayerstatus', player)
        return player_status

    async def get_player(self, player):
        player_info = await self._make_request('getplayer', player)
        return player_info

    def get_queue_stats(self, player_name, queue):
        player_list = self.search_player(player_name)

        if len(player_list) == 1:
            print(player_list)
            player_id = player_list[0]['player_id']
            queue_stats = self._make_request('getqueuestats', '{}/{}'.format(player_id, queue))
            return queue_stats
        else:
            return "Not Found"

    def search_player(self, player):
        """ The searchplayers function returns any players names that contain the 'player' parameter passed in """

        matching_players = self._make_request('searchplayers', player)
        print(matching_players)
        if matching_players['ret_msg'] == "Not Found":
            return "Not Found"

        for player_name in matching_players:
            if player_name['Name'].lower() == player.lower():
                return [player_name]
        return matching_players

    def get_player_loadouts(self, player, language='1'):
        player_loadouts = self._make_request('getplayerloadouts', '{}/{}'.format(player, language))
        return player_loadouts

    def get_player_details(self, player):
        player_details = self._make_request('getplayer', player)
        return player_details

    def get_match_history(self, player):
        match_history = self._make_request('getmatchhistory', player)
        return match_history

    def get_champion_ranks(self, player_name):
        champion_ranks = self._make_request("getchampionranks", player_name)
        return champion_ranks

    def get_friends(self, player_name):
        friends = self._make_request('getfriends', player_name)
        return friends

    def get_all_champions(self, language='1'):
        all_champions = self._make_request('getchampions', language)
        return all_champions

    def get_champion_skins(self, champion_id, language='1'):
        all_champion_skins = self._make_request('getchampionskins', '{}/{}'.format(champion_id, language))
        return all_champion_skins

    def get_all_items(self, language='1'):
        items = self._make_request('getitems', language)
        return items

    def check_data_used(self, session, lock):
        data_usage = self._make_request(session, lock, 'getdataused')
        return data_usage

    async def get_match_ids_by_hour(self, queue, date, hour, time_format=('00', '10', '20', '30', '40', '50')):
        """ Get all matches for any given hour. All matches are returned using 6 requests in an attempt
            to avoid timing out the connection
        """
        tasks = []

        for interval in time_format:
            tasks.append((self.get_matchid_by_queue(queue, date, '{hr},{min}'.format(hr=hour, min=interval))))

        match_ids = await self.fetch(tasks)

        print("Done with hour: {}".format(hour))

        ids = []
        try:
            ids = [match_id['Match'] for match_id in list(deepflatten(match_ids, ignore=dict))]
        except KeyError:
            print("Match Ids not found")

        return ids

    async def get_matches(self, match_ids):
        """ Get 10 matches at a time to avoid going over data limits using the get_matches_batch function"""
        tasks = []
        match_batch = 10
        i = 0
        num_matches = len(match_ids)

        while i < num_matches:
            if i + match_batch > num_matches:
                match_batch = num_matches - i

            matches = ','.join(match_ids[i:i+match_batch])
            tasks.append(self.get_matches_batch(matches))
            i += match_batch

        match_data = await self.fetch(tasks)
        return list(deepflatten(match_data, ignore=dict))
