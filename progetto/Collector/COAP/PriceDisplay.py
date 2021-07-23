from COAP.COAP_Model import COAPModel
import logging
from DatabaseConnection import DatabaseConnection

import datetime

logger = logging.getLogger("COAPModule")

PRICE_RESOURCE_PATH = "price"
IS_OBSERVABLE = True

PRICE_KEY = "price"
LAST_CHANGE_TS_KEY = "last_change_ts"
NODE_ID_KEY = "id"
NOW_KEY = "now"

DEFAULT_PRICE = 10.0
PRICE_NEVER_CHANGED = -1

class PriceDisplay(COAPModel):
    
    current_price = DEFAULT_PRICE
    last_price_change = -1
    linked_scale_device = ""


    def __init__(self, ip_addr):
        self.resource_path = PRICE_RESOURCE_PATH
        self.is_observable = IS_OBSERVABLE
        super().__init__(ip_addr)

    def update_state_from_json(self, json):
        try:
            self.current_price = json[PRICE_KEY]
            self.node_ts_in_seconds = json[NOW_KEY]
            self.last_price_change_in_seconds = json[LAST_CHANGE_TS_KEY]
            self.id = json[NODE_ID_KEY]
        except:
            logger.warning("unable to parse state from json")
            return False
        if self.last_price_change_in_seconds != PRICE_NEVER_CHANGED:
            last_change_offset = self.node_ts_in_seconds - self.last_price_change_in_seconds
            self.last_price_change = datetime.datetime.now() - datetime.timedelta(seconds=last_change_offset)
        else:
            self.last_price_change = None   #TO DO: check if it is dangerous for the insert in db
        #self.last_update = datetime.now()

        return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO price_display_state(node_id, timestamp, current_price, last_price_change) VALUES(%s, NOW(), %s, %s)"
        params = (self.id, self.current_price, self.last_price_change)
        conn.cursor.execute(sql, params)

    def set_new_values(self):
        #TO DO...
        return self
    
    def bind_scale_device(self, scale_ip):
        if(self.linked_scale_device!=""):
            logger.warning("[PriceDisplay: bind_scale_device] Price Display has already been associated with Scale Sensor")
            return False

        self.linked_scale_device = scale_ip

"""
TABLE NAME: price_display_state

+------------+----------+----------+--------------+-------------------+
|     ID     | node_id  |  now()   | curent_price | last_price_change |
+------------+----------+----------+--------------+-------------------+

"""