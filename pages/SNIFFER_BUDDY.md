# Sniffer Buddy 
[Back to Top](../README.md)

![Sniffer Buddy](../images/Sniffer_Buddy.JPEG)

An SCD-30 or SCD-40 sensor is attached to an ESP(286 or 32) microcontroller running Tasmota to monitor the CO2, air temperature, and humidity level within an indoor grow tent.  A photoresistor is attached to the top so that __The Director__ can detect when the light goes off and on.  The home's wifi is used to send the readings to __The Director__.
## Current Status
Prototype V2


### Hardware
- [SCD30 sensor from Adafruit](https://www.adafruit.com/product/4867)
- [ESP826 D1 mini](https://i2.wp.com/randomnerdtutorials.com/wp-content/uploads/2019/05/ESP8266-WeMos-D1-Mini-pinout-gpio-pin.png?quality=100&strip=all&ssl=1) I had in my parts bin.
- Photoresistor and 10K resistor for light on/off detection.  I also had these parts in my parts bin.

#### Requires Plug to Run

_Note: I wanted to use a battery to power the Air Sensor.  However, it turns out the ESP286/ESP32 was not designed for battery power. From a Discord chat:_
```
ESP8266 is not suitable for battery operation, unless long deep sleep intervals

Due to the extra battery t[d]rain, probably not too much shorter than 5 minutes
```
With that said, perhaps running on a plug is not a big deal because there will be a need for many devices to be powered within a grow tent.

### Firmware
The Sniffer Buddy uses the Tasmota Sensors build.  This is my first use of Tasmota.  Because I project several of the Buddies will be using Tasmota, I've collected what I have learned [in a separate page focused on Tasmota Learning](../pages/Tasmota_learnings.md)