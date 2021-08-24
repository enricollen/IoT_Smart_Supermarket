import traceback

from COAP.PriceDisplay import PriceDisplay
from COAP.ScaleDevice import ScaleDevice

from MQTT.FridgeTempSensor import FridgeTempSensor


from COAP.const import *

import logging
default_logger = logging.getLogger()
default_logger.setLevel(level=logging.CRITICAL)
logger = logging.getLogger("COAPModule")
logger.setLevel(level=logging.DEBUG)



class Collector:
    price_display_array = [] #array of PriceDisplays
    shelf_scale_device_array = [] # [ScaleDevice1, ScaleDevice2...]
    coupled_scale_and_price = [] # [[Scale1, Price1], [Scale2, Price2], ...]
    
    coap_devices = {}    #key: ip | value: bounded_object

    fridge_temp_sensor_array = [] # [FridgeTempSensor1, FridgeTempSensor2, ...] 

    mqtt_devices = {}   #key: node_id | value: bounded_object

    all_devices = {}    #key: node_id | value: bounded_object

    def __init__(self):
        #DONE IN Node.py:
        #a dedicated thread (or more than one) that checks the connection to each COAP node, 
        # in case that it is not reachable, it deletes it from devices using a proper method
            #each COAP obj should have a field 'last_connection' containing the timestamp of the last successful connection
            #the thread should check that now() - last_connection is under a certain value, in case it is not, it should try to make a request to the node
            #if it does not receives a response, it should delete it
        #
        #Talking by the node-side, it should have a connection_status variable, indicating whether it is connected to the internet and if it is connected to the collector
        return

    def check_if_already_connected(self, node_ip = "", node_id = "", kind = "", is_mqtt_connection = False):

        if(kind not in KINDS_LIST):
            logger.warning("[check_if_already_connected]: Kind not recognised! Received kind: "+ kind)
            return KIND_NOT_RECOGNISED

        if(node_ip != "" and is_mqtt_connection):
            logger.error("BAD USE OF THE FUNCTION check_if_already_connected!")
            return False

        if node_ip != "":
            if(node_ip in self.coap_devices):
                if kind == self.coap_devices[node_ip].kind:
                    self.coap_devices[node_ip].update_last_seen()
                    return ALREADY_REGISTERED
                else:
                    #case when a different kind of node is trying to connect with an ip already assigned to a node of another kind
                    logger.error("A node is trying to connect using an IP already in use by another node! node_ip = " + node_ip + " | new node kind = " + kind + " | already registered kind = " + self.coap_devices[node_ip].kind)
                    #here we could check the node.last_seen of the old node and verify that it is still alive, and handle the different cases
                    return ADDRESS_ALREADY_IN_USE
            else:
                return NOT_REGISTERED
        
        if node_id != "" and is_mqtt_connection:
            if(node_id in self.mqtt_devices):
                if kind == self.mqtt_devices[node_id].kind:
                    self.mqtt_devices[node_id].update_last_seen()
                    return ALREADY_REGISTERED
                else:
                    #case when a different kind of node is trying to connect with an ip already assigned to a node of another kind
                    logger.error("A node is trying to connect using an ID already in use by another node! node_id = " + node_id + " | new node kind = " + kind + " | already registered kind = " + self.mqtt_devices[node_id].kind)
                    #here we could check the node.last_seen of the old node and verify that it is still alive, and handle the different cases
                    return ADDRESS_ALREADY_IN_USE
            else:
                return NOT_REGISTERED
            

        return False

    def register_new_COAP_device(self, ip_addr, obj, kind):
        self.coap_devices[ip_addr] = obj
        
        #TO TEST:
        self.register_node(obj.node_id, obj)
        
        logger.debug("[register_new_COAP_device] ip: " + ip_addr + "| kind: " + kind)
        return self
    
    def connected_ip_list(self):
        return list( self.coap_devices.keys() )

    def register_new_price_display(self, ip_addr):

        try:
            price_display = PriceDisplay(ip_addr)
        except Exception as e:
            logger.critical("[Collector->register_new_price_display] exception: " + str(e))
            traceback.print_exc()
            return False

        self.register_new_COAP_device(ip_addr, price_display, PRICE_DISPLAY)

        self.price_display_array.append(price_display)

        #logic for binding a weight sensor with correspondent price display
        self.bind_price_and_scale(obj_price_display = price_display) 

        return self

    def remove_price_display(self, node_id):
        obj = self.all_devices[node_id]
        node_ip = self.all_devices[node_id].ip_address
        #here we check if this price-display was bounded with a scale device
        self.unbind_price_and_scale(obj)
        self.price_display_array.remove(obj)    #node_ip
        node = self.coap_devices[node_ip]
        assert isinstance(node, PriceDisplay)
        node.delete()
        del node
        del self.coap_devices[node_ip]
        return

    def register_new_scale_device(self, ip_addr):
        try:
            scale_device = ScaleDevice(ip_addr)
        except Exception as e:
            logger.warning(e)
            traceback.print_exc()
            return False

        self.register_new_COAP_device(ip_addr, scale_device, SHELF_SCALE)

        self.shelf_scale_device_array.append(scale_device)

        #logic for binding a weight sensor with correspondent price display
        self.bind_price_and_scale(obj_scale_device = scale_device) 

        return self
    
    def remove_scale_device(self, node_id):
        obj = self.all_devices[node_id]
        assert isinstance(obj, ScaleDevice), "[remove_scale_device]: the obj was supposed to be an instance of ScaleDevice"
        node_ip = self.all_devices[node_id].ip_address
        #here we check if this price-display was bounded with a scale device
        self.unbind_price_and_scale(obj)
        self.shelf_scale_device_array.remove(obj)   #node_ip
        obj = self.coap_devices[node_ip]
        assert isinstance(obj, ScaleDevice)
        obj.delete()
        del obj
        del self.coap_devices[node_ip]
        return

    #utility array to make binding process easier
    spare_price_displays = [] 
    spare_scale_devices = []

    def bind_price_and_scale(self, obj_price_display = None, obj_scale_device = None):
        if obj_price_display: #we want to bind price display with a spare scale device
            if len(self.spare_scale_devices)==0:
                self.spare_price_displays.append(obj_price_display)
                return
            else:
                obj_scale_device = self.spare_scale_devices.pop()
                assert isinstance(obj_scale_device, ScaleDevice), "[collector.bind_price_and_scale]: obj_scale_device is not instance of ScaleDevice!"
                assert isinstance(obj_price_display, PriceDisplay), "[collector.bind_price_and_scale]: obj_price_display is not instance of PriceDisplay!"
                obj_scale_device.bind_price_display(obj_price_display)
                obj_price_display.bind_scale_device(obj_scale_device)
                self.coupled_scale_and_price.append([obj_scale_device, obj_price_display])

        elif obj_scale_device: #we want to bind scale device with a spare price display
            if len(self.spare_price_displays)==0:
                self.spare_scale_devices.append(obj_scale_device)
                return
            else:
                obj_price_display = self.spare_price_displays.pop()
                assert isinstance(obj_scale_device, ScaleDevice), "[collector.bind_price_and_scale]: obj_scale_device is not instance of ScaleDevice!"
                assert isinstance(obj_price_display, PriceDisplay), "[collector.bind_price_and_scale]: obj_price_display is not instance of PriceDisplay!"
                obj_scale_device.bind_price_display(obj_price_display)
                obj_price_display.bind_scale_device(obj_scale_device)
                self.coupled_scale_and_price.append([obj_scale_device, obj_price_display])


    def unbind_price_and_scale(self, obj):

        found = False

        for couple in self.coupled_scale_and_price:
            if obj in couple:
                found = True
                self.coupled_scale_and_price.remove(couple)
                assert isinstance(couple, list)
                couple.remove(obj)
                spare_obj = couple.pop()
                #we want to know the kind of this obj and add it to the correct spare_array
                if spare_obj.kind == PRICE_DISPLAY:
                    self.spare_price_displays.append(spare_obj)
                elif spare_obj.kind == SHELF_SCALE:
                    self.spare_scale_devices.append(spare_obj)
                return

        if not found:
            if obj.kind == PRICE_DISPLAY:
                self.spare_price_displays.remove(obj)
            elif obj.kind == SHELF_SCALE:
                self.spare_scale_devices.remove(obj)

        return

