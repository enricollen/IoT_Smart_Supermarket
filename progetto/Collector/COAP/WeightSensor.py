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

    number_of_weight_changes = 0
    
    def update_last_seen():
        logger.error("ATTENTION! WeightSensor->update_last_seen method not initialized!")
        return

    def price_variation_handler():
        logger.error("ATTENTION! WeightSensor->price_variation_handler method not initialized!")
        return

    def __init__(self, ip_addr, update_last_seen_callback, price_variation_handler):
        self.resource_path = WEIGHT_RESOURCE_PATH
        self.observable = IS_OBSERVABLE
        self.name_style = NAME_STYLE
        self.update_last_seen = update_last_seen_callback
        self.price_variation_handler = price_variation_handler
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

    def new_message_from_the_node(self):
    #we redefine the method that is invoked each time that the weight changes
        #here we should also call update_last_seen on the wrapper class of this resource (ScaleDevice):
        self.update_last_seen()
        #we can bind here a callback that will count the number of changes and eventually trigger the price change
        self.number_of_weight_changes = self.number_of_weight_changes + 1
        #here we should call another callback (maybe a method of ShelfScale) that will check the number of refills, the number of weight_changes and eventually change the price (using another callback received from the collector)
        self.price_variation_handler()


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