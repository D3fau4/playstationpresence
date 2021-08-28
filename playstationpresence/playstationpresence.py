#!/usr/bin/env python3
import asyncio
import os
import time
import winstray
import yaml
from psnawp_api import psnawp
from pypresence import Presence
from winstray import MenuItem as item
from winstray._base import Icon
from winstray._win32 import loadIcon
from threading import Event

exit_event = Event()

def discordrpc(clientId):
    rpc = Presence(clientId, pipe=0, loop=asyncio.new_event_loop())
    rpc.connect()
    return rpc

def quit(icon: Icon):
    icon.visible = False
    exit_event.set()
    icon.stop()

def clearStatus(rpc: Presence, icon: Icon):
    print("User is offline, clearing status")
    rpc.clear()
    icon.title = "Offline"
    icon.notify(f"Status changed to Offline", "playstationpresence")

def updateStatus(rpc: Presence, tray_icon: Icon, state: str, psnid: str, large_image: str, large_text: str, tray_tooltip: str):
    start_time = int(time.time())
    rpc.update(state=state, start=start_time, small_image="ps5_main", small_text=psnid, large_image=large_image, large_text=large_text)
    print(f"Status changed to {tray_tooltip}")
    tray_icon.title = tray_tooltip
    tray_icon.notify(f"Status changed to {tray_tooltip}", "playstationpresence")

def mainloop(icon: Icon):
    old_info: dict = {}
    config: dict = yaml.safe_load(open("../.local/config.yaml", "r"))
    npsso = config['npsso']
    psnid = config['PSNID']
    ps = psnawp.PSNAWP(npsso)

    icon.visible = True

    rpc = discordrpc(config['discordClientId'])
    
    while not exit_event.is_set():
        user_online_id = ps.user(online_id=psnid)
        mainpresence: dict = user_online_id.get_presence()
        platform_info: dict = mainpresence['primaryPlatformInfo']
        game_info: list[dict] = mainpresence.get('gameTitleInfoList', None)
        
        if platform_info['onlineStatus'] == "offline" and not old_info.get('onlineStatus', "") == "offline":
            clearStatus(rpc, icon)
        else: 
            if (old_info == platform_info):
                pass
            else:
                if (game_info == None):
                    updateStatus(rpc, icon, psnid, "Not in game", "ps5_main", "Homescreen", "Not in game")
                else:
                    game: dict[str, str] = game_info[0]
                    updateStatus(rpc, icon, game['titleName'], psnid, game['npTitleId'].lower(), game['titleName'], f"Playing {game['titleName']}")

        exit_event.wait(20) #Adjust this to be higher if you get ratelimited
        old_info = platform_info

    rpc.close()

def main():
    image = loadIcon(os.path.join(os.path.dirname(__file__), 'logo.ico'))

    menu = [item('Quit', quit)]

    icon: Icon = winstray.Icon("playstationpresence", image, "playstationpresence", menu)
    icon.icon = image
    icon.run(mainloop)

if __name__ == "__main__":
    main()