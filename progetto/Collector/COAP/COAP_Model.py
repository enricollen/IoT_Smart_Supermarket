from DatabaseConnection import DatabaseConnection
from coapthon.client.helperclient import HelperClient
from abc import ABC, abstractmethod
import json

import logging

logger = logging.getLogger("COAPModule")
#logging.config(level=logging.DEBUG)

DEFAULT_COAP_PORT = 5683

#classe astratta con alcuni metodi da implementare

class COAPModel:
    ip_address = ""
    resource_path = ""
    is_observable = False

    def __init__(self, ip_address):
        self.ip_address = ip_address
        #self.resource_path = resource_path

        if self.get_current_state() == False:
            #we have to throw an exception
            raise Exception("[COAPModel]: unable to instantiate the object | ip: " + str(self.ip_address))


        if(self.is_observable()):
            self.start_observing(self.observe_handler)

    def is_observable(self):
        return self.is_observable

    @abstractmethod #not sure if it should be abstract or not
    def start_observing(self, observe_handler):
        #TO DO:
        #implement COAPthon method to register as observer and bind observe_handler to handle notifies
        pass

    @abstractmethod #not sure if it should be abstract or not
    def observe_handler(self):
        #TO DO:
        #in some ways receives current node state whenever it updates its state and notifies the subscribers,
        #we then have to update object state and store it in the database
        pass

    #@abstractmethod
    def get_current_state(self):
        client = HelperClient(server=(self.ip_address, DEFAULT_COAP_PORT))
        response = client.get(self.resource_path)
        client.stop()
        #here we have to do something with the response

        if(response.payload == None):
                logger.warning("[COAPmodel.get_current_state]: empty response from node " + str(self.ip_address))
                return False

        try:
            json_parsed = json.loads(response.payload)
        except:
            logger.warning("[COAPmodel.get_current_state]: unable to parse JSON from " + str(self.ip_address) + " | trew on response.payload= " + str( response.payload ) )
            return False

        ret = self.update_state_from_json(json_parsed)
        if ret:
            self.save_current_state()
            return self
        else:
            return False


    @abstractmethod
    def update_state_from_json(json):
        pass

    @abstractmethod
    def set_new_values(self):
        pass

    @abstractmethod
    def save_current_state(self):
        pass

    