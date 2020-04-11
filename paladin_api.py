from api_base import BaseApi
import util
from player import MatchPlayer


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

    def get_matchid_by_queue(self, queue, date, hour):
        match_ids = self._make_request('getmatchidsbyqueue', '{}/{}/{}'.format(queue, date, hour))
        return match_ids

    def pro_matches_details(self):
        esport_details = self._make_request('getesportsproleaguedetails')
        return esport_details

    def get_demo_details(self, match_id):
        demo_details = self._make_request('getdemodetails', match_id)
        return demo_details

    def get_player_status(self, player):
        player_status = self._make_request('getplayerstatus', player)
        return player_status

    def get_player(self, player):
        player_info = self._make_request('getplayer', player)
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

    def get_match_ids_by_hour(self, queue, date, hour, time_format=('00', '10', '20', '30', '40', '50')):
        match_ids = []

        """ Get all matches for any given hour. All matches are returned using 6 requests in an attempt
            to avoid timing out the connection 
        """
        for interval in time_format:
            match_ids += self.get_matchid_by_queue(queue, date, '{hr},{min}'.format(hr=hour, min=interval))

        return match_ids

    def get_matches_for_one_hour(self, match_ids):
        """ Get 10 matches at a time to avoid going over data limits using the get_matches_batch function"""
        num_of_matches = len(match_ids)
        match_batch_ids = ''
        match_counter = 0
        match_batch = 10
        matches = []

        for match_id in match_ids:

            if match_batch > num_of_matches:
                match_batch = num_of_matches

            match_counter += 1
            current_id = match_id['Match']

            if match_batch - match_counter > 0:
                current_id += ','

            match_batch_ids += current_id
            print('Ids: ', match_batch_ids)

            if match_counter == match_batch:
                matches += self.get_matches_batch(match_batch_ids)
                num_of_matches -= match_counter
                match_batch_ids = ''
                print("Remaining matches: ", num_of_matches)
                match_counter = 0

        return matches


def main():
    ans = ''
    paly = PaladinAPI()
    while ans != 'done':
        print("1:create session")
        print("2:get player status")
        print("3:get all champions")
        print("4:test session")
        print("5:get_friends")
        print("6:get match history")
        print("7:pro match details")
        print("8:get player details")
        print("9:get server status")
        print("10:data used")
        print("11:ping")
        print("12: get all items")
        print("13: get champion skins")
        print("14: get demo details ")
        print("15: get match details")
        print("16: get matches batch")
        print("17: get match ids by queue")
        print("18: get queue stats")
        print("19: player load-outs")
        print("20: Get all match ids for any given hour, queue, and date")
        print("21: Enter a player name to search for player with similar name")
        print("22: Enter player name to get live match data ")
        print("23: Get more info on a particular player")
        print("24: Get all matches for any given hour")

        ans = input("Make a choice\n")

        if ans == '1':
            paly.create_session()
        elif ans == '2':
            util.print_json(paly.get_player_status(input("Enter player name\n")))
        elif ans == '3':
            util.print_json(paly.get_all_champions())
        elif ans == '4':
            util.print_json(paly.test_session())
        elif ans == '5':
            util.print_json(paly.get_friends(input("Enter player name\n")))
        elif ans == '6':
            util.print_json(paly.get_match_history(input("Enter player name\n")))
        elif ans == '7':
            util.print_json(paly.pro_matches_details())
        elif ans == '8':
            util.print_json(paly.get_player_details(input("Enter player name\n")))
        elif ans == '9':
            util.print_json(paly.get_server_status())
        elif ans == '10':
            util.print_json(paly.check_data_used())
        elif ans == '11':
            util.print_json(paly.ping())
        elif ans == '12':
            util.print_json(paly.get_all_items())
        elif ans == '13':
            util.print_json(paly.get_champion_skins(input("Enter champion id\n")))
        elif ans == '14':
            util.print_json(paly.get_demo_details(input("Enter match id\n")))
        elif ans == '15':
            match_id = input("Enter match id\n")
            util.print_json(paly.get_match_details(match_id))
            match_player = MatchPlayer(paly.get_match_details(match_id)[0])
            print("Here are the items purchased: ", match_player.get_items_purchased())
            print("Here is the loadout used: ", match_player.get_loadout())
            #print("Here is a kda", match_player.get_kda())

        elif ans == '16':
            util.print_json(paly.get_matches_batch(input("Enter match ids separated by commas\n")))
        elif ans == '17':
            util.print_json(paly.get_matchid_by_queue(input("Enter queue\n"), input("Enter date\n"), input("Enter hour\n")))
        elif ans == '18':
            util.print_json(paly.get_queue_stats(input("Enter player name\n"), input("Enter queue\n")))
        elif ans == '19':
            util.print_json(paly.get_player_loadouts(input("Enter player name\n")))
        elif ans == '20':
            util.print_json(paly.get_match_ids_by_hour(input("Enter queue"), input("Enter date"), input("Enter hour")))
        elif ans == '21':
            util.print_json(paly.search_player(input("Enter a player name")))
        elif ans == '22':
            util.print_json(paly.get_live_match_details(input("Enter live match id")))
        elif ans == '23':
            util.print_json(paly.get_player(input("Enter player name")))
        elif ans == '24':
            match_ids = paly.get_match_ids_by_hour(input("Enter queue"), input("Enter date in yyyymmdd format"),
                                                       input("Enter the hour"))
            util.print_json(paly.get_matches_for_one_hour(match_ids))
        print("\n")


main()