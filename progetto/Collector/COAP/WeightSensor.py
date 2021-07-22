from COAPModel import COAPModel
import logging
from DatabaseConnection import DatabaseConnection

WEIGHT_RESOURCE_PATH = "weight"
IS_OBSERVABLE = True

WEIGHT_KEY = "weight"

DEFAULT_WEIGHT = 2000

class WeightSensor(COAPModel):
    
    current_weight = DEFAULT_WEIGHT

    def __init__(self):
        self.resource_path = WEIGHT_RESOURCE_PATH
        self.is_observable = IS_OBSERVABLE
        super().__init__()

    def update_state_from_json(self, json):
        try:
            self.current_weight = json[WEIGHT_KEY]
        except:
            logging.warning("unable to parse state from json")
            return False

        return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO weight_sensor_state(node_id, timestamp, current_weight) VALUES(%s, NOW(), %s)"
        params = (self.id, self.current_price)
        conn.cursor.execute(sql, params)

    def set_new_values(self):
        #TO DO...
        return self

"""
TABLE NAME: weight_sensor_state

+----------+----------+---------------+
|   ID     |  now()   | curent_weight | 
+----------+----------+---------------+

"""