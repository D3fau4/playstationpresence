import argparse
import os
import locale

from playstationpresence.playstationpresence import PlaystationPresence

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-tray-icon", help="Don't create a tray icon", action="store_true")
    args = parser.parse_args()

    pspresence = PlaystationPresence(locale.getdefaultlocale()[0])

    if args.no_tray_icon:
        pspresence.mainloop(notifier=None)
    else:
        from winstray import MenuItem as item
        from winstray._win32 import Icon, loadIcon

        image = loadIcon(os.path.join(os.path.dirname(__file__), 'logo.ico'))
        menu = [item('Quit', pspresence.quit)]

        icon: Icon = Icon("playstationpresence", image, "playstationpresence", menu)
        icon.icon = image
        icon.run(pspresence.mainloop)

if __name__ == "__main__":
    main()