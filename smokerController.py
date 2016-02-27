# !/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain
from __future__ import division

import math
import time
from datetime import datetime
import os
import sys
import RPi.GPIO as GPIO
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# 10k trim pot connected to adc #0
probe1 = 0
probe2 = 2
fanPin = 22
butt1Pin = 27
butt2Pin = 17

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(fanPin, GPIO.OUT)

GPIO.setup(butt1Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(butt2Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def buttonEvent(channel):
	
	time_pressed = time.time()
	while (GPIO.input(butt1Pin) == 0) or (GPIO.input(butt2Pin) == 0):
		time.sleep(0.01)
		pressed_count = time.time() - time_pressed
		
		if pressed_count > 5:
			print "Shutting Down"
			mail(fileName,
				"Smoker data attached",
				fileName)
			GPIO.cleanup()
			os.system("sudo shutdown -h now")
			sys.exit()
	
	if (channel == 17):
		global fuel
		fuel = 1
	elif (channel == 27):
		global lid
		lid = 1

GPIO.add_event_detect(butt1Pin, GPIO.FALLING, callback=buttonEvent, bouncetime=6000)
GPIO.add_event_detect(butt2Pin, GPIO.FALLING, callback=buttonEvent, bouncetime=6000)

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
	if ((adcnum > 7) or (adcnum < 0)):
			return -1
	GPIO.output(cspin, True)

	GPIO.output(clockpin, False)  # start clock low
	GPIO.output(cspin, False)     # bring CS low

	commandout = adcnum
	commandout |= 0x18  # start bit + single-ended bit
	commandout <<= 3    # we only need to send 5 bits here
	for i in range(5):
			if (commandout & 0x80):
					GPIO.output(mosipin, True)
			else:
					GPIO.output(mosipin, False)
			commandout <<= 1
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)

	adcout = 0
	# read in one empty bit, one null bit and 10 ADC bits
	for i in range(12):
			GPIO.output(clockpin, True)
			GPIO.output(clockpin, False)
			adcout <<= 1
			if (GPIO.input(misopin)):
					adcout |= 0x1

	GPIO.output(cspin, True)
	
	adcout >>= 1       # first bit is 'null' so drop it
	return adcout

def analToFar(anal):
	R = math.log1p((1 / ((1024 / anal) - 1)) * 10000);
	# Compute degrees C
	tempF = (1 / ((5.3612e-4) + (1.91532e-4) * R + (6.557e-8) * R * R * R)) - 273.25;
	#convert to F
	tempF = ((tempF * 9.0) / 5.0 + 32.0);
	return tempF	
	
EMAIL_TO = 'dnye2011@gmail.com, nickrumberger@gmail.com'
GMAIL_USER = 'dnye2011@gmail.com'
GMAIL_PASS = 'Jaeges@15a'
	
def mail(subject, text, attach):
	msg = MIMEMultipart()
	
	msg['From'] = GMAIL_USER
	msg['To'] = EMAIL_TO
	msg['Subject'] = subject

	msg.attach(MIMEText(text))

	part = MIMEBase('application', 'octet-stream')
	part.set_payload(open(attach, 'rb').read())
	Encoders.encode_base64(part)
	part.add_header('Content-Disposition',
		   'attachment; filename="%s"' % os.path.basename(attach))
	msg.attach(part)

	mailServer = smtplib.SMTP("smtp.gmail.com", 587)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	mailServer.login(GMAIL_USER, GMAIL_PASS)
	mailServer.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())
	# Should be mailServer.quit(), but that crashes...
	mailServer.close()


def calcTemp(probe, temp_fltr):
	analog = readadc(probe, SPICLK, SPIMOSI, SPIMISO, SPICS)
	if(analog < 1023):
		temp_local = analToFar(analog)
	else:
		temp_local = 0
		
	if temp_fltr == 0:
		temp_fltr = temp_local;
	else:
		temp_fltr = (0.9*temp_fltr) + (0.1*temp_local);
	return temp_fltr;

tempFile =  open("/home/pi/smokerController/smokerData/temp.txt", 'w')

fileName = datetime.now().strftime("%Y-%m-%d")
tempFile.write(fileName)
tempFile.write('\n')
time.sleep(10)
fileName = datetime.now().strftime("%Y-%m-%d")
tempFile.write(fileName)
tempFile.write('\n')
time.sleep(30)
fileName = datetime.now().strftime("%Y-%m-%d")
tempFile.write(fileName)
tempFile.write('\n')

fileName = '/home/pi/smokerController/smokerData/smokerData_' + fileName + '.txt'
tempFile.write('\n');	
tempFile.write(fileName)
tempFile.write('\nvalue: %d' % os.path.isfile(fileName))
tempFile.close()

if(os.path.isfile(fileName) == False):
	f = open(fileName, 'w')
	f.write('Smoker Data %s\n' % datetime.now().strftime("%Y-%m-%d"))
	f.write('Sampling every 5s\n\n')
	f.write('PitTemp,FoodTemp,FanSetPoint,FanStatus,FanCount,Lid,Fuel,Time')
	f.close()

tempF1 = 0;
tempF2 = 0;
fanCount = 0;

global lid
global fuel
lid = 0
fuel = 0
try:
	while True:
		tempF1 = calcTemp(probe1, tempF1);
		tempF2 = calcTemp(probe2, tempF2);
		
		fanSetTempFile = open('/home/pi/smokerController/fanSetTemp.txt', 'r')
		setTemp = int(fanSetTempFile.readline())
		fanSetTempFile.close()
		
		print setTemp
		if tempF1 < setTemp:
			GPIO.output(fanPin, True)
			fanStatus = 1;
			fanCount = fanCount + 1
		else:
			GPIO.output(fanPin, False)
			fanStatus = 0;
			fanCount = 0;
			
		localTime = datetime.now().strftime("%I:%M:%S")	
		f = open(fileName, 'a')
		f.write('\n%d,%d,%d,%d,%d,%d,%d,%s' % (tempF1, tempF2, setTemp, fanStatus, fanCount, lid, fuel, localTime))
		f.close()
		print "PitTemp: %d FoodTemp: %d FanStatus: %d FanCount: %d Lid: %d Fuel: %d %s" % (tempF1, tempF2, fanStatus, fanCount, lid, fuel, localTime)
		lid = 0;
		fuel = 0;
		time.sleep(5)
except KeyboardInterrupt:
	GPIO.cleanup()