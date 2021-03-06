import board
import digitalio
import time
from adafruit_debouncer import Debouncer
from PAR_LIB import PAR
import neopixel

(NOT_CONNECTED,CONNECTED) = range(2)

def button_setup():
    pin = digitalio.DigitalInOut(board.D0) # Button pin on QT PY ESP32 S2
    pin.pull = digitalio.Pull.UP
    return Debouncer(pin)

def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

def connect_callback():
    print("connect_callback")
    global state
    state = CONNECTED
    pixels.fill((0, 0, 255))
    time.sleep(1)
    pixels.fill((0, 0, 0))
    #time.sleep(0.5)
def reading_received_callback():
    print("reading received")
    pixels.fill((0, 255, 0))
    time.sleep(1)
    pixels.fill((0, 0, 0))

# We're starting out.  The first thing we need to do is connect to wifi and the
# mqtt broker.  We use the global state variable to track where we are.
state = NOT_CONNECTED
button = button_setup()
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
p = PAR()
p.connect(connect_callback)
# Once connected, the state will be CONNECTED, since this was set in the callback.
print("waiting for button press to collect a sample.")
while True:
    time.sleep(0.1)
    if (state == CONNECTED):
        # If the button is pressed, collect a sample_rate
        button.update()
        if button.rose:
            print("button pressed!")
            channel_samples = p.take_reading()
            pixels.fill((255, 255, 0))
            time.sleep(1)
            pixels.fill((0, 0, 0))
            p.send_reading(channel_samples,reading_received_callback)

