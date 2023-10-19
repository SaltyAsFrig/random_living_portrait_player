# random_living_portrait_player

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
