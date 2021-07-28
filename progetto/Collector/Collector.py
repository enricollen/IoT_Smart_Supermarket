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

    def __init__(self):
        #TO DO:
        #a dedicated thread (or more than one) that checks the connection to each COAP node, 
        # in case that it is not reachable, it deletes it from devices using a proper method
            #each COAP obj should have a field 'last_connection' containing the timestamp of the last successful connection
            #the thread should check that now() - last_connection is under a certain value, in case it is not, it should try to make a request to the node
            #if it does not receives a response, it should delete it
        #
        #Talking by the node-side, it should have a connection_status variable, indicating whether it is connected to the internet and if it is connected to the collector
        return

    def register_new_COAP_device(self, ip_addr, obj, kind):
        self.coap_devices[ip_addr] = obj
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
        self.bind_price_and_scale(ip_addr_price_display=ip_addr) 

        return self

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
        self.bind_price_and_scale(ip_addr_scale_device=ip_addr) 

        return self

    #utility array to make bind prcess easier
    spare_price_displays = [] 
    spare_scale_devices = []

    def bind_price_and_scale(self, ip_addr_price_display="", ip_addr_scale_device=""):
        if ip_addr_price_display!="": #we want to bind price display with a spare scale device
            if len(self.spare_scale_devices)==0:
                self.spare_price_displays.append(ip_addr_price_display)
                return
            else:
                ip_addr_scale_device = self.spare_scale_devices.pop()
                self.coupled_scale_and_price.append([ip_addr_scale_device, ip_addr_price_display])

        if ip_addr_scale_device!="": #we want to bind scale device with a spare price display
            if len(self.spare_price_displays)==0:
                self.spare_scale_devices.append(ip_addr_scale_device)
                return
            else:
                ip_addr_price_display = self.spare_price_displays.pop()
                self.coupled_scale_and_price.append([ip_addr_scale_device, ip_addr_price_display])

#---------------------------------------------------------------------------------------------

    def register_new_mqtt_device(self, node_id, obj, kind):
        self.mqtt_devices[node_id] = obj
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

#---------------------------------------------------------------------------------------------

    def close(self):
        """while 1:
            if len(self.price_display_array):
                el = self.price_display_array.pop()
                el.delete()
                
            elif len(self.shelf_scale_device_array):
                el = self.shelf_scale_device_array.pop()
                el.delete()
            else:
                break"""
        for ip, obj in self.coap_devices.items():
            #logger.info("[closing connection with]: " + obj.kind + " | ip: " + ip)
            obj.delete()
            del obj
            
collector = Collector()