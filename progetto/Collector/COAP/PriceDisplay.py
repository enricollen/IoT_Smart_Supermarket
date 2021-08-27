from Node import Node
from COAP.COAP_Model import COAPModel
import logging
from DatabaseConnection import DatabaseConnection

import datetime

logger = logging.getLogger("COAPModule")

from COAP.const import BLUE_STYLE, PRICE_DISPLAY, NO_CHANGE

PRICE_RESOURCE_PATH = "price"
IS_OBSERVABLE = True

PRICE_KEY = "price"
LAST_CHANGE_TS_KEY = "last_chg"
NODE_ID_KEY = "id"
NOW_KEY = "now"

DEFAULT_PRICE = 10.0
PRICE_NEVER_CHANGED = -1

NAME_STYLE = BLUE_STYLE

class PriceDisplay(COAPModel, Node):
    
    current_price = DEFAULT_PRICE
    last_price_change = -1  #it is a datetime
    linked_scale_device = ""
    initial_price = -1  #we will use that for the price ranges

    kind = PRICE_DISPLAY

    def __init__(self, ip_addr):
        self.resource_path = PRICE_RESOURCE_PATH
        self.observable = IS_OBSERVABLE
        self.name_style = NAME_STYLE
        super().__init__(ip_addr)
        Node.__init__(self)

    def update_state_from_json(self, json):
        no_change = False
        try:

            if self.current_price == json[PRICE_KEY] and \
                    self.node_ts_in_seconds == json[NOW_KEY] and \
                    self.last_price_change_in_seconds == json[LAST_CHANGE_TS_KEY] and \
                    self.node_id == json[NODE_ID_KEY]:
                no_change = True

            #we assert that at the moment of the first connection the current price of the PriceDisplay is the default price (we will use that for the price ranges)
            if self.initial_price == -1:
                self.initial_price = json[PRICE_KEY]

            self.current_price = json[PRICE_KEY]
            self.node_ts_in_seconds = json[NOW_KEY]
            self.last_price_change_in_seconds = json[LAST_CHANGE_TS_KEY]
            self.node_id = json[NODE_ID_KEY]
        except:
            logger.warning("unable to parse state from json")
            return False
        if self.last_price_change_in_seconds != PRICE_NEVER_CHANGED:
            last_change_offset = self.node_ts_in_seconds - self.last_price_change_in_seconds
            self.last_price_change = datetime.datetime.now() - datetime.timedelta(seconds=last_change_offset)
        else:
            self.last_price_change = None   #TO DO: check if it is dangerous for the insert in db
        #self.last_update = datetime.now()
        if no_change:
            return NO_CHANGE
        else:
            return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO price_display_state(node_id, timestamp, current_price, last_price_change) VALUES(%s, NOW(), %s, %s)"
        params = (self.node_id, self.current_price, self.last_price_change)
        conn.cursor.execute(sql, params)
        conn.dbConn.commit()

    def set_new_price(self, new_price):
        
        req_body = 'new_price='+str(new_price)

        ret = self.set_new_values(req_body, use_default_callback=True)

        #so that we update the state of the PriceDisplay object by the collector side
        self.get_current_state()

        return ret
    
    def bind_scale_device(self, scale_obj):
        if(self.linked_scale_device!=""):
            logger.warning("[PriceDisplay: bind_scale_device] Price Display has already been associated with Scale Sensor")
            return False

        self.linked_scale_device = scale_obj

    def delete(self):
        logger.debug("PriceDisplay id " + self.node_id + " beeing deallocated!")
        self.close_coap_connections()
        self.delete_thread()
        

    def __del__(self):
        self.delete()
        

"""
TABLE NAME: price_display_state

+------------+----------+----------+--------------+-------------------+
|     ID     | node_id  |  now()   | curent_price | last_price_change |
+------------+----------+----------+--------------+-------------------+

"""