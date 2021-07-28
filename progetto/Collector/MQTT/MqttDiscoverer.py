import json

import logging
logger = logging.getLogger("MqttDiscoverer")
logger.setLevel(level=logging.DEBUG)

from COAP.const import bold, italic, ALREADY_REGISTERED, REGISTRATION_SUCCESSFULL, INTERNAL_ERROR, WRONG_PAYLOAD

from MQTT.MqttClient import MqttClient
from Collector import collector

DISCOVERY_TOPIC = "discovery"

ID_KEY = "id"
KIND_KEY="kind"

class MQTTDiscoverer(MqttClient):

    def __init__(self, sub_topics):

        self.DEFAULT_SUB_TOPIC = DISCOVERY_TOPIC

        super().__init__(sub_topics=sub_topics)

    def on_message(self, client, userdata, msg):
        
        options = {
        "FridgeTemperature" : collector.register_new_fridge_temp_sensor
        }
    
        try:
            message = json.loads(msg.payload)
            node_id = message[ID_KEY]
            kind = message[KIND_KEY]
        except:
            logger.error("Unable to parse JSON in discovery | msg = " + str(msg.payload))

        if node_id in collector.connected_node_id_list():
            outcome = ALREADY_REGISTERED
        else:
            if(kind in options):
                success = options[kind](node_id)   #instantiates the nodes' model
                if( success == False):
                    outcome = INTERNAL_ERROR
                    logger.debug("INTERNAL_ERROR: request.payload = " + str(msg.payload))

                elif(success == ALREADY_REGISTERED):
                    outcome = ALREADY_REGISTERED
                    logger.info("discovered already known device")
                else:
                    logger.info("New registration for: " + node_id + " | kind: " + kind)
                    outcome = REGISTRATION_SUCCESSFULL

            else:
                logger.debug("discovered unrecognized device: " + str(msg.payload))
                outcome = WRONG_PAYLOAD
                
        logger.info("["+ bold("discoverer") + "]: registration request from [" +bold( str(node_id) ) + "] | outcome: " + italic(outcome))
        
        return