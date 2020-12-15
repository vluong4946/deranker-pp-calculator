import requests

key = 'YOUR KEY HERE'
id = 'YOUR USER ID HERE'
limit = '100'

#def get_beatmap_name(beatmap_id):
#    request = "https://osu.ppy.sh/api/get_beatmaps?" + "k="+key + "&b="+beatmap_id
    #response = requests.get(request).json()
    #return response[0]["artist"] + response[0]["title"]

get_user_best_request = "https://osu.ppy.sh/api/get_user_best?" + "k="+key + "&u="+id + "&limit="+limit
# returns array of scores, each of which is in dict type
get_user_best_response = requests.get(get_user_best_request).json()

# Compute PP from *current* top 100 
curr_top_100_pp = 0
i = 0
for score in get_user_best_response:
    curr_top_100_pp += float(score["pp"]) * 0.95**i
    i += 1
    
# Compute Bonus PP
get_user_request = "https://osu.ppy.sh/api/get_user?" + "k="+key + "&u="+id
get_user_response = requests.get(get_user_request).json()
profile_pp = float(get_user_response[0]["pp_raw"])

bonus_pp = profile_pp - curr_top_100_pp # 379.1

# Compute PP from *experimental* top 100
exp_top_100_pp = 0

deranker_mods = [1, 4096, 4097] # 1 = NF, 4096 = SO, 4097 = 4096^1 = NFSO
deranker_mask = 4097
def mod_weight(mods_id):
    if mods_id == 1:
        return 0.90
    elif mods_id == 4096:
        return 0.95
    elif mods_id == 4097:
        return 0.85

i = 0
for score in get_user_best_response:
    # Recompute PP on scores with NF, SO, or NFSO
    if int(score["enabled_mods"]) & deranker_mask in deranker_mods: 
        mods_id = int(score["enabled_mods"]) & deranker_mask
        exp_score_pp = float(score["pp"]) / mod_weight(mods_id) * 0.95**i
        
        # Print map info (the below 2 lines are too slow)
        #score_map_name = get_beatmap_name(score["beatmap_id"])
        #print(score_map_name + "; Old PP: " + score["pp"] + ", New PP: " + str(round(exp_score_pp, 3)))
        print(score["beatmap_id"] + "; Old PP: " + score["pp"] + ", New PP: " + str(round(exp_score_pp / (0.95**i), 3)))
        
        exp_top_100_pp += exp_score_pp
    else: # Compute normally if without NF, SO, or NFSO
        exp_top_100_pp += float(score["pp"]) * 0.95**i
    i += 1

exp_top_100_pp += bonus_pp

print(exp_top_100_pp)