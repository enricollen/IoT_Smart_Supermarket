from COAP.COAP_Model import COAPModel
import logging
from DatabaseConnection import DatabaseConnection

import datetime

REFILL_RESOURCE_PATH = "refill"
IS_OBSERVABLE = True

LAST_REFILL_JSON_KEY = "last_refill_ts"
ID_KEY = "id"
NOW_KEY = "now"

from COAP.const import CYAN_STYLE, NO_CHANGE

NAME_STYLE = CYAN_STYLE

class RefillSensor(COAPModel):
    
    last_refill = -1
    node_id = ""
    node_ts_in_seconds = -1
    last_refill_in_seconds = -1

    def __init__(self, ip_addr):
        self.resource_path = REFILL_RESOURCE_PATH
        self.observable = IS_OBSERVABLE
        self.name_style = NAME_STYLE
        super().__init__(ip_addr)

    def update_state_from_json(self, json):
        no_change = False
        try:
            if (self.last_refill_in_seconds == json[LAST_REFILL_JSON_KEY] and \
                self.node_id == json[ID_KEY] and \
                self.node_ts_in_seconds == json[NOW_KEY]):
                    no_change = True

            self.last_refill_in_seconds = json[LAST_REFILL_JSON_KEY]
            self.node_id = json[ID_KEY]
            self.node_ts_in_seconds = json[NOW_KEY]
        except:
            logging.warning("unable to parse state from json")
            return False
        
        last_refill_offset = self.node_ts_in_seconds - self.last_refill_in_seconds
        self.last_refill = datetime.datetime.now() - datetime.timedelta(seconds=last_refill_offset)
        if no_change:
            return NO_CHANGE
        else:
            return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO last_refill(node_id, timestamp, last_refill_ts) VALUES(%s, NOW(), %s)"
        params = (self.node_id, self.last_refill)
        conn.cursor.execute(sql, params)
        conn.dbConn.commit()


"""
TABLE NAME: last_refill

+------------+----------+----------+----------------+
|     ID     | node_id  |  now()   | last_refill_ts |
+------------+----------+----------+----------------+

CREATE TABLE `last_refill` (
   `ID` int(11) NOT NULL AUTO_INCREMENT,
   `node_id` varchar(50) NOT NULL,
   `timestamp` timestamp NULL DEFAULT current_timestamp(),
   `last_refill_ts` timestamp NOT NULL DEFAULT current_timestamp(),
      PRIMARY KEY (`ID`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

"""