import requests 
import hashlib
from datetime import *
import time 
import config
import json

class PaladinAPI:
    
    def __init__(self, id, key):
        self.dev_id = id 
        self.auth_key = key 
        self.paladins_endpoint = "http://api.paladins.com/paladinsapi.svc/"
    
    def create_session(self):
        success = requests.get(self.paladins_endpoint+"createsessionJson"+"/"+self.dev_id+"/"+self.generate_signature("createsession")+"/"+self.get_utc_time())
        return success.json()

    def get_utc_time(self):
        current_time = datetime.utcnow()

        # utc time formatted to YYYYmmddhhmmss
        utc_time = current_time.strftime("%Y%m%d%I%M%S")

        return utc_time
   
    def generate_signature(self, method):
       signature = hashlib.md5((self.dev_id+method+self.auth_key+self.get_utc_time()).encode())

       return signature.hexdigest()

    def test_session(self, session_id):
        valid_id = requests.get(self.paladins_endpoint+"testsessionJson/"+self.dev_id+'/'+self.generate_signature("testsession")+'/'+session_id+'/'+self.get_utc_time())
        return valid_id.json()

    def get_server_status(self, session_id):
        server_status = requests.get(self.paladins_endpoint+"gethirezserverstatusJson"+'/'+self.dev_id+'/'+self.generate_signature("gethirezserverstatus")+'/'+session_id+'/'+self.get_utc_time())
        return server_status.json()

    def check_data_used(self, session_id):
        data_usage = requests.get(self.paladins_endpoint+"getdatausedJson/"+self.dev_id+'/'+self.generate_signature("getdataused")+'/'+session_id+'/'+self.get_utc_time())
        return data_usage.json()

    def get_demo_details(self, session_id, match_id):
        demo_details = requests.get(self.paladins_endpoint+"getdemodetailsJson/"+self.dev_id+'/'+self.generate_signature("getdemodetails")+'/'+session_id+'/'+self.get_utc_time()+'/'+match_id)
        return demo_details.json()

    def pro_matches_details(self, session_id):
        esport_details = requests.get(self.paladins_endpoint+"getesportsproleaguedetailsJson/"+self.dev_id+'/'+self.generate_signature("getesportsproleaguedetails")+'/'+session_id+'/'+self.get_utc_time())
        return esport_details.json()

    def get_friends(self, session_id, player_name):
        friends = requests.get(self.paladins_endpoint+"getfriendsJson/"+self.dev_id+'/'+self.generate_signature("getfriends")+'/'+session_id+'/'+self.get_utc_time()+'/'+player_name) 
        return friends.json()

    def get_champion_ranks(self, session_id, player_name):
         champion_ranks = requests.get(self.paladins_endpoint+"getchampionranksJson/"+self.dev_id+'/'+self.generate_signature("getchampionranks")+'/'+session_id+'/'+self.get_utc_time()+'/'+player_name)
         return champion_ranks.json()
    
    def get_all_champions(self, session_id, language='1'):
        all_champions = requests.get(self.paladins_endpoint+"getchampionsJson/"+self.dev_id+'/'+self.generate_signature("getchampions")+'/'+session_id+'/'+self.get_utc_time()+'/'+language)
        return all_champions.json()

    def get_champion_skins(self, session_id, champion_id, language='1'):
        all_champion_skins = requests.get(self.paladins_endpoint+"getchampionskinsJson/"+self.dev_id+'/'+self.generate_signature("getchampionskins")+'/'+session_id+'/'+self.get_utc_time()+'/'+champion_id+'/'+language)
        return all_champion_skins.json()

    def get_all_items(self, session_id, language='1'):
        items = requests.get(self.paladins_endpoint+"getitemsJson/"+self.dev_id+'/'+self.generate_signature("getitems")+'/'+session_id+'/'+self.get_utc_time()+'/'+language)
        return items.json()

    def get_match_details(self, session_id, match_id):
        match_details = requests.get(self.paladins_endpoint+"getmatchdetailsJson/"+self.dev_id+'/'+self.generate_signature("getmatchdetails")+'/'+session_id+'/'+self.get_utc_time()+'/'+match_id)
        return match_details.json()

    def get_matches_batch(self, session_id, match_ids):
        batch_details = requests.get(self.paladins_endpoint+"getmatchdetailsbatchJson/"+self.dev_id+'/'+self.generate_signature("getmatchdetailsbatch")+'/'+session_id+'/'+self.get_utc_time()+'/'+match_ids)
        return batch_details.json()

    def get_matchid_by_queue(self, session_id, queue, date, hour):
        match_ids = requests.get(self.paladins_endpoint+"getmatchidsbyqueueJson/"+self.dev_id+'/'+self.generate_signature("getmatchidsbyqueue")+'/'+session_id+'/'+self.get_utc_time()+'/'+queue+'/'+date+'/'+hour)
        return match_ids.json()

    def get_leaderboard(self, session_id, queue, tier, season):
        leaderboard = requests.get(self.paladins_endpoint+"getleagueleaderboardJson/"+self.dev_id+'/'+self.generate_signature("getleagueleaderboard")+'/'+session_id+'/'+self.get_utc_time()+'/'+queue+'/'+tier+'/'+season)
        return leaderboard.json()

    def get_seasons(self, session_id, queue):
        seasons = requests.get(self.paladins_endpoint+"getleagueseasonsJson/"+self.dev_id+'/'+self.generate_signature("getleagueseasons")+'/'+session_id+'/'+self.get_utc_time()+'/'+queue)
        return seasons.json()

    def get_match_history(self, session_id, player):
        match_history = requests.get(self.paladins_endpoint+"getmatchhistoryJson/"+self.dev_id+'/'+self.generate_signature("getmatchhistory")+'/'+session_id+'/'+self.get_utc_time()+'/'+player)
        return match_history.json()

    def get_player_details(self, session_id, player):
        player_details = requests.get(self.paladins_endpoint+"getplayerJson/"+self.dev_id+'/'+self.generate_signature("getplayer")+'/'+session_id+'/'+self.get_utc_time()+'/'+player)
        return player_details.json()

    def get_player_loadouts(self, session_id, player, language='1'):
        player_loadouts = requests.get(self.paladins_endpoint+"getplayerloadoutsJson/"+self.dev_id+'/'+self.generate_signature("getplayerloadouts")+'/'+session_id+'/'+self.get_utc_time()+'/'+player+'/'+language)
        return player_loadouts.json()

    def get_player_status(self, session_id, player):
        player_status = requests.get(self.paladins_endpoint+"getplayerstatusJson/"+self.dev_id+'/'+self.generate_signature("getplayerstatus")+'/'+session_id+'/'+self.get_utc_time()+'/'+player)
        return player_status.json()

    def get_queue_stats(self, session_id, player, queue):
        queue_stats = requests.get(self.paladins_endpoint+"getqueuestatsJson/"+self.dev_id+'/'+self.generate_signature("getqueuestats")+'/'+session_id+'/'+self.get_utc_time()+'/'+player+'/'+queue)
        return queue_stats.json()

    def get_patch_info(self, session_id):
        patch_info = requests.get(self.paladins_endpoint+"getpatchinfoJson/"+self.dev_id+'/'+self.generate_signature("getpatchinfo")+'/'+session_id+'/'+self.get_utc_time())
        return patch_info.json()

def print_json(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)