import pytest
from unittest.mock import MagicMock
from api_wrapper.api import PaladinApi
import aiounittest
import asyncio


@pytest.mark.asyncio
async def test_make_request_non_list_response():
    paly = PaladinApi()
    simple_response = {'ret_msg': 'done'}
    resp = await paly.get_response_message(simple_response)
    assert isinstance(resp, str)


@pytest.mark.asyncio
async def test_response_is_list():
    paly = PaladinApi()
    simple_response = [{'ret_msg': 'done'}, {'ret_msg': 'done'}]
    resp = await paly.get_response_message(simple_response)
    assert isinstance(resp, str)
