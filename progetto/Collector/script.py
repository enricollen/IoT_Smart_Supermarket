#TO DO LIST:
    #link to db
    #COAP /registration endpoint
    #MQTT subscribe

#starts COAPserver with 'register' endpoint
#we have to bind the COAP models to the registrations of each kind of node
from COAP.COAP_registration_server import CoAPServer

COAP_SERVER_IP = "::"
COAP_SERVER_PORT = 5683


server = CoAPServer(COAP_SERVER_IP, COAP_SERVER_PORT)

try:
    print("Starting smart Super-Market Collector")
    server.listen(10)
except KeyboardInterrupt:
    print("Server Shutdown")
    server.close()
    print("Exiting...")