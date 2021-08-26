import datetime
import json

from MQTT.MqttClient import MqttClient

from Node import Node

from DatabaseConnection import DatabaseConnection

import logging
logger = logging.getLogger("COAPModule")

from COAP.const import NO_CHANGE, bold, FRIDGE_TEMPERATURE_SENSOR

CURRENT_TEMP_KEY = "temperature"
DESIRED_TEMP_KEY = "desired_temp"
NOW_KEY = "timestamp"

DEFAULT_DESIRED_TEMP = 0.0

class FridgeTempSensor(MqttClient, Node):

    node_id = ""
    pub_topic = ""

    node_ts_in_seconds = -1
    current_temp = ""
    desired_temp = DEFAULT_DESIRED_TEMP

    kind = FRIDGE_TEMPERATURE_SENSOR

    def __init__(self, node_id):
        self.node_id = node_id
        sub_topic = "fridge/" + self.node_id + "/temperature"
        self.pub_topic = "fridge/"+ self.node_id + "/desired_temp"
        super().__init__(sub_topic)
        Node.__init__(self)

    def change_setpoint(self, new_setpoint):
        #TO DO:
        #should publish a message on self.pub_topic in the appropriate format

        #remember to call self.update_last_seen() if everything works
        pass

    def on_message(self, client, userdata, msg):
        #TESTed:
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
            if (self.current_temp == json[CURRENT_TEMP_KEY] and
                self.node_ts_in_seconds == json[NOW_KEY] and
                self.desired_temp == json[DESIRED_TEMP_KEY]):
                no_change = True

            self.current_temp = json[CURRENT_TEMP_KEY]
            self.desired_temp = json[DESIRED_TEMP_KEY]
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
        sql = "INSERT INTO fridge_temperatures(node_id, timestamp, node_ts_in_seconds, temperature, desired_temp) VALUES(%s, NOW(), %s, %s, %s)"
        params = (self.node_id, self.node_ts_in_seconds, self.current_temp, self.desired_temp)
        conn.cursor.execute(sql, params)
        conn.dbConn.commit()

    
    def set_new_temp(self, new_temp):
        ret = self.publish(new_temp, self.pub_topic)
        return ret


"""
TABLE NAME: fridge_temperatures

+------------+----------+----------+--------------------+-------------------+-------------------+
|     ID     | node_id  |  now()   | node_ts_in_seconds |    temperature    |   desired_temp    |
+------------+----------+----------+--------------------+-------------------+-------------------+

DROP TABLE IF EXISTS `fridge_temperatures`;

CREATE TABLE `fridge_temperatures` (
  `ID` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `node_id` varchar(50) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `node_ts_in_seconds` INT NOT NULL COMMENT 'seconds since last node restart',
  `temperature` float NOT NULL,
  `desired_temp` float NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=277 DEFAULT CHARSET=utf8mb4;

"""