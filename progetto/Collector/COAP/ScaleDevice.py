from COAP.PriceDisplay import PriceDisplay
from COAP.WeightSensor import WeightSensor
from COAP.RefillSensor import RefillSensor

import logging
logger = logging.getLogger("COAPModule")

import datetime

from COAP.const import SHELF_SCALE
from Node import Node

class ScaleDevice(Node):
    
    weight_sensor = 0
    refill_sensor = 0   
    linked_price_display = ""   #the obj of the linked price_display
    ip_address = ""
    
    kind = SHELF_SCALE

    def __init__(self, ip_addr):


        def update_last_seen_callback():
            self.update_last_seen()

        self.refill_sensor = RefillSensor(ip_addr)

        self.node_id = self.refill_sensor.node_id   #both the resources share the same node_id
        self.ip_address = ip_addr

        self.weight_sensor = WeightSensor(ip_addr, update_last_seen_callback, self.weight_changes_handler)
        
        super().__init__()

    def weight_changes_handler(self):
        if (self.linked_price_display == "" or not isinstance(self.linked_price_display, PriceDisplay)):
            logger.debug("No linked price_display for the scale device id " + self.node_id)
            return False

        num_of_weight_changes = self.weight_sensor.number_of_weight_changes
        seconds_since_begin = self.weight_sensor.now_in_seconds

        num_of_shelf_refills = self.refill_sensor.number_of_refills
        
        price_obj = self.linked_price_display
        
        initial_price = price_obj.initial_price
        current_price = price_obj.current_price
        #here we can implement the logic for the price changing, after we can easily change the price
        """
        THE PRICE CHANGES' RULES:
        1a. A product has a good selling ratio if num_of_shelf_refills / hour is more than 200
        1b. A product has a bad selling ratio if num_of_shelf_refills / hour is less than 100
        1c. A product has a terrible selling ratio if num_of_shelf_refills / hour is less than 10
        2a. A product can increase its price until 30% more than the initial price
        2b. A product can decrease its price until 60% less than the initial price
        3a. Do not change the price of a product, if it has changed recently (if price_obj.last_price_change is in the last 30 minutes)

        """
        CHANGE_THRESHOLD = 30 * 60  #30 minutes times 60 to obtain the value in seconds

        time_diff = datetime.datetime.now() - price_obj.last_price_change

        assert isinstance(time_diff, datetime.timedelta)
        if(time_diff.total_seconds() < CHANGE_THRESHOLD):
            return

        number_of_hours = seconds_since_begin / 3600

        if( (num_of_shelf_refills / number_of_hours) > 200):
            #case 1a -> we have to increase the price
            new_price = current_price * 1.1
            if(new_price > initial_price * 1.3):
                new_price = initial_price * 1.3
        elif( (num_of_shelf_refills / number_of_hours) < 10):
            #case 1c -> we want to set the price to minimum value
            new_price = initial_price * 0.4
        elif( (num_of_shelf_refills / number_of_hours) < 100):
             #case 1b -> we have to decrease the price
            new_price = current_price * 0.9
            if(new_price < initial_price * 0.4):
                new_price = initial_price * 0.4
        else:
            #normal selling ratio
            return

        price_obj.set_new_price(new_price)
        return
        
    def is_multi_resources_node(self):
        return True

    def get_resources_state(self):
        w_sensor_outcome = self.weight_sensor.get_current_state()
        r_sensor_outcome = self.refill_sensor.get_current_state()

        #get_current_state returns -1 OR False in case of error 
        if (not w_sensor_outcome and not r_sensor_outcome) or (w_sensor_outcome == -1 and r_sensor_outcome == -1):
            return False
        else:
            self.update_last_seen()
            return self

    #------------------------------------------------------------------------------------------------------------------------
    #proper interface methods to get or set the state of the resources of the node.
    #those methods should also call update_last_seen method on the Node

    def prompt_shelf_refill(self):
        return self.refill_sensor.prompt_refill()
    
    def get_current_weight(self):
        outcome = self.weight_sensor.get_current_state()
        if outcome != -1 and outcome:
            self.update_last_seen()
            return self.weight_sensor.current_weight
        else:
            return False

    def get_last_refill_ts(self):
        outcome = self.refill_sensor.get_current_state()
        if outcome != -1 and outcome:
            self.update_last_seen()
            return self.refill_sensor.last_refill
        else:
            return False

    #------------------------------------------------------------------------------------------------------------------------

    def bind_price_display(self, price_display_obj):
        if(self.linked_price_display!=""):
            logger.warning("[ScaleDevice: bind_scale_device] Scale Device has already been associated with Price Display")
            return False

        assert isinstance(price_display_obj, PriceDisplay)

        self.linked_price_display = price_display_obj

    def delete(self):
        if isinstance(self.weight_sensor, WeightSensor):
            self.weight_sensor.delete()
            del self.weight_sensor
        if isinstance(self.refill_sensor, RefillSensor):
            self.refill_sensor.delete()
            del self.refill_sensor
        self.delete_thread()

    def __del__(self):
        self.delete()