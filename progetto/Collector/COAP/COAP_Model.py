from DatabaseConnection import DatabaseConnection
from coapthon.client.helperclient import HelperClient
from coapthon import defines
from coapthon.messages.message import Message
from abc import ABC, abstractmethod
import json

import logging

logger = logging.getLogger("COAPModule")
#logging.config(level=logging.DEBUG)

from COAP.const import NO_CHANGE, DEFAULT_STYLE, YELLOW_STYLE, CANNOT_PARSE_JSON, bold
DEFAULT_COAP_PORT = 5683

DEFAULT_TIMEOUT = 10 #in seconds

import Node

#abstract class: use this to implement node types connected via CoAP

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
        #logger.debug("[start_observing]: begin")
        self.observer_client = HelperClient(server=(self.ip_address, DEFAULT_COAP_PORT))
        self.observer_client.observe(self.resource_path, self.observe_handler, timeout = DEFAULT_TIMEOUT)
        #client.stop()  #DO NOT STOP THE OBSERVER CLIENT
        return self

    def observe_handler(self, response):
        #in some ways receives current node state whenever it updates its state and notifies the subscribers,
        #we then have to update object state and store it in the database
        ret = self.parse_state_response(response)
        if ret == False:
            logger.error("[observe_handler] unable to parse state for ip : " + str(self.ip_address))

        #method to stop observing: self.observer_client.cancel_observing(response, True)  #True if you want to send RST message, else False
        return
    
    def new_message_from_the_node(self):
        #---------------------------
        if isinstance(self, Node.Node):
            self.update_last_seen()
        #else if it is not a Node istance, it is a resource of a multiresources Node, in that case the update_last_seen should be handled by the wrapper class
        #---------------------------
        return

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
        
        self.new_message_from_the_node()

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
        response = client.get(self.resource_path, timeout=DEFAULT_TIMEOUT)
        client.stop()
        return self.parse_state_response(response)

    def set_new_values(self, req_body, callback = None, use_default_callback = False):
        #make a COAP request using method POST to the RESOURCE endpoint
        #the body of the request differes per each kind of node

        #a callback function that check the response from the node, in case of error it logs the error
        def default_callback(message):
            #message is instance of the class Message in CoAPthon
            #it has the attributes code, payload, etc...
            #we want to check the result code and the response payload
            is_message = isinstance(message, Message)
            is_bad_request = False
            if is_message:
                is_bad_request = message.code == defines.Codes.BAD_REQUEST.number
            if not is_message or is_bad_request:
                payload = None
                if is_message:
                    payload = str(message.payload)
                logger.warning("[!] set_new_values error: bad request | response payload : " + str(payload) )
                #consider if removing the node or invoking some checks on that node
            else:
                logger.debug("set_new_values: received node response = " + str(message.payload))
                self.new_message_from_the_node()
            return

        if use_default_callback:
            callback = default_callback

        client = HelperClient(server=(self.ip_address, DEFAULT_COAP_PORT))
        response = client.post(self.resource_path, req_body, callback=callback, timeout=DEFAULT_TIMEOUT)
        #sometimes this post request throws an exception ------------ // cannot join thread before it is started
        #as a workaround we call a sleep before the stop method
        import time
        time.sleep(0.1)
        client.stop()
        return

    @abstractmethod
    def update_state_from_json(json):
        pass

    @abstractmethod
    def save_current_state(self):
        pass

    def close_coap_connections(self):
        if self.observer_client:
            self.observer_client.close()
            del self.observer_client

    def delete(self):#method to call when you want to close the server
        self.close_coap_connections()

    def __del__(self):  #class disruptor
        #self.observer_client.cancel_observing()
        self.delete()

    #---------------------------------------------
    def class_style(self, string):
        return self.name_style + string + DEFAULT_STYLE