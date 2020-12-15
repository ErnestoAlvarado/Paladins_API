import pytest
import unittest
from unittest.mock import MagicMock
from api_wrapper.api import PaladinApi
import aiounittest
import asyncio

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='class')
def api_object(request):
    class ApiObject:
        pass

    request.cls.paly = PaladinApi()


@pytest.mark.asyncio
@pytest.mark.usefixtures('api_object')
class TestAPI:

    async def test_make_request_non_list_response(self):
        simple_response = {'ret_msg': 'done'}
        resp = await self.paly.get_response_message(simple_response)
        assert isinstance(resp, str)

    async def test_response_is_list(self):
        simple_response = [{'ret_msg': 'done'}, {'ret_msg': 'done'}]
        resp = await self.paly.get_response_message(simple_response)
        assert isinstance(resp, str)

    async def test_get_matches_empty_list(self):
        assert await self.paly.get_matches([]) == []

    async def test_get_ids_empty_list(self):
        assert await self.paly.get_match_ids_by_hour(1, 1, 1) == []
