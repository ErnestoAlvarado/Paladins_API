import pytest
import unittest
from paladins_api import player


@pytest.mark.usefixtures('match_player_object')
class TestMatchPlayer(unittest.TestCase):
    def test_get_match_scores(self):
        self.assertEqual([(1, 4), (2, 0)], self.match_player.get_match_score())

    def test_get_team_score(self):
        self.assertEqual(4, self.match_player.get_team_score(1))

    def test_get_loadout_returns_five_items(self):
        self.assertEqual(5, len(self.match_player.get_loadout()))

    def test_get_number_of_bans(self):
        self.assertEqual(4, len(self.match_player.get_bans()))

    def test_number_of_items(self):
        self.assertEqual(2, len(self.match_player.get_items_purchased()))

    def test_match_items_less_than_four(self):
        players = player.MatchPlayer({'Item_Active_1': 'bob', 'Item_Active_2': 'tom', 'Item_Active_3': 'pam',
                                                 'Item_Active_4': ''})

        items_bought = players.get_items_purchased()
        self.assertEqual(3, len(items_bought))

    def test_missing_champion_bans(self):
        players = player.MatchPlayer({'Ban_1': 'bob', 'Ban_2': 'tom', 'Ban_3': 'other bob', 'Ban_4': ''})
        bans = players.get_bans()
        self.assertEqual(3, len(bans))

    def test_get_timestamp(self):
        tstamp = "12/10/2020 10:00:01 AM"
        self.assertEqual(tstamp, self.match_player.get_time_stamp())
