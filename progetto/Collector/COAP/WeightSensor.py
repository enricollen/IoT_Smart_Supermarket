from COAP.COAP_Model import COAPModel
import logging
logger = logging.getLogger("COAPModule")

from DatabaseConnection import DatabaseConnection

WEIGHT_RESOURCE_PATH = "weight"
IS_OBSERVABLE = True

WEIGHT_KEY = "weight"
ID_KEY = "id"

from COAP.const import GREEN_STYLE
NAME_STYLE = GREEN_STYLE

DEFAULT_WEIGHT = 2000

class WeightSensor(COAPModel):
    
    current_weight = DEFAULT_WEIGHT
    

    def __init__(self, ip_addr):
        self.resource_path = WEIGHT_RESOURCE_PATH
        self.observable = IS_OBSERVABLE
        self.name_style = NAME_STYLE
        super().__init__(ip_addr)

    def update_state_from_json(self, json):
        try:
            self.current_weight = json[WEIGHT_KEY]
        except:
            logger.warning("unable to parse state from json")
            return False

        return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO weight_sensor_state(node_id, timestamp, current_weight) VALUES(%s, NOW(), %s)"
        params = (self.id, self.current_price)
        conn.cursor.execute(sql, params)


"""
TABLE NAME: weight_sensor_state

+----------+-----------+-------------+----------------+
|    ID    |  node_id  |  timestamp  | current_weight | 
+----------+-----------+-------------+----------------+

"""