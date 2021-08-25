import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

from threading import Thread

from COAP.const import KINDS_LIST, PRICE_DISPLAY, SHELF_SCALE, FRIDGE_TEMPERATURE_SENSOR, green, blue, red

from Collector import collector

#from script import stop_collector

class CommandPrompt:

    thread = None

    commands = [
        "list",
        "list-kinds",
        "list-couples",
        "show-price",
        "show-prices",
        "set-price",
        "temp-info",
        "temp-infos",
        "set-desired-temp",
        "shelf-info",
        "shelf-infos",
        "info",
        "exit"
    ]

    def __init__(self):
        self.start()

    def start(self):
        self.thread = Thread(target=self.loop)
        self.thread.start()

    #def stop(self):
    #    if isinstance(self.thread, Thread):
    #        self.thread.cancel()

    def loop(self):
        #try:
        while True:
            self.list_commands()
            self.read_command()
        #except KeyboardInterrupt:
        #    logger.debug("CommandPrompt received keyboard interrupt! terminated...")
        #    return

    def list_commands(self):
        print("""
        Available commands:
        list                        -> lists all connected nodes, their IDs and kinds
        list KIND                   -> if KIND is a recognised kind, lists all the nodes of that KIND
        list-kinds                  -> lists all existing nodes' kind
        list-couples                -> lists all the PriceDisplay - ScaleDevice couples
        list-couples  --spare       -> lists all the PriceDisplay / ScaleDevice spare nodes
        show-price ID               -> if ID is the ID of a PriceDisplay, returns the current_price shown by that node
        show-prices                 -> returns the current_price for each PriceDisplay node
        set-price ID value          -> if ID is the ID of a PriceDisplay, set a new price for that node
        temp-info ID                -> if ID is the ID of a FridgeTemperatureSensor, returns current temperature and desired temperature of that sensor
        temp-infos                  -> returns current temperature and desired temperature for each connected FridgeTemperatureSensor
        set-desired-temp ID value   -> if ID is the ID of a FridgeTemperatureSensor, set a new desired temperature for that node
        shelf-info ID               -> if ID is the ID of a ShelfScaleDevice, returns current weight, number of refills and last refill timestamp of that sensor
        shelf-infos                 -> returns current weight, number of refills and last refill timestamp for each connected ShelfScaleDevice
        info ID                     -> if ID is the ID of a connected node, calls the proper method for that node kind and returns the node's infos
        exit                        -> stops the collector
        """)
        return

    def read_command(self):
        commands = {
            "list" : self.list,
            "list-kinds" : self.list_kinds,
            "list-couples" : self.list_couples,
            "show-price" : self.show_price,
            "show-prices" : self.show_prices,
            "set-price" : self.set_price,
            "temp-info" : self.temp_info,
            "temp-infos" : self.temp_infos,
            "set-desired-temp" : self.set_desired_temp,
            "shelf-info" : self.shelf_info,
            "shelf-infos" : self.shelf_infos,
            "info" : self.info,
            "exit" : self.close
        }
        command_string = input(green("paciollen@smart_supermarket") +":" + red("collector") + "$ ")

        #we have to parse the first part of the string using ' ' (space) as delimiter 
            # -> at that point we have to check that it is a valid command
        user_command = command_string.split(' ')[0]

        user_parameters = command_string.split(' ')
        del user_parameters[0]
        #user_parameters = command_string.replace(user_command, '')

        if user_command not in commands.keys():
            print("\t[!] Unrecognized command [!]")
            return

        commands[user_command](param = user_parameters)

        return

    
    def list_kinds(self, param):
        print("The recognised kinds are:" + str(KINDS_LIST).replace('[','').replace(']',''))
        return

    def list(self, param):
        """
        list                        -> lists all connected nodes, their IDs and kinds
        list KIND                   -> if KIND is a recognised kind, lists all the nodes of that KIND
        """
        #first we want to check if the user has specified a KIND, and in that case, we want to check if that kind exists
        assert isinstance(param, list)
        if(len(param)):
            #the case in which the user has wrote some parameter after the command
            selected_kind = param[0]    #list KIND expects as first parameter the desired KIND
            if selected_kind not in KINDS_LIST:
                print("[!] list command: unrecognised kind '" + selected_kind +"'!")
                return
            else:
                #if it is a recognised kind
                #we want to list all the nodes of that kind
                nodes_info = collector.list_devices(requested_kind = selected_kind)
                print("list of the connected nodes of kind '" + selected_kind + "'")

        else:
            #we want to list all the nodes
            nodes_info = collector.list_devices()
            #here we want to order the nodes by KIND
            assert isinstance(nodes_info, dict)
            nodes_info = dict(sorted(nodes_info.items(), key=lambda item: item[1]))
            print("list of all the connected nodes")

        #now in nodes_info we have a dict made in this way--- "node_id" : "kind"
        assert isinstance(nodes_info, dict)

        for node_id in nodes_info:
            row = node_id + "\t\t\t" + nodes_info[node_id]
            print(row)

        return

    def list_couples(self, param):
        return

    def show_price(self, param):
        return

    def show_prices(self, param):
        return

    def set_price(self, param):
        return

    def temp_info(self, param):
        return

    def temp_infos(self, param):
        return
    
    def set_desired_temp(self, param):
        return

    def shelf_info(self, param):
        return

    def shelf_infos(self, param):
        return

    def info(self, param):
        return

    def close(self, param):
        stop_collector()
        #raise KeyboardInterrupt

    