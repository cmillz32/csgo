import pandas as pd
import numpy as np
import math
import re

df = pd.read_csv('data/full_data_clean.csv')

dict = {'player': [], 'kills': [], 'deaths': [],
                      'adr': [], 'kast': [], 'rating': [], 'team_on': [], 'team_against': [], 'map': []}

for team in range(1, 3):
    team_on_string = 'team_' + str(team)
    if team == 1:
        team_against_string = 'team_' + str(team + 1)
    else:
        team_against_string = 'team_' + str(team - 1)
    teams_on = df[team_on_string]
    teams_against = df[team_against_string]

    for map in range(1, 4):
        map_string = 'map_' + str(map)
        maps = df[map_string]

        for play in range(1, 6):
            # PLAYER
            player_string = 'team_' + \
                str(team) + '_map_' + str(map) + '_player_' + str(play)
            players = list(df[player_string].values)
            dict['player'].extend(
                player for player in players if player == player)
            # KD
            kd_string = player_string + "_kd"
            kds = list(df[kd_string].values)
            kills = []
            deaths = []
            nan_indices = []
            for l in range(len(kds)):
                if kds[l] == kds[l]:
                    [k, d] = re.findall(r'\d+', kds[l])
                    kills.append(k)
                    deaths.append(d)
                else:
                    nan_indices.append(l)
            dict['kills'].extend(kills)
            dict['deaths'].extend(deaths)
            # ADR
            adr_string = player_string + "_adr"
            adrs = list(df[adr_string].values)
            dict['adr'].extend(
                adr for adr in adrs if adr == adr)
            # KAST
            kast_string = player_string + "_kast"
            kasts = list(df[kast_string].values)
            dict['kast'].extend(
                kast for kast in kasts if kast == kast)
            # RATING
            rating_string = player_string + "_rating"
            ratings = list(df[rating_string].values)
            dict['rating'].extend(
                rating for rating in ratings if rating == rating)
            # TEAM_ON
            dict['team_on'].extend(
                teams_on[t] for t in range(len(teams_on)) if t not in nan_indices)
            # TEAM_ON
            dict['team_against'].extend(
                teams_against[t] for t in range(len(teams_against)) if t not in nan_indices)
            # MAP
            dict['map'].extend(
                map for map in maps if map == map)

print(len(dict['player']), len(dict['kills']), len(dict['deaths']), len(dict['adr']), len(
    dict['kast']), len(dict['rating']), len(dict['team_on']), len(dict['team_against']), len(dict['map']))

df_new = pd.DataFrame.from_dict(dict)
df_new.to_csv('data/player_data.csv', index=False)
