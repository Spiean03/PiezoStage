#import programming tools
import time
import os
import sys

#wiimote
import cwiid

#audio
import ossaudiodev
import wave

#raspberry settings
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)


#On a new Pi:

#install alsa-base/alsa-utils/bluetooth/python-cwiid
#sudo service bluetooth status (check bluetooth status)
#hcitool dev (pi-adress)
#hcitool scan (scans for wiimote, press 1 + 2)
#sudo modprobe snd-pcm-oss (enables ossaudiodev), write snd-pcm-oss in /etc/modules
#sudo nano /etc/modprobe.d/alsa-base.conf depends on raspbian version
#either remove a # at the start of "options snd-usb-audio index=0"
#or change "options snd-usb-audio index -2" to index=0
#write python /home/pi masterswitch.py & above exit 0 in sudo nano /etc/rc.local to autostart masterswitch.py at startup

def main():

  #Led on pin 11 is on while waiting for an input (1+2) from the wiimote
  GPIO.output(11, True)
  print 'press button 1 + 2 on your Wii Remote...'
  time.sleep(1)

  #Actual search for a wiimote input, if succesful turn led11 out
  wm = cwiid.Wiimote()
  GPIO.output(11, False)
  print "Wii Remote connected..."

  #all leds are on for a short amount of time so the user sees
  #it is connected succesfully
  GPIO.output(7, True)
  GPIO.output(11, True)
  GPIO.output(16, True)
  GPIO.output(18, True)
  GPIO.output(22, True)

  time.sleep(0.77)

  GPIO.output(7, False)
  GPIO.output(11, False)
  GPIO.output(16, False)
  GPIO.output(18, False)
  GPIO.output(22, False)

  #shortcut wm for wiimote
  wm.rpt_mode = cwiid.RPT_BTN

  #setting variables used as counters to 0
  cplus=0
  cminus=0
  ctot=cplus-cminus

  xcount=0
  ycount=0

  #setting variables used as memory to 0
  prev_inputcplus=0
  prev_inputcminus=0
		
  while True:

      #actual programm, wii library:
      #'1' = 2
      #'2' = 1 (Sehsch dironie?;)
      #'a' = 8
      #'b' = 4
      #'plus' = 4096
      #'minus' = 16
      #'home' = 128
      #'left' = 2048
      #'right' = 1024
      #'up' = 512
      #'down' = 256
      #(if you hold the wiimote horizontally
      #with the direction buttons on the left side)
      #'left + 1' = 2050
      #'left + 2' = 2049  
      #same for 'right', 'up' and 'down'  

      #printcommands only useful while testing on screen/can be commanded# out			
      while wm.state['buttons'] == 2:
        print '1'
      while wm.state['buttons'] == 1:
        print '2'

      #if plus is pressed and prevcplus_input isn't 0 add 1 to cplus
      #if cplus-cminus exceeds 3 substract 1 from cplus so it will remain 3
      #ctot is determined as cplus-cminus which indicates the total speed mode (0, 1, 2 or 3)
      if (wm.state['buttons'] == 4096 and (not prevcplus_input)):
        print 'One speed higher'
        cplus+=1
        if cplus-cminus>3:
          cplus-=1
        ctot=cplus-cminus
        print 'You are on Speedlevel %r' %ctot

      #prevcplus_input does: while plus is pressed only add 1 once every time a command is received
      prevcplus_input=wm.state['buttons']==4096

      #same for cminus with a restriction not to go lower than 0
      if (wm.state['buttons'] == 16 and (not prev_inputcminus)):
        print 'One speed lower'
        cminus+=1
        if cplus-cminus<0:
          cminus-=1
        ctot=cplus-cminus
        print 'You are on Speedlevel %r' %ctot

      prev_inputcminus=wm.state['buttons']==16

      #again determination of speed mode
      ctot=cplus-cminus

      #determines which leds(16, 18, 22) are lit while on e specified speed mode so the user can see it
      if ctot==0:
        GPIO.output(16, False)
        GPIO.output(18, False)
        GPIO.output(22, False)
      if ctot==1:
        GPIO.output(16, True)
        GPIO.output(18, False)
        GPIO.output(22, False)
      if ctot==2:
        GPIO.output(16, True)
        GPIO.output(18, True)
        GPIO.output(22, False)
      if ctot==3:
        GPIO.output(16, True)
        GPIO.output(18, True)
        GPIO.output(22, True)

      #if home is pressed all leds light up shortly to indicate the user that the connection will be closed
      #and if in the right place the script masterswitch.py (programm starting switch) will be opened
      if wm.state['buttons'] == 128:
        GPIO.output(7, True)
        GPIO.output(11, True)
        GPIO.output(16, True)
        GPIO.output(18, True)
        GPIO.output(22, True)

        time.sleep(0.77)

        GPIO.output(7, False)
        GPIO.output(11, False)
        GPIO.output(16, False)
        GPIO.output(18, False)
        GPIO.output(22, False)
        exit(wm)
        os.system('python /home/pi/masterswitch.py')


      #the rest will just be the commands for the 4 directions
      #the user is able to either press 'left', 'left + 1' or 'left + 2'
      #which corresponds three different breaks during the output of the content of a .wav-audiofile
      #again printcommands are only useful while testing on a screen
      #explanations will only be on the first part
      #since 'right' will be the same axis as 'left' and vice versa for 'up' and 'down'
      #the other difference is only the speed mode (ctot==0, 1, 2 or 3)
      #the difference there will be a different audiofile, the rest should be the same

      #Speed 1
      #X-Axis ('left' and 'right')

      #while any of the X-Axis combinations are pressed on the wiimote:
      #the axis-indicator-led7 is turned off
      #the ycount is set to 0
      #the xcount mounts 1 for every X-Axis combination pressed on the wiimote
      #if the xcount is 1, which means it is th first X-Axis combination after a Y-Axis combination
      #there is a break of 10msec
      #this should alow the external relay to switch the signal on the correct output (X-Axis)

      #while any of the Y-Axis combinations are pressed on the wiimote:
      #the xcount is set to 0
      #the ycount mounts 1 for every Y-Axis combination pressed on the wiimote
      #if the ycount is 1, which means it is th first Y-Axis combination after a X-Axis combination
      #there is a break of 10msec and the axis-indicator-led7 is turned on
      #the break should alow the external relay to switch the signal on the correct output (Y-Axis)
      
      #sound_file = wave.open('/home/pi/sawtooth_10_minus.wav', 'rb')
        #opens .wav-audiofile
      #(nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        #gets parameters
      #sound = ossaudiodev.open('w')
        #opens audio output
      #sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        #sets parameters
      #data = sound_file.readframes(65536)
      #sound.write(data)
        #actually read the file
      #sound.flush()
      #sound.sync()
        #synchronises audio and deletes traces
      #sound.bufsize()
        #reads the buffersize
      #sound.obufcount()
        #reads the space used for pending output
      #sound.obuffree()
        #reads the amount of free memory
      #sound_file.close()
        #closes the file
      #sound.close()
        #closes the audio output
      #sawtooth_10_minus.wav consists of 10 tooths in negative direction
      #which means the opposite direction should be positively oriented (sawtooth_10.wav)
      #'left' has the same file as 'down' or 'up' and vice versa for 'right'
      #the only difference is the input on the microscope, which will be controlled with the external relay
      #there is a natural break of approximately 125usec between every period of 10 or whatever tooths
      #this break is caused by the duration of closing file and audio output and opening it again
      #those commands are necessary every time and can not be cut out
      #with time.sleep(x) you can extend this break to 125usec + x sec
      #the user can press every direction button + 1, 2 or nothing
      #the break is supposed to be bigger if the user presses only 'left' instead of 'left + 1'
      #same with 'left + 1' and 'left + 2'
      #this should result in 3 easily controllable speeds in each direction and speed mode
      #for 4 speed modes and 3 different breaks the user has 12 possible speeds in each direction
      #Alex Stauffer
      #Switzerland;)


      while wm.state['buttons'] == 2049 and ctot==0:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left'
        sound_file = wave.open('/home/pi/sawtooth_5_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2050 and ctot==0:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left medium speed'
        sound_file = wave.open('/home/pi/sawtooth_5_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2048 and ctot==0:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left max speed'
        sound_file = wave.open('/home/pi/sawtooth_5_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 1025 and ctot==0:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right'
        sound_file = wave.open('/home/pi/sawtooth_5.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1026 and ctot==0:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right medium speed'
        sound_file = wave.open('/home/pi/sawtooth_5.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1024 and ctot==0:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right max speed'
        sound_file = wave.open('/home/pi/sawtooth_5.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()



      #Y-Axis ('up' and 'down')
      while wm.state['buttons'] == 513 and ctot==0:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up'
        sound_file = wave.open('/home/pi/sawtooth_5_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 514 and ctot==0:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up medium speed'
        sound_file = wave.open('/home/pi/sawtooth_5_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 512 and ctot==0:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up max speed'
        sound_file = wave.open('/home/pi/sawtooth_5_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 257 and ctot==0:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down'
        sound_file = wave.open('/home/pi/sawtooth_5.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 258 and ctot==0:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down medium speed'
        sound_file = wave.open('/home/pi/sawtooth_5.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 256 and ctot==0:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down max speed'
        sound_file = wave.open('/home/pi/sawtooth_5.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()









      #Speed 2
      while wm.state['buttons'] == 2049 and ctot==1:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left'
        sound_file = wave.open('/home/pi/sawtooth_10_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2050 and ctot==1:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left medium speed'
        sound_file = wave.open('/home/pi/sawtooth_10_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2048 and ctot==1:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left max speed'
        sound_file = wave.open('/home/pi/sawtooth_10_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 1025 and ctot==1:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right'
        sound_file = wave.open('/home/pi/sawtooth_10.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1026 and ctot==1:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right medium speed'
        sound_file = wave.open('/home/pi/sawtooth_10.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1024 and ctot==1:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right max speed'
        sound_file = wave.open('/home/pi/sawtooth_10.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()



      while wm.state['buttons'] == 513 and ctot==1:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up'
        sound_file = wave.open('/home/pi/sawtooth_10_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 514 and ctot==1:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up medium speed'
        sound_file = wave.open('/home/pi/sawtooth_10_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 512 and ctot==1:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up max speed'
        sound_file = wave.open('/home/pi/sawtooth_10_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 257 and ctot==1:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down'
        sound_file = wave.open('/home/pi/sawtooth_10.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 258 and ctot==1:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down medium speed'
        sound_file = wave.open('/home/pi/sawtooth_10.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 256 and ctot==1:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down max speed'
        sound_file = wave.open('/home/pi/sawtooth_10.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()









      #Speed 3
      while wm.state['buttons'] == 2049 and ctot==2:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left'
        sound_file = wave.open('/home/pi/sawtooth_50_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2050 and ctot==2:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left medium speed'
        sound_file = wave.open('/home/pi/sawtooth_50_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2048 and ctot==2:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left max speed'
        sound_file = wave.open('/home/pi/sawtooth_50_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 1025 and ctot==2:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right'
        sound_file = wave.open('/home/pi/sawtooth_50.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1026 and ctot==2:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right medium speed'
        sound_file = wave.open('/home/pi/sawtooth_50.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1024 and ctot==2:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right max speed'
        sound_file = wave.open('/home/pi/sawtooth_50.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()



      while wm.state['buttons'] == 513 and ctot==2:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up'
        sound_file = wave.open('/home/pi/sawtooth_50_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 514 and ctot==2:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up medium speed'
        sound_file = wave.open('/home/pi/sawtooth_50_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 512 and ctot==2:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up max speed'
        sound_file = wave.open('/home/pi/sawtooth_50_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 257 and ctot==2:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down'
        sound_file = wave.open('/home/pi/sawtooth_50.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 258 and ctot==2:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down medium speed'
        sound_file = wave.open('/home/pi/sawtooth_50.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 256 and ctot==2:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down max speed'
        sound_file = wave.open('/home/pi/sawtooth_50.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()









      #Speed 4
      while wm.state['buttons'] == 2049 and ctot==3:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left'
        sound_file = wave.open('/home/pi/sawtooth_100_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2050 and ctot==3:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left medium speed'
        sound_file = wave.open('/home/pi/sawtooth_100_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 2048 and ctot==3:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'left max speed'
        sound_file = wave.open('/home/pi/sawtooth_100_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 1025 and ctot==3:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right'
        sound_file = wave.open('/home/pi/sawtooth_100.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1026 and ctot==3:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right medium speed'
        sound_file = wave.open('/home/pi/sawtooth_100.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 1024 and ctot==3:
        GPIO.output(7, False)
        xcount+=1
        ycount=0
        if xcount==1:
          print 'xcount = 1'
          time.sleep(0.01)
        print 'right max speed'
        sound_file = wave.open('/home/pi/sawtooth_100.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()



      while wm.state['buttons'] == 513 and ctot==3:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up'
        sound_file = wave.open('/home/pi/sawtooth_100_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 514 and ctot==3:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up medium speed'
        sound_file = wave.open('/home/pi/sawtooth_100_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 512 and ctot==3:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'up max speed'
        sound_file = wave.open('/home/pi/sawtooth_100_minus.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

      while wm.state['buttons'] == 257 and ctot==3:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down'
        sound_file = wave.open('/home/pi/sawtooth_100.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.88)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 258 and ctot==3:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down medium speed'
        sound_file = wave.open('/home/pi/sawtooth_100.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        time.sleep(0.38)
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()
      while wm.state['buttons'] == 256 and ctot==3:
        ycount+=1
        xcount=0
        if ycount==1:
          print 'ycount = 1'
          GPIO.output(7, True)
          time.sleep(0.01)
        print 'down max speed'
        sound_file = wave.open('/home/pi/sawtooth_100.wav', 'rb')
        (nc, sw, fr, nf, comptype, compname) = sound_file.getparams()
        sound = ossaudiodev.open('w')
        sound.setparameters(ossaudiodev.AFMT_S16_NE, nc, fr)
        data = sound_file.readframes(65536)
        sound.write(data)
        sound.flush()
        sound.sync()
        sound_file.close()
        buf = sound.bufsize()
        print 'Bufsize: %r' %buf
        obuf = sound.obufcount()
        print 'Pending: %r' %obuf
        obuff = sound.obuffree()
        print 'Free: %r' %obuff
        sound.close()

#put the volume to 100 -> amplitude setting
#os.system('sudo amixer cset numid=5 -- 400')
#set the audio output to the one on board
print os.system('sudo amixer cset numid=3 1')
#clear the window in the terminal
print os.system("clear"),chr(13),"  ",chr(13),

main()
