import json
import pytest
from paladins_api import api, player


@pytest.fixture(scope='class')
def api_object(request):
    class Api:
        pass
    request.cls.paly = api.PaladinApi()


@pytest.fixture(scope='class')
def match_player_object(request):

    class Match:
        pass
    with open('tests/data.json') as file:
        temp_data = json.load(file)

    request.cls.match_player = player.MatchPlayer(temp_data)
