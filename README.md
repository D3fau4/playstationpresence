# What is this?

This is a combination of two apps/tools:

- A fork of the original [playstationpresence](https://github.com/elsorino/playstationpresence), a python
app that syncs your PlayStation game status with Discord
- A fork of the tooling from [PlayStationDiscord-Games](https://github.com/Tustin/PlayStationDiscord-Games),
which is used to collect game icons and push them to Discord as app assets

Many thanks to these developers for sharing their work!

# What's different here?

There are a couple of major changes at the moment:

- Non-Windows platforms are not explicitly supported. I don't have the hardware to support this and wouldn't 
use it myself, but the code is structured such that you can (in theory)  run it on a non-Windows platform in 
a "reduced functionality" state. Specifically, you would need to run the app with the `--no-tray-icon` flag,
which (as the name suggests), would mean that you will not have a tray icon or system notifications.
- PS4 is not supported. This is probably not as big of a lift to keep intact, but again: I don't have a PS4
so I'd rather just set it aside.
- The generation and uploading of game icons to Discord has been greatly overhauled. Instead of bulding out
from a .yml file, it looks up *your game library* and then grabs the appropriate images for games you own.
This means that in order for this app to be of any use you will need to go through the process of setting up
your own Discord app. The upside is that you're not reliant upon game databases maintained by other people,
and Discord enforces a cap of 300 assets per app so that shared database design was bound to cap out at some
point.

There are other little tweaks here and there, code that's been refactored, and a new system tray icon for
playstationpresence has been added (with notifications).

# How would I use this?

It's a bit of a process to get things off the ground, but after that maintenance should be much simpler.

There are two steps, first you need to get game icons in place:

1. Clone the repo and `pip install -r requirements.txt` to get all necessary dependencies.
2. Create your own Discord app through their [developer portal](https://discord.com/developers/applications).
Note that the name you choose here is what will show up as your primary status in your Discord status card, so
you might want to pick something like "PlayStation".
3. Log in to your PlayStation account through your web browser and then retrieve 
[your SSO cookie](https://ca.account.sony.com/api/v1/ssocookie).
4. Get a valid Discord token. There are a number of guides/ways to do this but one way that should generally
work is to log into the [Discord web app](https://discord.com/app), open your browser's dev console, and then
look in the Applications -> Local Storage view for a field named "token".
5. Once you have your data, create a config file at `{repositoryRoot}/.local/config.yaml`, following the format
in the sample file and replace the values with your own.
6. Run `asset_updater.py login`, `asset_updater.py generate`, and `asset_updater.py push`. If everything goes
well then you should see a bunch of assets in your Discord app.
7. You'll also need to find and create an asset named "ps5_main" in your Discord app. It can be whatever you
want but the idea is that it should probably be some version of the PS5 logo.

After all that's done, starting up playstationpresence is quite a bit easier:

1. Make sure your PSN token/ID and Discord app ID are set in the config file.
2. Run it: `.\presence.py` (or `pythonw .\presence.py` to run in the background on Windows). For non-Windows
systems you must also provide the `--no-system-tray` flag; you can also use this flag on Windows if you'd
prefer not to have the system tray icon/notifications.
3. If everything worked you should get a tray icon and a notification to let you know the app has started.
To quit the app, right click the tray icon and choose "Quit".

# Other notes

Once you have game icons in place (the first step above), you do not need to do that process again unless
you purchase a new game. Then you'll want to repeat at least the generate/push steps to get new images
and push them to your app. If your tokens haven't yet expired then you shouldn't need the login step.

If you have games or apps that you do NOT want to have icons, you can exclude them by adding them to
an `ignored_titles.yaml` file in the `.local/` directory (see the sample). If you launch these titles
while playstationpresence is running then the text of your presence will be the game/app name and
the icon will simply be set to whatever your default `ps5_main` icon is.