from COAPModel import COAPModel
import logging
from DatabaseConnection import DatabaseConnection
#from datetime import datetime

PRICE_RESOURCE_PATH = "price"
IS_OBSERVABLE = True

PRICE_KEY = "price"
LAST_CHANGE_TS_KEY = "last_change_ts"

DEFAULT_PRICE = 10.0

class PriceDisplay(COAPModel):
    
    current_price = DEFAULT_PRICE
    last_price_change = -1

    #last_update = 0

    def __init__(self):
        self.resource_path = PRICE_RESOURCE_PATH
        self.is_observable = IS_OBSERVABLE
        super().__init__()

    def update_state_from_json(self, json):
        try:
            self.current_price = json[PRICE_KEY]
            self.last_price_change = json[LAST_CHANGE_TS_KEY]
        except:
            logging.warning("unable to parse state from json")
            return False

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

"""
TABLE NAME: price_display_state

+----------+----------+--------------+-------------+
|   ID     |  now()   | curent_price | last_change |
+----------+----------+--------------+-------------+

"""