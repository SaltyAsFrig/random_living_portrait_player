"""
Loads a folder of videos and randomly plays them when triggered by a PIR sensor (or other trigger).
Put this script in the same folder as the videos and launch. By default it will use *.mp4 as the filter.
You can set the repeatcount if you want to play the same video specific number of times before the next
random selection. While switching videos the desktop will be visible for a few seconds as omxplayer loads
again. To mask that it takes a screenshot of the currently paused starting frame and sets it as the
wallpaper. For this you **will also need to install** raspi2png to create the PNG file. There are also
configurable delays (in seconds) for how long to wait between a motion trigger event and playing the
video, and for how long to wait before enabling the trigger again after a video finishes. Use these to
enhance the startle factor by making it less predictable to passers by.

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
    print("Selected video: " + str(VIDEO_PATH))
    
    #set up omxplayer; load first video and pause; take a sccreenshot of the current video
    #and set the wallpaper to the screenshot
    player = OMXPlayer(VIDEO_PATH,  args=['--no-osd', '--loop', '--win', '0 0 {0} {1}'.format(slength, swidth)])
    sleep(1)
    player.pause()
    os.system("raspi2png --display 0 --pngname screen.png") 
    os.system("DISPLAY=:0 pcmanfm --set-wallpaper={0}/screen.png".format(cwd))

    #set up motionsensor
    pir = MotionSensor(4, queue_len=10, sample_rate=10, threshold=.75)

    print("Ready!")
    
    #Loop until keyboard interrupt [CTRL+C]
    while True:      
        if pir.motion_detected:
            tgr = tgr + 1
            print("Triggered! [count = {}]".format(tgr))
            
            #take a sccreenshot of the current video and set the wallpaper to the screenshot


            #Countdown the tgrDelay time
            for countdown in range(tgrDelay, 0, -1):
                print("Delay for",str(countdown - 1),"more seconds.   ", end = '\r')
                sleep(1)
            
            #Play the video
            print("\nPlaying!")
            player.play()
            sleep(player.duration())
            player.pause()

            #check if we need to pick a new video, update wallpaper
            if (tgr % repeatcount) == 0:
                for countdown in range(nextVideoDelay, 0, -1):
                    print("Waiting",str(countdown - 1),"seconds before switching videos.   ", end = '\r')
                    sleep(1)
                VIDEO_PATH = Path(videFilesList[random.randrange(0, len(videFilesList))])
                print("\nNext video: " + str(VIDEO_PATH))
                player.load(str(VIDEO_PATH), pause=True)
                os.system("raspi2png --display 0 --pngname screen.png") 
                os.system("DISPLAY=:0 pcmanfm --set-wallpaper={0}/screen.png".format(cwd))
            else:
                print("Repeat video {0} more times.".format(repeatcount - (tgr % repeatcount)))

            #wait fo the specified time before allowing a re-trigger
            for countdown in range(reTgrDelay, 0, -1):
                print("Waiting",str(countdown - 1),"seconds to rearm trigger.   ", end = '\r')
                sleep(1)
            print("\nReady!")
        else:
            pass
        player.set_position(0.0)


except KeyboardInterrupt:
    player.quit()
    sys.exit()
