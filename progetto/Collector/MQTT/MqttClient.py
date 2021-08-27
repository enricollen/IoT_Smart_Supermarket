from datetime import datetime
import paho.mqtt.client as mqtt

from abc import ABC, abstractmethod

import logging
logger = logging.getLogger("MqttClient")
logger.setLevel(level=logging.DEBUG)

from COAP.const import CYAN_STYLE, DEFAULT_STYLE

import Node

BROKER_ADDRESS = "127.0.0.1"
BROKER_PORT = 1883

DEFAULT_SUB_TOPIC = "fenom"

class MqttClient:
    client = 0
    sub_topic_array = []
    DEFAULT_SUB_TOPIC = DEFAULT_SUB_TOPIC
    name_style = CYAN_STYLE
    last_publish_ack = None

    def __init__(self, sub_topics = []):    #sub_topics can be a list or a string of a single topic

        logger.info("Starting mqtt client " + self.__class__.__name__)

        if(isinstance(sub_topics, list)):
            self.sub_topic_array += sub_topics
        else:
            self.sub_topic_array.append(sub_topics)

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish 
        
        connected = False

        global BROKER_ADDRESS


        while(not connected):
            try:
                self.client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
            except:
                ALTERNATIVE_BROKER = "192.168.1.137"
                logger.warning("Cannot connect to broker " + BROKER_ADDRESS + " | trying with " + ALTERNATIVE_BROKER)
                BROKER_ADDRESS = ALTERNATIVE_BROKER
            else:
                connected = True
                logger.info("Connecting to broker " + BROKER_ADDRESS)
        
        self.client.loop_start()    #instantiate a thread for this MqttClient instance

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        logger.debug("Connected with result code " + str(rc) )
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        if(len(self.sub_topic_array)):
            topics = ""
            for sub_topic in self.sub_topic_array:
                client.subscribe(sub_topic)
                topics += sub_topic + " | "
            
            logger.debug("Subscribed to " + topics + "\t len(self.sub_topic_array) = " + str(len(self.sub_topic_array)))
        else:
            logger.debug("Subscribing to default topic '" + self.DEFAULT_SUB_TOPIC +"'")
            client.subscribe(self.DEFAULT_SUB_TOPIC)

    def publish(self, payload, topic):
        ret = self.client.publish(topic,payload)
        return ret

    def on_publish(self, client,userdata,mid):             #create function for callback
        logger.debug("[on_publish]: just received ack for mid="+str(mid))
        self.last_publish_ack = datetime.now()

    @abstractmethod
    def on_message(self, client, userdata, msg):
        """
        print(msg.topic+" "+str(msg.payload))
         options = {
            "FridgeTemperature" : collector.register_new_fridge_temp_sensor,
            "FOOBAR" : collector.register_new_scale_device
            }
         ip = client.ip
         node_id = get_id(msg.topic)
         kind = get_kind(msg.topic)
         """

    def delete(self):
        self.close()

    def close(self):
        if( isinstance(self.client, mqtt.Client)):
            logger.info("["+self.__class__.__name__+"]"+"Stopping mqtt.Client instance self.client")
            try:
                self.client.loop_stop()
            except Exception as e:
                logger.critical("Could not stop self.client in MqttClient")
                print(e)
            else:
                del self.client
                logger.info("["+self.__class__.__name__+"]"+"stopped mqtt.Client instance self.client")
        
        if( isinstance(self, Node.Node)):
            self.delete_thread()
        del self
        return

    def __del__(self):
        self.close()

    #---------------------------------------------
    def class_style(self, string):
        return self.name_style + string + DEFAULT_STYLE