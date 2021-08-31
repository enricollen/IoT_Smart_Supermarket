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

from COAP.const import blue

from MQTT.MqttDiscoverer import MQTTDiscoverer

from CommandPrompt import CommandPrompt

import logging
import sys
import threading

log_format = "%(asctime)s - %(threadName)-10s - %(name)s - %(levelname)s - %(message)s"
log_file = "log.txt"

root_logger = logging.getLogger()

lhStdout = root_logger.handlers[0]  # stdout is the only handler initially

output_file_handler = logging.FileHandler(log_file)

formatter = logging.Formatter(log_format)

output_file_handler.setFormatter(formatter)
output_file_handler.setLevel(logging.DEBUG)

root_logger.addHandler(output_file_handler)

root_logger.removeHandler(lhStdout)

logger = logging.getLogger(__file__)
logger.setLevel(level=logging.DEBUG)

def boot_logo():
    print( blue ("""
        d8888b.  .d8b.   .o88b. d888888b  .d88b.  db      db      d88888b d8b   db
        88  `8D d8' `8b d8P  Y8   `88'   .8P  Y8. 88      88      88'     888o  88
        88oodD' 88ooo88 8P         88    88    88 88      88      88ooooo 88V8o 88
        88~~~   88~~~88 8b         88    88    88 88      88      88~~~~~ 88 V8o88
        88      88   88 Y8b  d8   .88.   `8b  d8' 88booo. 88booo. 88.     88  V888
        88      YP   YP  `Y88P' Y888888P  `Y88P'  Y88888P Y88888P Y88888P VP   V8P
    """) )


server = CoAPServer(COAP_SERVER_IP, COAP_SERVER_PORT)

try:
    boot_logo()
    print("Starting smart SuperMarket Collector")
    
    try:
        mqttdiscoverer = MQTTDiscoverer()
    except Exception as e:
        logger.critical("Cannot start MQTT Discovery")
        print(e)

    command_prompt = CommandPrompt()

    server.listen(10)

except KeyboardInterrupt:
    print("\nServer Shutdown")
    server.close()
    mqttdiscoverer.close()
    collector.close()
    command_prompt.stop()

    #mqtt_client.close()
    print("Exiting...")
    logger.info("""

        __________   ___  __  .___________. __  .__   __.   _______ 
        |   ____\  \ /  / |  | |           ||  | |  \ |  |  /  _____|
        |  |__   \  V  /  |  | `---|  |----`|  | |   \|  | |  |  __  
        |   __|   >   <   |  |     |  |     |  | |  . `  | |  | |_ | 
        |  |____ /  .  \  |  |     |  |     |  | |  |\   | |  |__| | 
        |_______/__/ \__\ |__|     |__|     |__| |__| \__|  \______| 
                                                             
    --------------------------------------------------------------------
    """)

    """
    for thread in threading.enumerate(): 
        print(thread.name)
    """
    sys.exit()    