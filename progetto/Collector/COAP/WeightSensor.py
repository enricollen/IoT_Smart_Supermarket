from COAP.COAP_Model import COAPModel
import logging
logger = logging.getLogger("COAPModule")

from DatabaseConnection import DatabaseConnection

WEIGHT_RESOURCE_PATH = "weight"
IS_OBSERVABLE = True

WEIGHT_KEY = "weight"
ID_KEY = "id"
NOW_KEY = "now"

from COAP.const import GREEN_STYLE, NO_CHANGE, CANNOT_PARSE_JSON
NAME_STYLE = GREEN_STYLE

DEFAULT_WEIGHT = 2000

class WeightSensor(COAPModel):
    
    current_weight = DEFAULT_WEIGHT
    node_id = ""
    now_in_seconds = -1
    

    def __init__(self, ip_addr):
        self.resource_path = WEIGHT_RESOURCE_PATH
        self.observable = IS_OBSERVABLE
        self.name_style = NAME_STYLE
        super().__init__(ip_addr)

    def update_state_from_json(self, json):
        no_change = False
        try:
            if(self.current_weight == json[WEIGHT_KEY] and
            self.node_id == json[ID_KEY] and
            self.now_in_seconds == json[NOW_KEY]):
                no_change = True

            self.current_weight = json[WEIGHT_KEY]
            self.node_id = json[ID_KEY]
            self.now_in_seconds = json[NOW_KEY]
        except:
            logger.warning("cannot parse state from json | object: " + self.__class__.__name__)
            return CANNOT_PARSE_JSON
        
        if no_change:
            return NO_CHANGE
        else:
            return self

    def save_current_state(self):
        conn = DatabaseConnection()
        sql = "INSERT INTO weight_sensor_state(node_id, timestamp, current_weight) VALUES(%s, NOW(), %s)"
        params = (self.node_id, self.current_weight)
        conn.cursor.execute(sql, params)
        conn.dbConn.commit()


"""
TABLE NAME: weight_sensor_state

+----------+-----------+-------------+----------------+
|    ID    |  node_id  |  timestamp  | current_weight | 
+----------+-----------+-------------+----------------+

"""