"""
Loads a folder of videos and randomly plays them when triggered by a PIR sensor (or other trigger).
Put this script in the same folder as the videos and launch. By default it will use *.mp4 as the
filter. You can set the repeatcount if you want to play the same video specific number of times
before the next random selection. While switching videos the desktop will be visible for a few
seconds as omxplayer loads again. To mask that it takes a screenshot of the currently paused
starting frame and sets it as the wallpaper. For this you will also need to install raspi2png to
create the PNG file. There are also configurable delays (in seconds) for how long to wait between
a motion trigger event and playing the video, how long to wait before switching videos, and for
how long to wait before enabling the trigger again after a video finishes. Use these to enhance
the startle factor by making it less predictable to passers by.

This version was developed on a Pi4 using the 2021-05-07-raspios-buster-armhf release. You need to
use a Buster release that still has omxplayer in it as newer Raspbian releases don't work with it.
This should still work on a Pi3B+ too, but I don't have one to test with.

For best results clear the desktop of all icons, empty the toolbar and set it to 0% opacity so
it's invisible. That way between loading videos the screenshot wallpaper masks the fact that
omxplayer is closing and re-opening to load next file. I also use unclutter in my startup to hide
the mouse cursor.
"""

#!/usr/bin/env python3
#Based on the original script by scarethetots

from gpiozero import MotionSensor
import sys
import os
import glob
import random
from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep

class colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"

#PARAMETERS TO SET
repeatcount = 1 #how many times to repeat a video before next random selection
slength = '1920' #the screen's normally horizontal resolution
swidth = '1080' #the screen's normally vertical resolution
tgrDelay = 5 #seconds to wait before playing the video after motion trigger
reTgrDelay = 20 #seconds to wait after playing before re-enabling trigger
nextVideoDelay = 10 #seconds to wait before switching videos

cwd = os.getcwd()
tgr = 0 

print("Starting up....")
videFilesList = sorted(glob.glob('*.mp4')) #get list of files to play
print("Found "+ str(len(videFilesList)) +" videos.")

#list files found
for i in range(0, len(videFilesList)):
    print("  "+str(i+1)+".\t"+videFilesList[i])

try:
    VIDEO_PATH = Path(videFilesList[random.randrange(0, len(videFilesList))])
    print("Selected video: "+colors.CYAN+str(VIDEO_PATH)+colors.LIGHT_GRAY)
    
    #set up omxplayer; load first video and pause; take a sccreenshot of the current video
    #and set the wallpaper to the screenshot
    player = OMXPlayer(VIDEO_PATH,  args=['--no-osd', '--loop', '--win', '0 0 {0} {1}'.format(slength, swidth)])
    sleep(1)
    player.pause()
    os.system("raspi2png --display 0 --pngname screen.png") 
    os.system("DISPLAY=:0 pcmanfm --set-wallpaper={0}/screen.png".format(cwd))

    #set up motionsensor
    pir = MotionSensor(4, queue_len=10, sample_rate=10, threshold=.75)

    print(colors.LIGHT_GREEN+"Ready!"+colors.LIGHT_GRAY)
    
    #Loop until keyboard interrupt [CTRL+C]
    while True:      
        if pir.motion_detected:
            tgr = tgr + 1
            print(colors.BLUE+"Triggered!"+colors.LIGHT_GRAY+" [count = {}]".format(tgr))
            
            #take a sccreenshot of the current video and set the wallpaper to the screenshot


            #Countdown the tgrDelay time
            for countdown in range(tgrDelay, 0, -1):
                print("Delay for",colors.RED+str(countdown - 1)+colors.LIGHT_GRAY,"more seconds.   ", end = '\r')
                sleep(1)
            
            #Play the video
            print(colors.LIGHT_GREEN+"\nPlaying!"+colors.LIGHT_GRAY)
            player.play()
            sleep(player.duration())
            player.pause()

            #check if we need to pick a new video, update wallpaper
            if (tgr % repeatcount) == 0:
                for countdown in range(nextVideoDelay, 0, -1):
                    print("Waiting",colors.RED+str(countdown - 1)+colors.LIGHT_GRAY,"seconds before switching videos.   ", end = '\r')
                    sleep(1)
                VIDEO_PATH = Path(videFilesList[random.randrange(0, len(videFilesList))])
                print("\nNext video: "+colors.CYAN+str(VIDEO_PATH)+colors.LIGHT_GRAY)
                player.load(str(VIDEO_PATH), pause=True)
                os.system("raspi2png --display 0 --pngname screen.png") 
                os.system("DISPLAY=:0 pcmanfm --set-wallpaper={0}/screen.png".format(cwd))
            else:
                print("Repeat video "+colors.CYAN+"{0}".format(repeatcount - (tgr % repeatcount))+colors.LIGHT_GRAY+" more times.")

            #wait fo the specified time before allowing a re-trigger
            for countdown in range(reTgrDelay, 0, -1):
                print("Waiting",colors.RED+str(countdown - 1)+colors.LIGHT_GRAY,"seconds to rearm trigger.   ", end = '\r')
                sleep(1)
            print(colors.GREEN+"\nReady!"+colors.LIGHT_GRAY)
        else:
            pass
        player.set_position(0.0)


except KeyboardInterrupt:
    player.quit()
    sys.exit()
