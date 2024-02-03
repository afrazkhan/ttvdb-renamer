#!/usr/bin/env python3

"""
Renames files based on series name and episode names found in thetvdb.com.
Makes pattern matching easy by using a delimeter and name position, rather than
a regular expression.

Requires an API key located in ~/.config/ttvdb/api_key, which you can get for
free here: https://thetvdb.com/api-information
"""

import json
import os
import re
from pathlib import Path
import click
import requests

api_base='https://api4.thetvdb.com/v4'
config_directory = os.path.expanduser('~/.config/ttvdb')

""" If we can't make a request to the API, fetch and set a new token"""
Path(config_directory).mkdir(exist_ok=True)
try:
    with open(f"{config_directory}/token", 'r') as file:
        token = file.read()
    requests.get(f"{api_base}/user", headers={'Authorization': token})
except Exception:
    with open(f"{config_directory}/api_key", 'r') as file:
        api_key = file.read()

    auth_payload = {"apikey": api_key}
    auth_r = requests.post(f"{api_base}/login", headers={'accept': 'application/json', 'Content-Type': 'application/json'}, data=json.dumps(auth_payload))
    token = auth_r.json()['data']['token']
    with open(f"{config_directory}/token", 'w') as file:
        file.write(token)

req = requests.Session()
req.headers.update({'Authorization': token})


def get_episodes(series: str) -> list:
    """ Returns a list of episodes if <series> is found """

    series_info_r = req.get(f"{api_base}/series/slug/{series}")
    series_id = series_info_r.json()['data']['id']

    next_page = f"{api_base}/series/{series_id}/episodes/default"
    episodes = []
    while next_page:
        series_r = req.get(next_page).json()
        episodes += (series_r['data']['episodes'])

        next_page = series_r['links']['next']

    return episodes

def find_episode(this_episode: str, episodes: str) -> int:
    """ Returns episode object if <this_episode> is found in <episodes> list"""

    return next((i for i, item in enumerate(episodes) if item["name"].lower() == this_episode.lower()), None)

def rename_file(filename, episode_info, series, batch):
    """ Deal with file renaming """

    season_and_episode = f"S{episode_info['seasonNumber']}E{episode_info['number']}"
    name = episode_info['name']
    new_filename = f"{series}.{season_and_episode}.{name}{os.path.splitext(filename)[1]}"

    if not batch:
        rename_okay = input(f"Rename '{filename}' to '{new_filename}'? [y/N]")
    else:
        rename_okay = 'y'

    if rename_okay == 'y':
        os.rename(filename, new_filename)
        print(f"🥸 Renamed '{filename}' to '{new_filename}'\n")

def get_file_list():
    this_directory = os.getcwd()

    return [f for f in os.listdir(this_directory) if os.path.isfile(os.path.join(this_directory, f))]


@click.command(no_args_is_help=True)
@click.argument('series')
@click.option('--delimeter', '-d', default='.', help="¡Work in Progress! Which character separates series info in the filename?")
@click.option('--name-position', '-n', default=1, help="How many delimeters are there before the name?")
@click.option('--batch', '-b', is_flag=True, default=False, help="Perform renames without asking for approval")
def scan(series, delimeter, name_position, batch):
    """
    Scan the current directory against thetvdb.com. The series name must be
    given, even if it appears in the filenames.

    --delimeter and --name-position can be used to tune where the episode name
    can be found in the filenames. The defaults of '.' and '1' respectively
    will work for files named so:

    '[series-name-or-anything].[episode-name].extension'

    results in

    '[series-name-or-anything].S[season-number]E[episode-number].extension'
    """

    series_slug = series.lower().replace(' ', '-')
    episodes = get_episodes(series_slug)

    file_list = get_file_list()

    for this_file in file_list:
        # This is a bit nasty, but we need to ignore things like 'Mr. '
        episode_name = re.split(f"\{delimeter}(?!\s)", this_file)[name_position]

        found = find_episode(episode_name, episodes)
        if found:
            rename_file(this_file, episodes[found], series, batch)
        else:
            print(f"⚠️ Couldn't find episode '{episode_name}' in series '{series}'\n")

if __name__ == '__main__':
    scan()
