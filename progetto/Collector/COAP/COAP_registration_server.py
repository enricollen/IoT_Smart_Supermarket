#import getopt
#import sys
from typing import Collection
from coapthon.server.coap import CoAP

from coapthon import defines
from coapthon.resources.resource import Resource

import logging
logger = logging.getLogger("COAPserver")
logger.setLevel(level=logging.DEBUG)

from Collector import collector
from COAP.const import ADDRESS_ALREADY_IN_USE, PRICE_DISPLAY, SHELF_SCALE, italic, bold, ALREADY_REGISTERED, REGISTRATION_SUCCESSFULL, NOT_REGISTERED, INTERNAL_ERROR, WRONG_PAYLOAD

class RegistrationResource(Resource):

    def __init__(self, name="RegistrationResource", coap_server=None):
        super(RegistrationResource, self).__init__(name, coap_server, visible=True, observable=False, allow_children=True)

        self.payload = "Registration Endpoint"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1" #TO DO: ?

    def render_GET_advanced(self, request, response):
        
        (node_ip, node_port) = request.source   #request.source should contain a tuple (ip, port)
        
        if node_ip in collector.connected_ip_list():
            response.payload = ALREADY_REGISTERED
        else:
            response.payload = NOT_REGISTERED

        return self, response

    def render_POST_advanced(self, request, response):  #render_POST(self, request):
    
        #here we have to handle the registration requests from the nodes
        #we should obtain the kind of node and call the proper class constructor
        #if the node is already registered, we should properly handle the request

        from coapthon.messages.response import Response
        assert(isinstance(response, Response))

        (node_ip, node_port) = request.source   #request.source should contain a tuple (ip, port)
        node_kind = request.payload

        node_connection_status = collector.check_if_already_connected(node_ip = node_ip, kind = node_kind)

        if node_connection_status == ALREADY_REGISTERED: #node_ip in collector.connected_ip_list():
            response.payload = ALREADY_REGISTERED
            response.code = defines.Codes.PRECONDITION_FAILED.number
            #we should anwer with 200 already connected
        elif node_connection_status == ADDRESS_ALREADY_IN_USE:
            response.payload = ADDRESS_ALREADY_IN_USE
            response.code = defines.Codes.PRECONDITION_FAILED.number
        elif node_connection_status == NOT_REGISTERED:
            options = {
            PRICE_DISPLAY : collector.register_new_price_display,
            SHELF_SCALE : collector.register_new_scale_device
            }

            #we assume that the payload contains only a string indicating the kind of node
            if node_kind in options:  #searches over the keys
                success = options[node_kind](node_ip)   #instantiates the nodes' model
                if( success == False):
                    response.payload = INTERNAL_ERROR
                    logger.debug("INTERNAL_ERROR: request.payload = " + str(request.payload))
                    response.code = defines.Codes.INTERNAL_SERVER_ERROR.number
                else:
                    response.payload = REGISTRATION_SUCCESSFULL    #should send ACK 200 response

            else:
                response.payload = WRONG_PAYLOAD
                logger.debug("WRONG_PAYLOAD: request.payload = " + str(request.payload))
                response.code = defines.Codes.BAD_REQUEST.number
                #wrong payload -> we should answer with error 400 (bad request)
        else:
            logger.error("check_if_already_connected returned: " + node_connection_status)
            response.payload = INTERNAL_ERROR
            response.code = defines.Codes.INTERNAL_SERVER_ERROR.number

        logger.info("["+ bold("registration_server") + "]: registration request from [" +bold( str(node_ip) ) + "] | outcome: " + italic(response.payload))
        return self, response

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("register/", RegistrationResource())