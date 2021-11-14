#!/usr/bin/env python3
import argparse
import os
import requests
import shutil
import sys
import time
from datetime import timedelta
from discord_assets.push import push_assets
from playstationpresence.lib.files import load_config, load_game_data, load_ignored_titles, save_config, save_game_data
from playstationpresence.lib.psnclient import PSNClient

icon_dir = ".local/game_icons"

def get_refresh_token(config):
    client = PSNClient(config['npsso'])
    oauth_code = client.get_oauth_code()
    token = client.get_refresh_token(oauth_code)
    config['refresh_token'] = token['refresh_token']
    config['refresh_token_expiration'] = token['refresh_token_expiration']
    save_config(config)

def refresh_token_is_expiring(config):
    delta = timedelta(seconds=(config['refresh_token_expiration'] - time.time()))
    return delta < timedelta(days=7)

def build_game_library(config):
    print("Retrieving game library...")

    client = PSNClient(config['npsso'], config['refresh_token'])
    #data = client.get_purchased_games()
    data = client.get_recent_games()

    # These are the titles for which we will not be uploading icons
    # Note: this file may not exist
    try:
        ignored_titles = load_ignored_titles()
    except:
        ignored_titles = set()
    
    # Some games may not appear as "purchased" because they are, e.g., pack-ins (like Astro's Playroom).
    # Initialize the library with these games to make sure they're included in the asset gathering process.
    library = {
        "ps5": { },
        "ps4": { }
    }

    try:
        for game in data['data']['purchasedTitlesRetrieve']['games']:
            if game['titleId'] in ignored_titles:
                continue

            if game['platform'].lower() == "ps4":
                # If we find a PS4 title we already saw on PS5, ignore the PS4 version
                if game['name'] in library['ps5']:
                    continue
            elif game['platform'].lower() == "ps5":
                # If we find a PS5 title we already saw on PS4, delete the PS4 record
                if game['name'] in library['ps4']:
                    del(library['ps4'][game['name']])

            library[game['platform'].lower()][game['name']] = {
                'name': game['name'],
                'titleId': game['titleId'],
                'image': game['image']['url']
            }
    except:
        for game in data['data']['gameLibraryTitlesRetrieve']['games']:
            if game['titleId'] in ignored_titles:
                continue

            if game['platform'].lower() == "ps4":
                # If we find a PS4 title we already saw on PS5, ignore the PS4 version
                if game['name'] in library['ps5']:
                    continue
            elif game['platform'].lower() == "ps5":
                # If we find a PS5 title we already saw on PS4, delete the PS4 record
                if game['name'] in library['ps4']:
                    del(library['ps4'][game['name']])
            else:
                continue


            library[game['platform'].lower()][game['name']] = {
                'name': game['name'],
                'titleId': game['titleId'],
                'image': game['image']['url']
            }

    print(f"Found {len(library['ps4']) + len(library['ps5'])} games in library")
    
    return library
    
def retrieve_game_icons(library):
    if len(library['ps4']) == 0 and len(library['ps5']) == 0:
        return

    if os.path.exists(icon_dir):
        shutil.rmtree(icon_dir)
		
    os.mkdir(icon_dir)

    for game in { **library['ps4'], **library['ps5'] }.values():
        print(f"Downloading image for {game['name']} ({game['titleId']})")
        output_file = f"{icon_dir}/{game['titleId']}.png"
        with requests.get(game['image'], stream=True) as r:
            with open(output_file, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

def write_games_yaml(library, verbose):
    print("Writing game data to disk...")

    if verbose:
        for game in { **library['ps4'], **library['ps5'] }.values():
            print(f"{game['name']} ({game['titleId']})")

    # Just save game IDs for the client to use for looking up what we support
    game_data = \
        [item['titleId'] for item in library['ps5'].values()] + \
        [item['titleId'] for item in library['ps4'].values()]

    save_game_data(game_data)

def generate(args):
    config = load_config()

    if refresh_token_is_expiring(config):
        print("Refresh token is approaching expiration; getting a new token")
        get_refresh_token(config)

    library = build_game_library(config)

    if not args.skip_icons:
        retrieve_game_icons(library)

    write_games_yaml(library, args.verbose)

def login(args):
    config = load_config()
    get_refresh_token(config)

def push(args):
    config = load_config()
    game_data = load_game_data()
    push_assets(config, game_data)

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", title="Available commands", metavar="")

    generate_command = subparsers.add_parser("generate", help="Build library, download icons, and write games.json")
    generate_command.add_argument("--skip-icons", help="Skip icon download step", action="store_true")
    generate_command.add_argument("--verbose", "-v", help="Print list of games found to the console", action="store_true")
    generate_command.set_defaults(func=generate)

    push_command = subparsers.add_parser("push", help="Push assets to Discord")
    push_command.set_defaults(func=push)

    login_command = subparsers.add_parser("login", help="Log in to PSN")
    login_command.set_defaults(func=login)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()