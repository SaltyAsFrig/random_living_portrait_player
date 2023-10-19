"""
Loads a folder of videos and randomly plays them when triggered by a PIR sensor (or other trigger).
Put this script in the same folder as the videos and launch. By default it will use *.mp4 as the filter.
You can  set a repeatcount if you want to play the same video specific number of times before the next
random selection. While switching video the desktop will be visible for a few seconds as omxplayer loads
again. To mask this ive implemented taking a screenshot of the currently paused starting frame and setting
it as the wallpaper as the video plays. For this you **will also need to install** raspi2png to create the PNG
file.

This version was developed on a Pi4 using the 2021-05-07-raspios-buster-armhf release. You need to use a Buster
release that still has omxplayer in it as newer Raspbian releases don't work with it. This should still work on
a Pi3B+ too, but I don't have one to test with.

For best results clear the desktop of all icons, empty the toolbar and set it to 0% opacity so it's invisible.
That way between loading videos the screenshot wallpaper masks the fact that omxplayer is closing and re-opening
to load next file. I also use unlcutter in my startup to hide the mouse cursor.
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


repeatcount = 1 #how many times to repeat a video before next random selection
slength = '1920' 
swidth = '1080'
tgr = 0
cwd = os.getcwd()

print("Starting up....")
videFilesList = sorted(glob.glob('*.mp4')) #get list of files to play
print("Found "+ str(len(videFilesList)) +" videos.")

#list files found
for i in range(0, len(videFilesList)):
    print("  "+str(i+1)+".\t"+videFilesList[i])

try:
    VIDEO_PATH = Path(videFilesList[random.randrange(0, len(videFilesList))])
    print("Selected video: " + str(VIDEO_PATH))
    player = OMXPlayer(VIDEO_PATH,  args=['--no-osd', '--loop', '--win', '0 0 {0} {1}'.format(slength, swidth)])
    pir = MotionSensor(4)
    sleep(1)
    print("Ready to trigger")
    while True:
        player.pause()
        if pir.motion_detected:
            print("trigger count {}".format(tgr))            
            os.system("raspi2png --display 0 --pngname screen.png") #take a sccreenshot of the current video 
            os.system("DISPLAY=:0 pcmanfm --set-wallpaper={0}/screen.png".format(cwd)) #set wallpaper to the screenshot
            player.play()
            sleep(player.duration())
            tgr = tgr + 1
            if (tgr % repeatcount) == 0:
                VIDEO_PATH = Path(videFilesList[random.randrange(0, len(videFilesList))])
                print("Next video: " + str(VIDEO_PATH))
                player.load(str(VIDEO_PATH), pause=True)
        else:
            pass
        player.set_position(0.0)


except KeyboardInterrupt:
    player.quit()
    sys.exit()
