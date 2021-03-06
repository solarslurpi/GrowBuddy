import board
import busio
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import ssl
from adafruit_as7341 import AS7341, Gain
import json
from secrets import secrets

_READING_MADE_IT = "PAR/READING_OK"
_TAKE_READING = "PAR/READING_TAKE"
_SEND_READING = "PAR/READING_SAVE"

class PAR:
    def __init__(self):

        i2c = busio.I2C(board.SCL1,board.SDA1)  # uses board.SCL and board.SDA
        self.sensor = AS7341(i2c)
        # THe gain, atime, astep are set to map to the discussion in the docs.
        self.sensor.gain = Gain.GAIN_4X
        self.atime = 59
        self.astep = 599
        self.bConnected = False
    def _on_disconnect_mqtt(self,mqtt_clientclient, userdata,rc=0):
        print("DisConnected result code "+str(rc))

    def _on_connect_mqtt(self,mqtt_client, userdata, flags, rc):
        # This function will be called when the mqtt_client is connected
        # successfully to the broker.

        # Subscribe to topics.
        # Freezes pretty quick when receive a message that the reading made it...hmm...
        # self.mqtt_client.subscribe(_READING_MADE_IT)
        self.mqtt_client.subscribe(_TAKE_READING)
        self.bConnected = True
        print("Connected to MQTT Broker!")
        print("Flags: {0}\n RC: {1}".format(flags, rc))

    def _on_message_mqtt(self,mqtt_client,topic,message):
        self.mqtt_client.loop()
        print("New message on topic {0}: {1}".format(topic, message))
        # We've been asked to take a reading by an mqtt client.  This allows any
        # device to take a reading if they have an mqtt client.
        if topic == _TAKE_READING:
            channel_samples = self.take_reading()
            PPFD = int(message)
            channel_samples.insert(0,PPFD)
            print(channel_samples)
            self.send_reading(channel_samples)

    def _connect_wifi(self):
        """      Internal function to connect to home's wifi.
        """
        # connect to wifi
        print("Connecting to %s"%secrets["ssid"])
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        print("Connected to %s!"%secrets["ssid"])

    def _connect_mqtt(self):
        """Connect to the mqtt broker.
        """
        # Create a socket pool
        pool = socketpool.SocketPool(wifi.radio)
        # connect to mqtt broker
        self.mqtt_client = MQTT.MQTT(
            broker=secrets["broker"],
            port=secrets["port"],
            socket_pool=pool,
            ssl_context=ssl.create_default_context(),
            )
        # Connect callback handlers to mqtt_client
        self.mqtt_client.on_connect = self._on_connect_mqtt
        # Freezes pretty quickly if receive messages...
        self.mqtt_client.on_message = self._on_message_mqtt
        self.mqtt_client.on_disconnect = self._on_disconnect_mqtt
        print("Attempting to connect to %s" % self.mqtt_client.broker)
        self.mqtt_client.connect()
        self.mqtt_client.loop()


    def connect(self,callback_function=None):
        """Setup and connect to wifi and mqtt.

        Args:
            callback_function (ptr to function): function passed in by caller
            that will be called after the connect method has completed.
        """
        self._connect_wifi()
        self._connect_mqtt()
        print("connected to wifi and mqtt")
        if (callback_function is not None):
            callback_function(self.mqtt_client)


    def take_reading(self):
        """Take a reading from the AS7341 8 visible channels using Adafruit's
           as7341 CP library.

        Returns:
            list: 8 entries...
            [0] = Count of photons in the 415nm range
            [1] = 445nm range
            [2] = 480nm
            [3] = 515nm
            [4] = 555
            [5] = 590
            [6] = 630
            [7] = 680
        """
        sensor_channels = self.sensor.all_channels
        return [ sensor_channels[i] for i in range(8)]

    def send_reading(self,reading):
        """Send the reading to the growbuddy Rasp Pi server to be saved in a csv file.

        Args:
            reading (list): List of 9 readings.  The first reading is the PPFD value recorded from the
            mq-500 PAR meter.  The 8 readings are measurements in the PAR light spectrum from the AS7341
            callback_function (ptr to a fucntion): [description]

        Raises:
            Exception: If it is detected that there is no connection to the mqtt broker.
        """
        if (not self.bConnected):
            raise Exception("Please connect first")
        # Convert to Json formatted string to make it easy for the nodered node to
        # convert into Json on it's end.
        readingJson = json.dumps(reading)
        # Send the reading.
        self.mqtt_client.loop()
        self.mqtt_client.publish(_SEND_READING,readingJson)

        print("reading sent!")