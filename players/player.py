
class MatchPlayer:
    """" Acts as an interface for players data.json pulled from a match
    """
    def __init__(self, match_data):
        self.match_data = match_data

    def get_account_level(self):
        return self.match_data['Account_Level']

    def get_assists(self):
        return self.match_data['Assists']

    def get_bans(self):
        bans = []

        for i in range(1, 5):
            if self.match_data['Ban_{}'.format(i)]:
                bans.append(self.match_data['Ban_{}'.format(i)])

        return bans

    def get_champion_id(self):
        return self.match_data['ChampionId']

    def get_damage_done_physical(self):
        return self.match_data['Damage_Done_Physical']

    def get_damage_done_in_hand(self):
        return self.match_data['Damage_Done_In_Hand']

    def get_damage_done(self):
        return self.match_data['Damage_Player']

    def get_damage_taken(self):
        return self.match_data['Damage_Taken']

    def get_deaths(self):
        return self.match_data['Deaths']

    def get_kda(self):
        return self.match_data['Kills_Player'] + self.match_data['Assists'] / self.match_data['Deaths']

    def get_gold_earned(self):
        return self.match_data['Gold_Earned']

    def get_gold_earned_per_minute(self):
        return self.match_data['Gold_Per_Minute']

    def get_healing(self):
        return self.match_data['Healing']

    def get_self_heal(self):
        return self.match_data['Healing_Player_Self']

    def get_loadout(self):
        loadout = []

        for i in range(1, 6):
            if self.match_data['Item_Purch_{}'.format(i)]:
                (card, level) = self.match_data['Item_Purch_{}'.format(i)], self.match_data['ItemLevel{}'.format(i)]
                loadout.append((card, level))

        return loadout

    def get_talent(self):
        return self.match_data['Item_Purch_6']

    def get_items_purchased(self):
        items_bought = []

        for i in range(1, 5):

            if self.match_data['Item_Active_{}'.format(i)]:
                items_bought.append(self.match_data['Item_Active_{}'.format(i)])

        return items_bought

    def get_kill_streak(self):
        return self.match_data['Killing_Spree']

    def get_kills(self):
        return self.match_data['Kills_Player']

    def get_league_losses(self):
        return self.match_data['League_Losses']

    def get_ranked_points(self):
        return self.match_data['League_Points']

    def get_current_rank(self):
        return self.match_data['League_Tier']

    def get_league_wins(self):
        return self.match_data['League_wins']

    def get_map(self):
        return self.match_data['Map_Game']

    def match_id(self):
        return self.match_data['Match']

    def get_match_duration_in_seconds(self):
        return self.match_data['Time_In_Match_Seconds']

    def get_match_duration_in_minutes(self):
        return self.match_data['Minutes']

    def get_objective_assists(self):
        return self.match_data['Objective_Assists']

    def get_party_id(self):
        return self.match_data['PartyId']

    def get_platform(self):
        return self.match_data['Platform']

    def get_champion_name(self):
        return self.match_data['Reference_Name']

    def get_region(self):
        return self.match_data['Region']

    def get_skin(self):
        return self.match_data['Skin']

    def get_skin_id(self):
        return self.match_data['SkinId']

    def get_team(self):
        return self.match_data['TaskForce']

    def get_team_score(self, team_id=None):
        if not team_id:
            team_id = self.match_data['TaskForce']

        return self.match_data['Team{}Score'.format(team_id)]

    def get_match_score(self):
        return [(team_id, self.get_team_score(team_id)) for team_id in range(1, 3)]

    def get_win_status(self):
        return self.match_data['Win_Status']

    def get_queue_id(self):
        return self.match_data['match_queue_id']

    def get_game_mode(self):
        return self.match_data['name']

    def get_player_name(self):
        return self.match_data['playerName']

    def get_time_stamp(self):
        return self.match_data['Entry_Datetime']
