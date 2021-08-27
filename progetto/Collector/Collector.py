import traceback

from COAP.PriceDisplay import PriceDisplay
from COAP.ScaleDevice import ScaleDevice

from MQTT.MqttClient import MqttClient
from COAP.COAP_Model import COAPModel

from MQTT.FridgeTempSensor import FridgeTempSensor

from Node import Node

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
        del self.coap_devices[node_ip]
        node.delete()
        del node
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
        del self.coap_devices[node_ip]
        obj.delete()
        del obj
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
        assert isinstance(obj, FridgeTempSensor)
        obj.delete()
        del self.mqtt_devices[node_id]
        del obj
        return

#---------------------------------------------------------------------------------------------

    def register_node(self, node_id, obj):
        self.all_devices[node_id] = obj
        return True

    def remove_node(self, node_id, node_ip = None):

        if node_id not in self.all_devices.keys():
            logger.warning("Tried to remove an unregistered node! node_id = " + node_id)
            return False

        if not isinstance(self.all_devices[node_id], Node):
            logger.warning("Tried to remove a device of node_id = " + node_id + " that is not connected anymore!")
            return False

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
    
    #----------------------------------------------------------------------------

    def list_devices(self, requested_kind = "any"):

        devices = {}

        for device_id in self.all_devices.keys():
            device_obj = self.all_devices[device_id]
            assert issubclass(device_obj.__class__, Node)
            device_kind = device_obj.kind

            if requested_kind != "any" and device_kind != requested_kind:
                continue    #in that way we can return only the nodes of a certain kind

            devices[device_id] = device_kind

        return devices

    def list_couples(self):
        """
        return an array of array made of two strings, 
        the first is the node_id of ScaleDevice, the latter is the node_id of PriceDisplay
        - [
        -    ["node_id of ScaleDevice1", "node_id of PriceDisplay1"],
        -    ["node_id of ScaleDevice2", "node_id of PriceDisplay2"]
        -]
        """
        couples = []
        #[[Scale1, Price1], [Scale2, Price2]]
        for couple in self.coupled_scale_and_price:
            scale_device_obj = couple[0]
            assert isinstance(scale_device_obj, ScaleDevice)
            price_display_obj = couple[1]
            assert isinstance(price_display_obj, PriceDisplay)
            row = [str(scale_device_obj.node_id), str(price_display_obj.node_id)]
            couples.append(row)
        return couples

    def list_spare_devices(self, desired_kind = "any"):
        """
        returns a dict node_id : KIND of all the spare devices if no desired_kind is specified, else returns only the devices of the specified kind
        """
        devices_info = {}

        if(desired_kind == "any" or desired_kind == SHELF_SCALE):
            for shelf_scale_obj in self.spare_scale_devices:
                assert isinstance(shelf_scale_obj, ScaleDevice)
                shelf_node_id = shelf_scale_obj.node_id
                devices_info[shelf_node_id] = shelf_scale_obj.kind

        if(desired_kind == "any" or desired_kind == PRICE_DISPLAY):
            for price_display_obj in self.spare_price_displays:
                assert isinstance(price_display_obj, PriceDisplay)
                price_display_node_id = price_display_obj.node_id
                devices_info[price_display_node_id] = price_display_obj.kind
        
        return devices_info

    def node_info(self, node_id):
        """
        returns the infos about the connected node of specified id node_id
        - if there is no connected device with that node_id, it returns False
        - it returns a dict with the following keys:
        - "node-id"
        - "node-ip"
        - "type-of-connection"
        - "kind"
        """
        
        if node_id not in self.all_devices.keys():
            return False

        node_obj = self.all_devices[node_id]

        assert isinstance(node_obj, Node)

        infos = {}

        infos["node-id"] = node_id
        infos["kind"]    = node_obj.kind
        if isinstance(node_obj, ScaleDevice) or isinstance(node_obj, COAPModel):
            infos["type-of-connection"] = COAP_CONNECTION
            infos["node-ip"] = node_obj.ip_address
        elif isinstance(node_obj, MqttClient):
            infos["type-of-connection"] = MQTT_CONNECTION
            infos["node-ip"] = None
        else:
            infos["type-of-connection"] = "unrecognized"
            infos["node-ip"] = None

        return infos

    def get_current_price(self, node_id):
        price_obj = self.all_devices[node_id]
        if not isinstance(price_obj, PriceDisplay):
            return False
        else:
            assert isinstance(price_obj, PriceDisplay)
            return price_obj.current_price

    def set_new_price(self, node_id, new_price):
        price_obj = self.all_devices[node_id]
        if not isinstance(price_obj, PriceDisplay):
            return False
        else:
            assert isinstance(price_obj, PriceDisplay)
            price_obj.set_new_price(new_price=new_price)
            return True
    
    def get_all_prices(self):
        """
        returns a dict node_id : current_price of all the PriceDisplay devices
        """
        price_devices_info = {}

        for price_obj in self.price_display_array:
                assert isinstance(price_obj, PriceDisplay)
                price_display_node_id = price_obj.node_id
                price_devices_info[price_display_node_id] = price_obj.current_price
        
        return price_devices_info

    def get_fridge_sensor_info(self, node_id):
        """
        returns a dict {"current_temp" : current_temp_value, "desired_temp" : desired_temp_value} of the FridgeTempSensor with ID = node_id
        """
        temp_obj = self.all_devices[node_id]
        if not isinstance(temp_obj, FridgeTempSensor):
            return False
        else:
            assert isinstance(temp_obj, FridgeTempSensor)
            fridge_dict = {
                    "current_temp":temp_obj.current_temp,
                    "desired_temp":temp_obj.desired_temp
            }
            return fridge_dict

    def get_all_temperatures(self):
        """
        returns a dict of dict node_id : {"current_temp" : current_temp_value, "desired_temp" : desired_temp_value} of all the FridgeTempSensor devices
        """
        fridge_devices_info = {}

        for fridge_temp_obj in self.fridge_temp_sensor_array:
                assert isinstance(fridge_temp_obj, FridgeTempSensor)
                fridge_temp_node_id = fridge_temp_obj.node_id
                fridge_dict = {
                    "current_temp":fridge_temp_obj.current_temp,
                    "desired_temp":fridge_temp_obj.desired_temp
                }
                fridge_devices_info[fridge_temp_node_id] = fridge_dict
        
        return fridge_devices_info

    def set_new_temperature(self, node_id, new_temp):
        temp_obj = self.all_devices[node_id]
        if not isinstance(temp_obj, FridgeTempSensor):
            return False
        else:
            assert isinstance(temp_obj, FridgeTempSensor)
            temp_obj.set_new_temp(new_temp=new_temp)
            return True

    def get_scale_info(self, node_id):
        """
        returns a dict {"current_weight" : current_weight_value, "number_of_refills" : number_of_refills_value,
        "last_refill_ts" : last_refill_ts} of the ScaleDevice with ID = node_id
        """
        scale_obj = self.all_devices[node_id]
        if not isinstance(scale_obj, ScaleDevice):
            return False
        else:
            assert isinstance(scale_obj, ScaleDevice)
            scale_dict = {
                "current_weight":scale_obj.get_current_weight(),
                "number_of_refills":scale_obj.get_number_of_refills(),
                "last_refill_ts":scale_obj.get_last_refill_ts()
            }
            return scale_dict

    def get_all_scales_infos(self):
        """
        returns a dict of dict node_id : {"current_weight" : current_weight_value, "number_of_refills" : number_of_refills_value,
        "last_refill_ts" : last_refill_ts} of all the ScaleDevice devices
        """
        scale_devices_info = {}

        for scale_obj in self.shelf_scale_device_array:
                assert isinstance(scale_obj, ScaleDevice)
                scale_obj_node_id = scale_obj.node_id
                scales_dict = {
                    "current_weight":scale_obj.get_current_weight(),
                    "number_of_refills":scale_obj.get_number_of_refills(),
                    "last_refill_ts":scale_obj.get_last_refill_ts()
                }
                scale_devices_info[scale_obj_node_id] = scales_dict
        
        return scale_devices_info

    #----------------------------------------------------------------------------

    def close(self):
        node_ids = list( self.all_devices.keys() )
        for node_id in node_ids:
            self.remove_node(node_id=node_id)
        
        return
    
    def __del__(self):
        self.close()

            
collector = Collector()