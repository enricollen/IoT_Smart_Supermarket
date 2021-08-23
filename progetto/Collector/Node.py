from threading import Timer
import datetime

from MQTT.MqttClient import MqttClient
import COAP.COAP_Model

import Collector

import logging
default_logger = logging.getLogger()
default_logger.setLevel(level=logging.CRITICAL)
logger = logging.getLogger("Node_Class")
logger.setLevel(level=logging.DEBUG)


CHECK_PRESENCE_INTERVAL = 100 #in seconds

class Node:
    node_id = False
    kind = "UNDEFINED KIND"
    last_seen = None

    thread = False

    def __init__(self):
        self.update_last_seen()
        return

    def update_last_seen(self):
        self.last_seen = datetime.datetime.now()
        self.reset_timer_presence_checker_thread()
        return True

    def check_presence(self):
        logger.debug("Checking if the node " + str(self.node_id) + " | kind: " + self.kind + " is still present")
        if self.is_mqtt_node():
            logger.debug("MQTT node timed out!")
            self.prompt_the_collector_to_delete_this()
        elif issubclass(self.__class__, COAP.COAP_Model.COAPModel):
            #if it is CoAP node
            #we should make a GET request and check if we receive a response,
            #in case we receive nothing, the node should be deleted!
            outcome = self.get_current_state()
            if outcome:
                self.update_last_seen()
            else:
                self.prompt_the_collector_to_delete_this()
        elif self.is_multi_resources_node():
            outcome = self.get_resources_state()
            if outcome:
                self.update_last_seen()
            else:
                self.prompt_the_collector_to_delete_this()
        else:
            logger.warning("[check presence]: unhandled kind of node!")


        return

    def is_multi_resources_node(self):
        return False

    def is_mqtt_node(self):
        if issubclass(self.__class__, MqttClient):
            return True
        else:
            return False

    def prompt_the_collector_to_delete_this(self):
        #TO DO:
        #a proper collector method to delete the node from the connected node list to be called from here
        Collector.collector.remove_node(self.node_id)
        return

    #--------------------------------------------------------------------

    def create_presence_checker_thread(self):
        self.thread = Timer(CHECK_PRESENCE_INTERVAL, self.check_presence)
        self.thread.start() # TO TEST
        return

    def reset_timer_presence_checker_thread(self):
        if isinstance(self.thread, Timer):
            self.thread.cancel()
        self.create_presence_checker_thread()
        return
    
    def __del__(self):
        if isinstance(self.thread, Timer):
            self.thread.cancel()
        del self.thread