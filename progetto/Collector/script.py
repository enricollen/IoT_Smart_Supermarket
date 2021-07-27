#TO DO LIST:
    #link to db
    #COAP /registration endpoint
    #MQTT subscribe

#starts COAPserver with 'register' endpoint
#we have to bind the COAP models to the registrations of each kind of node
from COAP.COAP_registration_server import CoAPServer
from Collector import collector

COAP_SERVER_IP = "::"
COAP_SERVER_PORT = 5683

def boot_logo():
    print("""
    d8888b.  .d8b.   .o88b. d888888b  .d88b.  db      db      d88888b d8b   db
    88  `8D d8' `8b d8P  Y8   `88'   .8P  Y8. 88      88      88'     888o  88
    88oodD' 88ooo88 8P         88    88    88 88      88      88ooooo 88V8o 88
    88~~~   88~~~88 8b         88    88    88 88      88      88~~~~~ 88 V8o88
    88      88   88 Y8b  d8   .88.   `8b  d8' 88booo. 88booo. 88.     88  V888
    88      YP   YP  `Y88P' Y888888P  `Y88P'  Y88888P Y88888P Y88888P VP   V8P
    """)

server = CoAPServer(COAP_SERVER_IP, COAP_SERVER_PORT)

try:
    boot_logo()
    print("Starting smart SuperMarket Collector")
    server.listen(10)
except KeyboardInterrupt:
    print("\nServer Shutdown")
    server.close()
    #I think that the cause for the program to not closing is that some COAP_Models do observe certain topic and they keep some COAPthon clients opened
    collector.close()
    print("Exiting...")
    exit()
    