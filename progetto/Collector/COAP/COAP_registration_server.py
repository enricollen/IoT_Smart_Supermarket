#import getopt
#import sys
from typing import Collection
from coapthon.server.coap import CoAP

from coapthon.resources.resource import Resource

from Collector import collector

REGISTRATION_SUCCESSFULL = "Registration Successfull"
ALREADY_REGISTERED = "Already Registered"
WRONG_PAYLOAD = "Invalid Sensor Type"

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

    def render_POST(self, request):
        #TO DO:
        #here we have to handle the registration requests from the nodes
        #we should obtain the kind of node and call the proper class constructor
        #if the node is already registered, we should properly handle the request
        (node_ip, node_port) = request.source   #request.source should contain a tuple (ip, port)

        if node_ip in collector.connected_ip_list():
            #we should anwer with 200 already connected

        options = {
           "PriceDisplay" : collector.register_new_price_display,
           "ShelfScale" : collector.register_new_shelf_scale_device
        }

        #we assume that the payload contains only a string indicating the kind of node
        if request.payload in options:  #searches over the keys
            options[request.payload](node_ip)   #instantiates the nodes' model
            #should send ACK 200 response
        else:
            #wrong payload -> we should answer with error 400 (bad request)

        return self

class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port), False)
        self.add_resource("register/", RegistrationResource())