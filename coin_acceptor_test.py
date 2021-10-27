# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import RPi.GPIO as GPIO
from threading import Thread
from RPLCD.gpio import CharLCD
from RPLCD.i2c import CharLCD
from gpiozero import LEDBoard
import time

# LCD1602 variables.
# lcd = CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)
# lcd = CharLCD('PCF8573', address=0x27, port=1, backlight_enabled=False)
lcd = CharLCD('PCF8574', address=0x27, port=1, cols=16, rows=2, dotsize=8, auto_linebreaks=True, backlight_enabled=True)

def write_to_lcd(lcd, framebuffer, num_cols):
    lcd.home()
    for row in framebuffer:
        lcd.write_string(row.ljust(num_cols)[:num_cols])
        lcd.write_string('\r\n')

def loop_string(string, lcd, framebuffer, row, num_cols, delay=0.3):
    padding = ' ' * num_cols
    s = padding + string + padding
    for i in range(len(s) - num_cols + 1):
        framebuffer[row] = s[i:i + num_cols]
        write_to_lcd(lcd, framebuffer, num_cols)
        time.sleep(delay)

### Coin Acceptor variables.
newCoin = False
pulseCount = 0
lastPulseTime = 0
interval = 0
# ?
max_impulse = 10
denomination = 5
coinType = 0

GPIO.setmode(GPIO.BCM)
COIN_PIN=16
GPIO.setup(COIN_PIN,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def millis():
    return round(time.time() * 1000)

def coinEventHandler(pin):
    global lastPulseTime
    global pulseCount
    global newCoin

    time.sleep(0.001)

    if (GPIO.input(COIN_PIN) == 1):
        newCoin = True; 
        pulseCount += 1
        lastPulseTime = millis();
    else:
        print("glitch")


def displayCoinData():
    global coinType
    global pulseCount

    print("interval = %s" % interval)
    print("pulse count = %s" % pulseCount)
    print("Do what ever you want. Inserted Money = %s" % coinType)
    lcd.clear()
    lcd.write_string("Coin type = %s" % coinType)
    # remove if you want to save Coins and print sum of inserted coins
    coinType = 0
    pulseCount = 0


GPIO.add_event_detect(COIN_PIN,GPIO.RISING,callback=coinEventHandler)

try:
    print('Press Ctrl-C to Stop... ')
    while True:
        while (newCoin is True):
            #interval from first and last impulse
            nowTime = millis()
            interval = nowTime - lastPulseTime  

            # Max_impulse will avoid any extra impulses for any reason.
            # This is the reason why I recommended to you use 1 2 4 5 10 20 Impulses instead of 3 7 9 etc...
            if ( interval > 200 and pulseCount > 0):
                coinType = pulseCount * denomination
                newCoin = False
                displayCoinData()

except KeyboardInterrupt:
    print('Close the code.')
finally:
    GPIO.cleanup()
    lcd.clear()

