#import getopt
#import sys
from typing import Collection
from coapthon.server.coap import CoAP

from coapthon import defines
from coapthon.resources.resource import Resource

import logging
logger = logging.getLogger("COAP_registration_server")
logger.setLevel(level=logging.DEBUG)

from Collector import collector

REGISTRATION_SUCCESSFULL = "Registration Successfull"
ALREADY_REGISTERED = "Already Registered"
WRONG_PAYLOAD = "Invalid Sensor Type"
INTERNAL_ERROR = "Internal error while handling the request"

class RegistrationResource(Resource):

    def __init__(self, name="RegistrationResource", coap_server=None):
        super(RegistrationResource, self).__init__(name, coap_server, visible=True, observable=False, allow_children=True)

        self.payload = "Registration Endpoint"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1" #TO DO: ?

    def render_GET(self, request):
        self.payload = "Hello"
        return self

    def render_POST_advanced(self, request, response):  #render_POST(self, request):
    
        #here we have to handle the registration requests from the nodes
        #we should obtain the kind of node and call the proper class constructor
        #if the node is already registered, we should properly handle the request

        from coapthon.messages.response import Response
        assert(isinstance(response, Response))

        (node_ip, node_port) = request.source   #request.source should contain a tuple (ip, port)

        if node_ip in collector.connected_ip_list():
            response.payload = ALREADY_REGISTERED
            response.code = defines.Codes.PRECONDITION_FAILED.number
            #we should anwer with 200 already connected
        else:
            options = {
            "PriceDisplay" : collector.register_new_price_display,
            "ShelfScale" : collector.register_new_scale_device
            }

            #we assume that the payload contains only a string indicating the kind of node
            if request.payload in options:  #searches over the keys
                success = options[request.payload](node_ip)   #instantiates the nodes' model
                if( success == False):
                    response.payload = INTERNAL_ERROR
                    logger.debug("INTERNAL_ERROR: request.payload = " + str(request.payload))

                    response.code = defines.Codes.INTERNAL_SERVER_ERROR.number
                else:
                    response.payload = REGISTRATION_SUCCESSFULL    #should send ACK 200 response

            else:
                response.payload = WRONG_PAYLOAD
                response.code = defines.Codes.BAD_REQUEST.number
                #wrong payload -> we should answer with error 400 (bad request)
        logger.info("[registration_server]: just handled registration request from " + str(node_ip) + " | response_sent = " + response.payload)
        return self, response

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("register/", RegistrationResource())