#!/usr/bin/env python
import RPi.GPIO as GPIO
import pygame
import time
import mpr121
import os
import LCD1602
from  itertools import cycle
import talkey

KidRockPin = 5
Gpin   = 26
Rpin   = 23
BackGroundMusicArrayCount = 0
touches = [0,0,0,0,0,0,0,0,0,0,0,0];

snare = None
kick = None
closedhh = None
openhh = None
tom1 = None
tom2 = None
BackGroundMusic = None
BackGroundMusicArray = []
BackGroundMusicArrayCount = 0
KidRockVar = 0
MusicPaused = 1
IterFunc = cycle([0,1]).next
PauseFunc = cycle([0,1,2]).next
tts = talkey.Talkey(
	preferred_languages =['en'],
	preferred_factor =80.0,
	engine_preference = ['pico']
	)

def setup():
	# PIN Setup
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by physical location
	GPIO.setup(Gpin, GPIO.OUT)     # Set Green Led Pin mode to output
	GPIO.setup(Rpin, GPIO.OUT)     # Set Red Led Pin mode to output
	GPIO.setup(6, GPIO.IN)		# Set interrupt Pin to input
	GPIO.setup(KidRockPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(KidRockPin, GPIO.FALLING, callback=detect, bouncetime=300)
	#Pygame setup
	pygame.mixer.pre_init(44100, -16, 2, 512)
	pygame.mixer.init()
	pygame.mixer.music.set_volume(0.99)  
	# Initialize MPR121 here
	mpr121.TOU_THRESH = 10
	mpr121.REL_THRESH = 20
	mpr121.setup(0x5a)
	tts.say("Let's get this party started")
	# Initialize LCD Display
	LCD1602.init(0x27, 1)
	LCD1602.clear()
	KidRock()
    
def KidRock():
	global KidRockVar
	global snare
	global kick
	global closedhh
	global openhh
	global tom1
	global tom2
	global BackGroundMusic
	global BackGroundMusicArrayCount
	global BackGroundMusicArray
	KidRockVar = IterFunc()
	if (KidRockVar == 0):
		filepath_music = "/home/pi/beetbox/samples_music/kid/"
		filepath_drums = "/home/pi/beetbox/kid_drums/"
		lcd_message = "Kid-Mode!"
		GPIO.output(Rpin, 0)
		GPIO.output(Gpin, 1)
		talkey_message = "Kid Mode activated!"
	else:		
		GPIO.output(Rpin, 1)
		GPIO.output(Gpin, 0)
		filepath_music = "/home/pi/beetbox/samples_music/drumless_songs/"
		filepath_drums = "/home/pi/beetbox/drums/"
		lcd_message = "Rock-Mode!"
		talkey_message = "Rock Mode activated!"
	#load background music in an array to skip through
	BackGroundMusicArray = []
	DrumsArray = []
	for filename in sorted(os.listdir(filepath_music)):
		BackGroundMusicArray.append(filepath_music + filename)
	BackGroundMusicArrayCount = 0
	pygame.mixer.music.load(BackGroundMusicArray[BackGroundMusicArrayCount])
	pygame.mixer.music.set_volume(0.7)
	#drum sounds are loaded
	for filename_drums in sorted(os.listdir(filepath_drums)):
		DrumsArray.append(filepath_music + filename_drums)
	kick = pygame.mixer.Sound(DrumsArray[0])
	snare = pygame.mixer.Sound(DrumsArray[1])
	closedhh = pygame.mixer.Sound(DrumsArray[2])
	openhh = pygame.mixer.Sound(DrumsArray[3])
	tom1 = pygame.mixer.Sound(DrumsArray[4])
	tom2 = pygame.mixer.Sound(DrumsArray[5])
	LCD1602.clear()
	LCD1602.write(0, 0, lcd_message)
	showtitle = BackGroundMusicArray[0]
	indexofslash = showtitle.rfind("/")+1
	showtitle = showtitle[indexofslash:]
	LCD1602.write(0, 1,showtitle)
	tts.say(talkey_message)

def detect(chn):
	pygame.mixer.music.stop()
	KidRock()

def nextSong():
	global BackGroundMusic
	global BackGroundMusicArrayCount
	global BackGroundMusicArray
	pygame.mixer.music.stop()
	if (BackGroundMusicArrayCount != len(BackGroundMusicArray)):
		BackGroundMusicArrayCount = BackGroundMusicArrayCount+1
		pygame.mixer.music.load(BackGroundMusicArray[BackGroundMusicArrayCount])
		#pygame.mixer.music.play(0)
	else:
		BackGroundMusicArrayCount = 0
		pygame.mixer.music.load(BackGroundMusicArray[BackGroundMusicArrayCount])
		#pygame.mixer.music.play(0)
	LCD1602.clear()
	showtitle = BackGroundMusicArray[BackGroundMusicArrayCount]
	indexofslash = showtitle.rfind("/")+1
	showtitle = showtitle[indexofslash:]
	LCD1602.write(0, 1,showtitle)

def previousSong():
	global BackGroundMusic
	global BackGroundMusicArrayCount
	global BackGroundMusicArray
	pygame.mixer.music.stop()
	if (BackGroundMusicArrayCount != 0):
		BackGroundMusicArrayCount = BackGroundMusicArrayCount-1
		pygame.mixer.music.load(BackGroundMusicArray[BackGroundMusicArrayCount])
		#pygame.mixer.music.play(0)
	else:
		BackGroundMusicArrayCount = len(BackGroundMusicArray)-1
		pygame.mixer.music.load(BackGroundMusicArray[BackGroundMusicArrayCount])
		#pygame.mixer.music.play(0)
	LCD1602.clear()
	showtitle = BackGroundMusicArray[BackGroundMusicArrayCount]
	indexofslash = showtitle.rfind("/")+1
	showtitle = showtitle[indexofslash:]
	LCD1602.write(1, 0,showtitle)

def run():
	global BackGroundMusic
	global MusicPaused
	while True:
		if (GPIO.input(6)): # Interupt pin is high
			pass
		else: # Interupt pin is low
			touchData = mpr121.readData(0x5a)
			for i in range(9):
				if (touchData & (1<<i)):
					if (touches[i] == 0):
							#print( 'Pin ' + str(i) + ' was just touched')
						if (i == 0):
							kick.play()
						elif i == 1:
							snare.play()
						elif i == 2:
							openhh.play()
						elif i == 3:
							closedhh.play()
						elif i == 4:
							tom1.play()
						elif i == 5:
							tom2.play()
						elif i == 6:
							previousSong()
						elif i == 7:
							MusicPaused = PauseFunc()
							if (MusicPaused == 0):
								pygame.mixer.music.stop()
								time.sleep(0.2)
								pygame.mixer.music.play()
							elif (MusicPaused == 1):
								pygame.mixer.music.pause()
							elif (MusicPaused == 2):
								pygame.mixer.music.unpause()
						elif i == 8:
							nextSong()
					touches[i] = 1
				else:
					if (touches[i] == 1):
						#print( 'Pin ' + str(i) + ' was just released')
						touches[i] = 0;

def destroy():
	GPIO.output(Gpin, GPIO.HIGH)       # Green led off
	GPIO.output(Rpin, GPIO.HIGH)       # Red led off
	GPIO.cleanup()                     # Release resource
	LCD1602.clear()
	LCD1602.write(0,0,"Good bye,")
	LCD1602.write(0,1,"Niklas")

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		run()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()
