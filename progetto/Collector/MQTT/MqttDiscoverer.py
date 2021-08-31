import json

import logging
logger = logging.getLogger("MqttDiscoverer")
logger.setLevel(level=logging.DEBUG)

from COAP.const import ADDRESS_ALREADY_IN_USE, FRIDGE_TEMPERATURE_SENSOR, FRIDGE_ALARM_LIGHT, NOT_REGISTERED, bold, italic, ALREADY_REGISTERED, REGISTRATION_SUCCESSFULL, INTERNAL_ERROR, WRONG_PAYLOAD, KIND_NOT_RECOGNISED

from MQTT.MqttClient import MqttClient
from Collector import collector

DISCOVERY_TOPIC = "discovery"

ID_KEY = "id"
KIND_KEY="kind"



#in "discovery" we receive a message:
#    id   = 434334
#    kind = FRIDGE_TEMPERATURE_SENSOR | ...
#depending on id and kind we start another mqttclient that subscribes to the topic of the discovered node


#the MQTTDiscoverer expects to read messages about new nodes connected. The expected syntax is:
# - JSON
# {"id": "xxxx", "kind": "yyyy"}

class MQTTDiscoverer(MqttClient):

    def __init__(self, sub_topics = []):

        self.DEFAULT_SUB_TOPIC = DISCOVERY_TOPIC

        super().__init__(sub_topics=sub_topics)

    def on_message(self, client, userdata, msg):
        
        options = {
        FRIDGE_TEMPERATURE_SENSOR : collector.register_new_fridge_temp_sensor,
        FRIDGE_ALARM_LIGHT        : collector.register_new_fridge_alarm_light
        }

        payload_str = str(msg.payload.decode("utf-8").split('\x00',1)[0])
    
        try:
            message = json.loads(payload_str)
        except Exception as e:
            logger.error("Unable to parse JSON in discovery | msg = " + payload_str + " len(msg) = " + str(len(payload_str)) )
            print(e)
            return

        try:
            node_id = message[ID_KEY]
            kind = message[KIND_KEY]
        except:
            logger.error("Could not parse required keys from received json array = " + message)
            return

        node_connection_status = collector.check_if_already_connected(node_id = node_id, kind = kind, is_mqtt_connection=True)

        if node_connection_status == ALREADY_REGISTERED: #node_id in collector.connected_node_id_list():
            outcome = ALREADY_REGISTERED
        elif node_connection_status == NOT_REGISTERED:
            if(kind in options):
                success = options[kind](node_id)   #instantiates the nodes' model
                if( success == False):
                    outcome = INTERNAL_ERROR
                    logger.debug("INTERNAL_ERROR: request.payload = " + str(msg.payload.decode("utf-8")))

                elif(success == ALREADY_REGISTERED):
                    outcome = ALREADY_REGISTERED
                    logger.info("discovered already known device")
                else:
                    logger.info("New registration for: " + node_id + " | kind: " + kind)
                    outcome = REGISTRATION_SUCCESSFULL

            else:
                logger.debug("discovered unrecognized device: " + str(msg.payload.decode("utf-8")))
                outcome = WRONG_PAYLOAD

        elif node_connection_status == ADDRESS_ALREADY_IN_USE:
            logger.warning("[x] Duplicate mqtt node with same node_id")
            outcome = ADDRESS_ALREADY_IN_USE

        elif node_connection_status:
            outcome = node_connection_status

        else:
            outcome = INTERNAL_ERROR

        if outcome != ALREADY_REGISTERED: 
            logger.info("["+ bold("discoverer") + "]: registration request from [" +bold( str(node_id) ) + "] | outcome: " + italic(outcome))
        
        return