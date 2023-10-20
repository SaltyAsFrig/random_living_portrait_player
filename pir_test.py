"""
Test PIR parameters and sensitivity.
If pir.value >= threshold then it detected motion.
"""

#!/usr/bin/env python3

from gpiozero import MotionSensor
import sys
from time import sleep

try:
    pir = MotionSensor(4, queue_len=10, sample_rate=10, threshold=.75)
    
    while True:
        print("                \t\tpir.value =", str(pir.value),"    ", end='\r')
        if pir.motion_detected:
            print("MOTION DETECTED!\t\tpir.value =", str(pir.value),"    ", end='\r')

        else:
            pass
    sleep(.5)

except KeyboardInterrupt:
    sys.exit()
