from COAPModel import COAPModel
import logging
from DatabaseConnection import DatabaseConnection

REFILL_RESOURCE_PATH = "refill"
IS_OBSERVABLE = True

LAST_REFILL_JSON_KEY = "last_refill_ts"

class RefillSensor(COAPModel):
    
    last_refill = -1    

    def __init__(self, ip_addr):
        self.resource_path = REFILL_RESOURCE_PATH
        self.is_observable = IS_OBSERVABLE
        super().__init__(ip_addr)

    def update_state_from_json(self, json):
        try:
            self.last_refill = json[LAST_REFILL_JSON_KEY]
        except:
            logging.warning("unable to parse state from json")
            return False

        return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO last_refill(node_id, timestamp, last_refill_ts) VALUES(%s, NOW(), %s)"
        params = (self.id, self.last_refill)
        conn.cursor.execute(sql, params)