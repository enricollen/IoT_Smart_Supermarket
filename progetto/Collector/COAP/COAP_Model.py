from DatabaseConnection import DatabaseConnection
from coapthon.client.helperclient import HelperClient
from abc import ABC, abstractmethod
import json

import logging

logger = logging.getLogger("COAPModule")
#logging.config(level=logging.DEBUG)

from COAP.const import NO_CHANGE, DEFAULT_STYLE, YELLOW_STYLE, CANNOT_PARSE_JSON, bold
DEFAULT_COAP_PORT = 5683

#classe astratta con alcuni metodi da implementare

class COAPModel:
    ip_address = ""
    resource_path = ""
    observable = False
    observer_client = None
    name_style = YELLOW_STYLE
    
    def __init__(self, ip_address):
        self.ip_address = ip_address
        #self.resource_path = resource_path

        if self.get_current_state() == False:
            #we have to throw an exception
            raise Exception("[COAPModel]: unable to instantiate the object | ip: " + str(self.ip_address))

        if(self.observable == True):
            self.start_observing()


    def is_observable(self):
        return self.observable == True

    #@abstractmethod #not sure if it should be abstract or not
    #REFERENCE: https://github.com/Tanganelli/CoAPthon/blob/6db71de6fef365e428308adcbc59e477922ee688/coapclient.py#L28
    def start_observing(self):
        #implement COAPthon method to register as observer and bind observe_handler to handle notifies
        logger.debug("[start_observing]: begin")
        self.observer_client = HelperClient(server=(self.ip_address, DEFAULT_COAP_PORT))
        self.observer_client.observe(self.resource_path, self.observe_handler)
        #client.stop()  #DO NOT STOP THE OBSERVER CLIENT
        return self

    #@abstractmethod #not sure if it should be abstract or not
    def observe_handler(self, response):
        #TO DO:
        #in some ways receives current node state whenever it updates its state and notifies the subscribers,
        #we then have to update object state and store it in the database
        ret = self.parse_state_response(response)
        if ret == False:
            logger.error("[observe_handler] unable to parse state for ip : " + str(self.ip_address))

        #method to stop observing: self.observer_client.cancel_observing(response, True)  #True if you want to send RST message, else False
        return
        #pass

    def parse_state_response(self, response):

        if(response == None):
                return -1   #this happen when you call the delete method

        if(response.payload == None):
                logger.warning("[COAPmodel.parse_state_response]: empty response from node " + str(self.ip_address))
                return False

        try:
            json_parsed = json.loads(response.payload)
        except:
            logger.warning("[COAPmodel.parse_state_response]: unable to parse JSON from " + str(self.ip_address) + " | trew on response.payload= " + str( response.payload ) )
            return False
        try:
            ret = self.update_state_from_json(json_parsed)
        except Exception as e:
            logger.critical("exception during update_state_from_json | json = " + str(response.payload))
            raise(e)
        if ret == NO_CHANGE:
            logger.info("[" + self.ip_address +"]["+ self.class_style(self.__class__.__name__ + ".parse_state_response") + "]: no change")
            return self
        elif ret:
            self.save_current_state()
            logger.info("[" + self.ip_address +"]["+ self.class_style(self.__class__.__name__ + ".parse_state_response") + "]: new node state set: " + bold( str(response.payload) ) )
            return self
        elif ret == CANNOT_PARSE_JSON:
            logger.warning("CANNOT_PARSE_JSON")
            return False
        elif ret == False:
            return False
        return self

    def get_current_state(self):
        client = HelperClient(server=(self.ip_address, DEFAULT_COAP_PORT))
        response = client.get(self.resource_path)
        client.stop()
        return self.parse_state_response(response)


    @abstractmethod
    def update_state_from_json(json):
        pass

    @abstractmethod
    def set_new_values(self):
        pass

    @abstractmethod
    def save_current_state(self):
        pass

    def delete(self):#method to call when you want to close the server
        
        if self.observer_client:
            self.observer_client.close()

    def __del__(self):  #class disruptor
        #self.observer_client.cancel_observing()
        if self.observer_client:
            self.observer_client.close()

    #---------------------------------------------
    def class_style(self, string):
        return self.name_style + string + DEFAULT_STYLE