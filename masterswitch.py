#import modules
import time
from sys import exit
import os
import sys
#make pin settings
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.IN)


#define program
def main():
  #set a variable that will buffer the input and make multiple inputs fro one switch pull impossible
  prev_input=0		
  while True:
    input = GPIO.input(13)
    # if switch is turned on, start wiifile.py
    if ((not prev_input) and input):
      print 'button'		
      time.sleep(1)
      os.system('python /home/pi/wiifile.py')
      GPIO.output(11, False)
    prev_input = input
    time.sleep(0.5)

#set audio output and clear terminal
print os.system('sudo amixer cset numid=3 1')
print os.system("clear"),chr(13),"  ",chr(13),

#run program
main()