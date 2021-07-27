from COAP.COAP_Model import COAPModel
import logging
from DatabaseConnection import DatabaseConnection

import datetime

REFILL_RESOURCE_PATH = "refill"
IS_OBSERVABLE = True

LAST_REFILL_JSON_KEY = "last_refill_ts"
ID_KEY = "id"
NOW_KEY = "now"

from COAP.const import CYAN_STYLE

NAME_STYLE = CYAN_STYLE

class RefillSensor(COAPModel):
    
    last_refill = -1    

    def __init__(self, ip_addr):
        self.resource_path = REFILL_RESOURCE_PATH
        self.observable = IS_OBSERVABLE
        self.name_style = NAME_STYLE
        super().__init__(ip_addr)

    def update_state_from_json(self, json):
        try:
            self.last_refill_in_seconds = json[LAST_REFILL_JSON_KEY]
            self.id = json[ID_KEY]
            self.node_ts_in_seconds = json[NOW_KEY]
        except:
            logging.warning("unable to parse state from json")
            return False
        
        last_refill_offset = self.node_ts_in_seconds - self.last_refill_in_seconds
        self.last_refill = datetime.datetime.now() - datetime.timedelta(seconds=last_refill_offset)
        return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO last_refill(node_id, timestamp, last_refill_ts) VALUES(%s, NOW(), %s)"
        params = (self.id, self.last_refill)
        conn.cursor.execute(sql, params)
        conn.dbConn.commit()


"""
TABLE NAME: last_refill

+------------+----------+----------+----------------+
|     ID     | node_id  |  now()   | last_refill_ts |
+------------+----------+----------+----------------+

"""