import pytest
import asynctest
import json
from unittest.mock import MagicMock, patch
from ..api_wrapper.api import PaladinApi
from ..api_wrapper import exceptions
from ..players.player import MatchPlayer


@pytest.fixture(scope='class')
def api_object(request):
    class ApiObject:
        pass

    request.cls.paly = PaladinApi()
    with open('tests/data.json') as file:
        temp_data = json.load(file)

    request.cls.player = MatchPlayer(temp_data)


@pytest.mark.asyncio
@pytest.mark.usefixtures('api_object')
class BaseTestClass(asynctest.TestCase):
    pass


class TestAPI(BaseTestClass):

    async def test_make_request_non_list_response(self):
        simple_response = {'ret_msg': 'done'}
        resp = await self.paly.get_response_message(simple_response)
        self.assertIsInstance(resp, str)

    async def test_response_is_list(self):
        simple_response = [{'ret_msg': 'done'}, {'ret_msg': 'done'}]
        resp = await self.paly.get_response_message(simple_response)
        self.assertIsInstance(resp, str)

    async def test_get_matches_given_empty_list(self):
        self.paly.fetch = asynctest.CoroutineMock(return_value=[])
        empty_list = await self.paly.get_matches([])
        self.assertEqual(empty_list, [])

    async def test_get_match_ids_by_hour_given_empty_list(self):
        self.paly.fetch = asynctest.CoroutineMock(return_value=[])
        no_ids_found = await self.paly.get_match_ids_by_hour(1, 1, 1)
        self.assertEqual(no_ids_found, [])

    async def test_get_match_ids_by_hour_ids_not_found(self):
        self.paly.fetch = asynctest.CoroutineMock(return_value={'ret_msg': 'not_found'})
        ids = await self.paly.get_match_ids_by_hour(486, 202020101, 10)
        self.assertEqual(ids, [])

    async def test_search_player_multiple_players_returned(self):
        self.paly._PaladinApi__make_request = asynctest.CoroutineMock(return_value=[{'ret_msg': 'found', 'Name': 'bob'},
                                                                                  {'ret_msg': 'not found', 'Name': ''}])
        player = await self.paly.search_player('bob')
        self.assertEqual(player['Name'], 'bob')

    async def test_search_player_not_found(self):
        self.paly._PaladinApi__make_request = asynctest.CoroutineMock(return_value={'ret_msg': 'Not Found'})
        player = self.paly.search_player('bob')
        self.assertAsyncRaises(exceptions.NotFound, player)

    async def test_get_queue_stats_too_many_players(self):
        self.paly._PaladinApi__make_request = asynctest.CoroutineMock(return_value=[{'win': 10, 'games': 10},
                                                                                    {'name': 'bob'}])
        player = self.paly.get_queue_stats('bob', 420)
        self.assertAsyncRaises(exceptions.NotFound, player)


class TestMatchPlayer(BaseTestClass):
    def test_get_match_scores(self):
        self.assertEqual([(1, 4), (2, 0)], self.player.get_match_score())

    def test_get_team_score(self):
        self.assertEqual(4, self.player.get_team_score(1))

    def test_get_loadout_returns_five_items(self):
        self.assertEqual(5, len(self.player.get_loadout()))

    def test_get_number_of_bans(self):
        self.assertEqual(4, len(self.player.get_bans()))

    def test_number_of_items(self):
        self.assertEqual(2, len(self.player.get_items_purchased()))

    def test_match_items_less_than_four(self):
        player = MatchPlayer({'Item_Active_1': 'bob', 'Item_Active_2': 'tom', 'Item_Active_3': 'pam',
                              'Item_Active_4': ''})

        items_bought = player.get_items_purchased()
        self.assertEqual(3, len(items_bought))

    def test_missing_champion_bans(self):
        player = MatchPlayer({'Ban_1': 'bob', 'Ban_2': 'tom', 'Ban_3': 'other bob', 'Ban_4': ''})
        bans = player.get_bans()
        self.assertEqual(3, len(bans))

    def test_get_timestamp(self):
        tstamp = "12/10/2020 10:00:01 AM"
        self.assertEquals(tstamp, self.player.get_time_stamp())