#---------------------------------------------------------------------------------------------

    def register_new_mqtt_device(self, node_id, obj, kind):
        self.mqtt_devices[node_id] = obj
        self.register_node(node_id, obj)
        logger.debug("[register_new_MQTT_device] node_id: " + node_id + "| kind: " + kind)
        return self

    def connected_node_id_list(self):
        return list( self.mqtt_devices.keys() )

    def register_new_fridge_temp_sensor(self, node_id):
        #we should check that this sensor is not present yet
        if node_id in self.connected_node_id_list():
            return ALREADY_REGISTERED
        
        try:
            fridge_temp_sensor = FridgeTempSensor(node_id)
        except Exception as e:
            logger.critical("[Collector->register_new_fridge_temp_sensor] exception: " + str(e))
            traceback.print_exc()
            return False

        self.register_new_mqtt_device(node_id, fridge_temp_sensor, FRIDGE_TEMPERATURE_SENSOR)

        self.fridge_temp_sensor_array.append(fridge_temp_sensor)

        return self

    def remove_fridge_temperature_sensor(self, node_id):
        #TO TEST:
        #check that the remove from temp_sensor_array works properly
        obj = self.mqtt_devices[node_id]
        self.fridge_temp_sensor_array.remove(obj)   #node_id
        del self.mqtt_devices[node_id]
        return

#---------------------------------------------------------------------------------------------

    def register_node(self, node_id, obj):
        self.all_devices[node_id] = obj
        return True

    def remove_node(self, node_id, node_ip = None):

        node_kind = self.all_devices[node_id].kind

        action = {
            FRIDGE_TEMPERATURE_SENSOR: self.remove_fridge_temperature_sensor,
            PRICE_DISPLAY: self.remove_price_display,
            SHELF_SCALE: self.remove_scale_device
        }

        logger.debug("going to delete node " + node_id + " | kind = " + node_kind)

        try:
            action[node_kind](node_id)
        except Exception as e:
            logger.warning("Cannot remove node! node_kind = " + node_kind + " | node_id = " + node_id)
            traceback.print_exc()
            return False

        del self.all_devices[node_id]

        logger.debug("just deleted node " + node_id + " | kind = " + node_kind)

        return True

    def close(self):
        node_ids = list( self.all_devices.keys() )
        for node_id in node_ids:
            self.remove_node(node_id=node_id)
        
        return
    
    def __del__(self):
        self.close()

            
collector = Collector()