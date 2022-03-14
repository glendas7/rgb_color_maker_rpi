from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
from gpiozero import RGBLED, Button
from colorzero import Color
from ADCDevice import *
import firebase_setup
from firebase_admin import firestore
import constant
 
db = firestore.client()
collection = firebase_setup.db.collection(constant.COLLECTION_NAME)
doc_rgb_ref = collection.document(constant.RGB_DATA)
doc_color_ref = collection.document(constant.COLOR_DATA)
doc_button_ref = collection.document(constant.BUTTON_DATA)

doc_rgb_ref.update({u'rgbVal': "rgb(0,0,0)"})
doc_button_ref.update({u'redBtn': False})
doc_button_ref.update({u'greenBtn': False})
doc_button_ref.update({u'blueBtn': False})

rgb_val = "0"
led = RGBLED(19, 13, 6)
potA = ADCDevice()
potA = ADS7830()

rButton = Button(16) 
gButton = Button(20)
bButton = Button(21)
buttons = [rButton, gButton, bButton]
colors = ["redVal", "greenVal", "blueVal"]
activeButton = rButton
led.color = Color('red')

def setColor(value):
    for btn, color in zip(buttons, colors):
        if activeButton == btn:
            if value > 255:
                value = 255
            doc_color_ref.update({color:value})
            
def on_rgbdoc_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        global rgb_val
        rgb_val = doc.to_dict()["rgbVal"]
        lcd.clear()

doc_rgb_watch = doc_rgb_ref.on_snapshot(on_rgbdoc_snapshot)

def red_pressed():
    doc_button_ref.update({u'redBtn': True})
    doc_button_ref.update({u'greenBtn': False})
    doc_button_ref.update({u'blueBtn': False})
    global activeButton
    activeButton = rButton
    led.color = Color('red')
def green_pressed():
    doc_button_ref.update({u'redBtn': False})
    doc_button_ref.update({u'greenBtn': True})
    doc_button_ref.update({u'blueBtn': False})
    global activeButton
    activeButton = gButton
    led.color = Color('green')
    
def blue_pressed():
    doc_button_ref.update({u'redBtn': False})
    doc_button_ref.update({u'greenBtn': False})
    doc_button_ref.update({u'blueBtn': True})
    global activeButton
    activeButton = bButton
    led.color = Color('blue') 
    
rButton.when_pressed = red_pressed
gButton.when_pressed = green_pressed
bButton.when_pressed = blue_pressed
    
PCF8574_address = 0x27
PCF8574A_address = 0x3F
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Address Error !')
        exit(1)

lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        mcp.output(3,1)
        lcd.begin(16,2)
        while True:
            lcd.clear()
            lcd.setCursor(0,0)
            lcd.message( rgb_val + '\n' )
            valueA = potA.analogRead(0)
            setColor(valueA)
            print(valueA)
    except KeyboardInterrupt:
        lcd.clear()

