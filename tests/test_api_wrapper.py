import asynctest
import pytest
import unittest
from paladins_api import api, exceptions


@pytest.mark.usefixtures('api_object')
@pytest.mark.asyncio
class TestAPI(unittest.TestCase):
    async def test_response_is_list(self):
        simple_response = [{'ret_msg': 'done'}, {'ret_msg': 'done'}]
        resp = await self.paly.get_response_message(simple_response)
        self.assertIsInstance(resp, str)

    async def test_get_matches_given_empty_list(self):
        self.self.paly.fetch = asynctest.CoroutineMock(return_value=[])
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
