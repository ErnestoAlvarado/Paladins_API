from player import MatchPlayer
import champion_roles


class Match:
    """" This class will serve the purpose of managing the data involved in a Paladins match """

    def __init__(self, match_data):
        # match data is a list of dictionaries where each dictionary corresponds to
        # a player in that match
        self.match_players = []
        self.champions_used = []

        for player_data in match_data:
            player = MatchPlayer(player_data)
            self.match_players.append(player)
            self.champions_used.append(player.get_champion_name())

    def get_champions_picked(self):
        champions_used = []
        for player in self.match_players:
            champions_used.append(player.get_champion_name())

        return champions_used

    def get_team_comp(self):
        team_comp = []
        for champ in self.champions_used:
            team_comp.append(champion_roles.CHAMPIONS[champ])

        team_comp.sort()
        return tuple(team_comp)

    def get_champions(self):
        return self.champions_used
