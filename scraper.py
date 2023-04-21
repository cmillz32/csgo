from bs4 import BeautifulSoup
import requests
import json
import pandas as pd


def get_match_links(low, high):
    links = []
    for i in range(low, high):
        if i == 0:
            url = "https://www.hltv.org/results?startDate=all"
        else:
            url = "https://www.hltv.org/results?offset=" + \
                str(100*i) + "&startDate=all"
        page = requests.get(url).content

        big_soup = BeautifulSoup(page, 'html.parser')
        urls = big_soup.find_all('a', {'class': "a-reset"})
        urls_text = []
        for url in urls:
            url_text = url.get('href')
            if not url_text.startswith("/matches/"):
                break
            urls_text.append(url_text)
        maps = big_soup.find_all('div', {'class': "map-text"})
        for i in range(len(urls_text)):
            if maps[i].text == 'bo3':
                links.append(urls_text[i])

    return links


def scrape_it():
    links = get_match_links(8, 9)
    frames = []
    for link in links[1:]:
        url = "https://www.hltv.org" + link
        print(url)
        while True:
            page = requests.get(
                url='https://proxy.scrapeops.io/v1/',
                params={
                    'api_key': 'ffeab0c2-6e63-44b1-b8d4-0e6b585fdd40',
                    'url': url,
                },
            ).content
            soup = BeautifulSoup(page, 'html.parser')
            if soup is not None:
                break
        match = {}
        # get date
        try:
            date = soup.find('div', {'class': 'date'}).text
            time = soup.find('div', {'class': 'time'}).text
        except AttributeError:
            date = 0
            time = 0
        id = link[9:16]
        date_time = str(date) + ' ' + str(time) + ' ' + str(id)
        # get maps
        map_menu = soup.findAll('div', {'class': 'stats-menu-link'})[1:]
        maps = []
        for map in map_menu:
            if map.text[1:5] == 'nuke':
                maps.append(map.text.replace('\n', '')[4:])
            else:
                maps.append(map.text.replace('\n', '')[3:])
        # get team data
        safety_stop = 30
        for i in range(safety_stop):
            team_list = soup.findAll('div', {'class': 'teamName'})
            if len(team_list) > 0:
                break
        try:
            team1_name = team_list[0].text
            team2_name = team_list[1].text
        except IndexError:
            team1_name = "unknown"
            team2_name = "unknown"
        results = soup.findAll(
            'div', {'class': 'results played'})
        winners = []
        picks = []
        for result in results:
            if result.find('div', {'class': 'results-left won'}) is not None:
                winners.append(team1_name)
                picks.append(team2_name)
            elif result.find('div', {'class': 'results-left lost'}) is not None:
                winners.append(team2_name)
                picks.append(team2_name)
            elif result.find('div', {'class': 'results-left won pick'}) is not None:
                winners.append(team1_name)
                picks.append(team1_name)
            elif result.find('div', {'class': 'results-left lost pick'}) is not None:
                winners.append(team2_name)
                picks.append(team1_name)

        # get players for teams
        team_stats = soup.findAll(
            'table', {'class': 'table totalstats'})[2:]
        players = []
        curr_map = 0
        line = {}
        for i in range(0, len(team_stats), 2):
            teams = {}
            team_stats_by_map = team_stats[i: (i+1)+1]
            team_players = []
            for team_stat in team_stats_by_map:
                players = team_stat.findAll(
                    'span', {'class': 'player-nick'})
                kd = team_stat.findAll(
                    'td', {'class': 'kd text-center'})[1:]
                adr = team_stat.findAll(
                    'td', {'class': 'adr text-center'})[1:]
                kast = team_stat.findAll(
                    'td', {'class': 'kast text-center'})[1:]
                rating = team_stat.findAll(
                    'td', {'class': 'rating text-center'})[1:]
                player_list = []
                for j in range(len(players)):
                    player_list.append(
                        {'player': players[j].text, 'kd': kd[j].text, 'adr': adr[j].text, 'kast': kast[j].text, 'rating': rating[j].text})
                team_players.append(player_list)
            teams[team1_name] = {'players': team_players[0]}
            teams[team2_name] = {'players': team_players[1]}
            match[maps[curr_map]] = {
                'teams': teams, 'winner': winners[curr_map], 'pick': picks[curr_map]}
            curr_map += 1
        line = {'id': [date_time], 'team_1': [
            team1_name], 'team_2': [team2_name]}
        for i in range(len(maps)):
            map_string = 'map_' + str(i + 1)
            line[map_string] = maps[i]
            for j in range(2):
                for k in range(5):
                    player_string = 'team_' + \
                        str(j + 1) + '_map_' + str(i + 1) + \
                        '_player_' + str(k + 1)
                    kd_string = 'team_' + \
                        str(j + 1) + '_map_' + str(i + 1) + \
                        '_player_' + str(k + 1) + '_kd'
                    adr_string = 'team_' + \
                        str(j + 1) + '_map_' + str(i + 1) + \
                        '_player_' + str(k + 1) + '_adr'
                    kast_string = 'team_' + \
                        str(j + 1) + '_map_' + str(i + 1) + \
                        '_player_' + str(k + 1) + '_kast'
                    rating_string = 'team_' + \
                        str(j + 1) + '_map_' + str(i + 1) + \
                        '_player_' + str(k + 1) + '_rating'

                    if j == 0:
                        line[player_string] = [match[maps[i]
                                                     ]['teams'][team1_name]['players'][k]['player']]
                        line[kd_string] = [match[maps[i]
                                                 ]['teams'][team1_name]['players'][k]['kd']]
                        line[adr_string] = [match[maps[i]
                                                  ]['teams'][team1_name]['players'][k]['adr']]
                        line[kast_string] = [match[maps[i]
                                                   ]['teams'][team1_name]['players'][k]['kast']]
                        line[rating_string] = [match[maps[i]
                                                     ]['teams'][team1_name]['players'][k]['rating']]
                    elif j == 1:
                        line[player_string] = [match[maps[i]
                                                     ]['teams'][team2_name]['players'][k]['player']]
                        line[kd_string] = [match[maps[i]
                                                 ]['teams'][team2_name]['players'][k]['kd']]
                        line[adr_string] = [match[maps[i]
                                                  ]['teams'][team2_name]['players'][k]['adr']]
                        line[kast_string] = [match[maps[i]
                                                   ]['teams'][team2_name]['players'][k]['kast']]
                        line[rating_string] = [match[maps[i]
                                                     ]['teams'][team2_name]['players'][k]['rating']]

        frames.append(pd.DataFrame.from_dict(line))
    starting_frame = frames[0]
    for i in range(1, len(frames)):
        new_frame = pd.concat([starting_frame, frames[i]])
        starting_frame = new_frame
    starting_frame.to_csv('data/page9.csv', index=False)


def concat_it():
    starting_frame = None
    for i in range(1, 10):
        csv_string = 'data/page' + str(i) + '.csv'
        new_frame = pd.read_csv(csv_string)
        if starting_frame is None:
            starting_frame = new_frame
        else:
            concat = pd.concat([starting_frame, new_frame])
            starting_frame = concat
    starting_frame.to_csv('data/full_data.csv', index=False)


def clean_it():
    data = pd.read_csv('data/full_data_clean.csv')
    data_no_dup = data.drop_duplicates()
    data_clean = data_no_dup.loc[data["map_1"] != ' ']
    data_clean.to_csv('data/full_data_clean.csv', index=False)


clean_it()
