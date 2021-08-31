import datetime
import json

import MQTT.FridgeTempSensor
from MQTT.MqttClient import MqttClient

from Node import Node

from DatabaseConnection import DatabaseConnection

import logging
logger = logging.getLogger("MQTTModule")
logger.setLevel(level=logging.DEBUG)

from COAP.const import NO_CHANGE, YELLOW_STYLE, bold, FRIDGE_ALARM_LIGHT

NAME_STYLE = YELLOW_STYLE

CURRENT_ALARM_STATE_KEY = "alarm_state"
NOW_KEY = "timestamp"

RECOGNISED_COMMANDS = ["ON", "OFF"]


class FridgeAlarmLight(MqttClient, Node):

    node_id = ""
    pub_topic = ""

    node_ts_in_seconds = -1
    current_alarm_state = ""
    last_alarm_state_change = 0

    linked_fridge_temp_sensor = None

    kind = FRIDGE_ALARM_LIGHT

    def __init__(self, node_id):
        self.node_id = node_id
        self.name_style = NAME_STYLE
        sub_topic = "alarm/" + self.node_id + "/state"
        self.pub_topic = "alarm/"+ self.node_id + "/actuator-cmd"
        super().__init__(sub_topic)
        Node.__init__(self)

    def change_state(self, new_state):
        #DONE:
        #should publish a message on self.pub_topic in the appropriate format
        if new_state not in RECOGNISED_COMMANDS:
            logger.warning("[change_state]: received unrecognised command '" + new_state + "' for the node " + self.node_id)
            return False
    
        if(self.current_alarm_state == new_state):
            logger.warning("[change_state]: no change command '" + new_state + "' for the node " + self.node_id)
            return True
    
        ret = self.publish(new_state, self.pub_topic)
        return ret

    def toggle_state(self):
        if(self.current_alarm_state == "ON"):
            new_state = "OFF"
        else:
            new_state = "ON"

        return self.change_state(new_state)

    def on_message(self, client, userdata, msg):
        #parse state from json and update class state,
        #it also save the received state in the database
        if(msg.payload == None):
            logger.warning("["+ self.__class__.__name__ + ".on_message]: Received empty MQTT message from " + self.node_id)
            return False
        
        try:
            json_parsed = json.loads(msg.payload)
        except:
            logger.error("["+ self.__class__.__name__ + ".on_message]: Cannot parse json from MQTT message")
            return False
        
        try:
            ret = self.update_state_from_json(json_parsed)

        except Exception as e:
            logger.critical("exception during update_state_from_json | json = " + str(msg.payload))
            raise(e)
        
        if ret == NO_CHANGE:
            logger.info("[" + self.node_id +"]["+ self.class_style(self.__class__.__name__ + ".parse_state_response") + "]: no change")
            #--------------------------
            self.update_last_seen()
            #--------------------------
            return self
        elif ret == False:
            logger.warning("[" + self.node_id +"]["+ self.class_style(self.__class__.__name__ + ".parse_state_response") + "]: cannot parse state from json! | " + bold( str(msg.payload) ) )
            return False
        elif ret:
            self.save_current_state()
            logger.info("[" + self.node_id +"]["+ self.class_style(self.__class__.__name__ + ".parse_state_response") + "]: new node state set: " + bold( str(msg.payload) ) )
            #--------------------------
            self.update_last_seen()
            #--------------------------
            return self

        return

    def update_state_from_json(self, json):
        no_change = False

        try:
            #here we try to parse the excepted values from json object. If something is missing, we should raise an error
            if (self.node_ts_in_seconds == json[NOW_KEY] and
                self.current_alarm_state == json[CURRENT_ALARM_STATE_KEY]):
                no_change = True

            if(self.current_alarm_state != json[CURRENT_ALARM_STATE_KEY]):
                self.last_alarm_state_change = datetime.datetime.now()

            self.current_alarm_state = json[CURRENT_ALARM_STATE_KEY]
            self.node_ts_in_seconds = json[NOW_KEY]
        
        except:
            logger.warning("unable to parse state from json")
            return False

        if no_change:
            return NO_CHANGE
        else:
            return self


    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO fridge_alarm_light(node_id, timestamp, node_ts_in_seconds, state, last_state_change) VALUES(%s, NOW(), %s, %s, %s)"
        params = (self.node_id, self.node_ts_in_seconds, self.current_alarm_state, self.last_alarm_state_change)
        conn.cursor.execute(sql, params)
        conn.dbConn.commit()

    def bind_fridge_temp_sensor(self, fridge_temp_sensor):
        if(self.linked_fridge_temp_sensor!=None):
            logger.warning("[FridgeAlarmLight: bind_fridge_temp_sensor] FridgeAlarmLight has already been associated with FridgeTempSensor")
            return False

        assert isinstance(fridge_temp_sensor, MQTT.FridgeTempSensor.FridgeTempSensor)

        self.linked_fridge_temp_sensor = fridge_temp_sensor

    def unbind_coupled_device(self):
        if(self.linked_fridge_temp_sensor):
            del self.linked_fridge_temp_sensor
        return

    def delete(self):
        self.unbind_coupled_device()
        self.delete_thread()
        self.close()

"""
TABLE NAME: fridge_alarm_light

+------------+----------+----------+--------------------+-------------------+-------------------+
|     ID     | node_id  |  now()   | node_ts_in_seconds |    state          | last_state_change |
+------------+----------+----------+--------------------+-------------------+-------------------+

DROP TABLE IF EXISTS `fridge_alarm_light`;

CREATE TABLE `fridge_alarm_light` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `node_id` varchar(50) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `node_ts_in_seconds` INT NOT NULL COMMENT 'seconds since last node restart',
  `state` VARCHAR(5) NOT NULL,
  `last_state_change` timestamp,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=277 DEFAULT CHARSET=utf8mb4;

"""