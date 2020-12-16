import pytest
import asynctest
from unittest.mock import MagicMock
from api_wrapper.api import PaladinApi


@pytest.fixture(scope='class')
def api_object(request):
    class ApiObject:
        pass

    request.cls.paly = PaladinApi()


@pytest.mark.asyncio
@pytest.mark.usefixtures('api_object')
class TestAPI(asynctest.TestCase):

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
