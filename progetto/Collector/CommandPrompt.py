import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

from threading import Thread

from COAP.const import COUPLES_KINDS_LIST, FRIDGE_ALARM_LIGHT, KINDS_LIST, PRICE_DISPLAY, SHELF_SCALE, FRIDGE_TEMPERATURE_SENSOR, COUPLES_NAMES_DICT, green, blue, purple, red, bold, colored_print_kind

from Collector import collector

#from script import stop_collector

class CommandPrompt:

    thread = None

    run = True

    commands = [
        "list",
        "list-kinds",
        "list-couples",
        "list-couples-kinds",
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

    def stop(self):
        if isinstance(self.thread, Thread):
            self.run = False
            del self.thread
            print("collector terminated. press ENTER to quit")

    def __del__(self):
        self.stop()

    def loop(self):
        #try:
        while self.run:
            self.list_commands()
            self.read_command()
        return
        #except KeyboardInterrupt:
        #    logger.debug("CommandPrompt received keyboard interrupt! terminated...")
        #    return

    def list_commands(self):
        print("""
        Available commands:
        list                        -> lists all connected nodes, their IDs and kinds
        list KIND                   -> if KIND is a recognised kind, lists all the nodes of that KIND
        list-kinds                  -> lists all existing nodes' kind
        list-couples-kinds          -> lists all existing couples' kinds
        list-couples                -> lists all the couples of every couple kind
        list-couples  --kind KIND   -> lists all the couples of the specified KIND, if KIND is a valid COUPLE-KIND
        list-couples  --spare       -> lists all the PriceDisplay / ScaleDevice / FridgeTempSensor / FridgeAlarmLight spare nodes
        list-couples  --spare KIND  -> lists all the spare nodes of specific kind
        show-price ID               -> if ID is the ID of a PriceDisplay, returns the current_price shown by that node
        show-prices                 -> returns the current_price for each PriceDisplay node
        set-price ID value          -> if ID is the ID of a PriceDisplay, set a new price for that node
        temp-info ID                -> if ID is the ID of a FridgeTemperatureSensor, returns current temperature and desired temperature of that sensor
        temp-infos                  -> returns current temperature and desired temperature for each connected FridgeTemperatureSensor
        set-desired-temp ID value   -> if ID is the ID of a FridgeTemperatureSensor, set a new desired temperature for that node
        get-fridge-alarm-states     -> returns current alarm state and last state change for each connected FridgeAlarmLight
        get-fridge-alarm-state  ID  -> if ID is the ID of a FridgeAlarmLight, returns current alarm state and last state change for that FridgeAlarmLight
        set-fridge-alarm-state ID X -> if ID is the ID of a FridgeAlarmLight and if X is one of ["ON", "OFF"] sets alarm state for that FridgeAlarmLight
        shelf-info ID               -> if ID is the ID of a ShelfScaleDevice, returns current weight, number of refills and last refill timestamp of that sensor
        shelf-infos                 -> returns current weight, number of refills and last refill timestamp for each connected ShelfScaleDevice
        info ID                     -> if ID is the ID of a connected node, calls the proper method for that node kind and returns the node's infos
        exit                        -> stops the collector
        """)
        return

    def read_command(self):
        commands = {
            ""      : self.dummy,
            "list" : self.list,
            "list-kinds" : self.list_kinds,
            "list-couples" : self.list_couples,
            "list-couples-kinds" : self.list_couples_names,
            "show-price" : self.show_price,
            "show-prices" : self.show_prices,
            "set-price" : self.set_price,
            "temp-info" : self.temp_info,
            "temp-infos" : self.temp_infos,
            "set-desired-temp" : self.set_desired_temp,
            "get-fridge-alarm-states" : self.get_fridge_alarm_states,
            "get-fridge-alarm-state" : self.get_fridge_alarm_state,
            "set-fridge-alarm-state" : self.set_fridge_alarm_state,
            "shelf-info" : self.shelf_info,
            "shelf-infos" : self.shelf_infos,
            "info" : self.info,
            "exit" : self.close
        }
        print(green("paciollen@smart_supermarket") +":" + red("collector") + "$ ", end="")
        command_string = input()

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

    def list_couples_names(self, param):
        print("The recognised couples' kinds are:" + str(COUPLES_KINDS_LIST).replace('[','').replace(']',''))
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
            print("NodeID\t\t\tNode Kind")

        #now in nodes_info we have a dict made in this way--- "node_id" : "kind"
        assert isinstance(nodes_info, dict)

        for node_id in nodes_info:
            row = bold(node_id) + "\t\t\t" + colored_print_kind(nodes_info[node_id])
            print(row)

        return

    def list_couples(self, param):
        """
        list-couples                        -> lists all the couples of every couple kind
        list-couples  --kind COUPLE-KIND    -> lists all the couples of the specified kind
        list-couples  --spare               -> lists all the PriceDisplay / ScaleDevice / FridgeTempSensor / FridgeAlarmLight spare nodes
        list-couples  --spare KIND          -> lists all the spare nodes of specific kind
        """
        ALLOWED_OPTIONS = ["--spare", "--kind"]

        assert isinstance(param, list)
        if(len(param)):
            #the case in which the user has wrote some parameter after the command
            option = param[0]
            if option not in ALLOWED_OPTIONS:
                print("[!] list command: unrecognised option '" + option +"'!")
                return
            elif(option == "--spare"):
                #if it is a recognised option
                desired_kind = "any"

                print_condition = ""

                if len(param) > 1:
                    #we expect a specific kind as second parameter
                    desired_kind = param[1]
                    ALLOWED_KINDS = [SHELF_SCALE, PRICE_DISPLAY, FRIDGE_TEMPERATURE_SENSOR, FRIDGE_ALARM_LIGHT]
                    if desired_kind not in ALLOWED_KINDS:
                        print("[!] list-couples --spare command: kind '" + desired_kind +"' not allowed!")
                        print("[+] allowed kinds: " + str(ALLOWED_KINDS).replace('[','').replace(']',''))
                        return
                    print_condition = " of kind '"+colored_print_kind(desired_kind)+"'"
                
                nodes_info = collector.list_spare_devices(desired_kind = desired_kind)
                print("list of spare devices"+print_condition+":\n")

            elif(option == "--kind"):
                if(len(param) < 2):
                    print("[!] list-couples --kind needs you to specify the couple kind!")
                    print("[+] allowed couples names:\n")
                    self.list_couples_names()
                    return
                couple_kind = param[1]
                if couple_kind not in COUPLES_KINDS_LIST:
                    print("[!] '" + couple_kind + "'is not a valid couple kind!")
                    print("[+] allowed couples names:\n")
                    self.list_couples_names(param=None)
                    return
                
                couples_dict = collector.list_couples()

                requested_couples = couples_dict[couple_kind]

                couple_header = COUPLES_NAMES_DICT[couple_kind]

                print(couple_header + ":")

                for couple in requested_couples:
                    print(couple[0] + "\t\t\t\t" + couple[1])

                return

            
            #now in nodes_info we have a dict made in this way--- "node_id" : "kind"
            assert isinstance(nodes_info, dict)
            #sort by kind:
            nodes_info = dict(sorted(nodes_info.items(), key=lambda item: item[1]))

            for node_id in nodes_info:
                row = node_id + "\t\t\t" + colored_print_kind(nodes_info[node_id])
                print(row)


        else:
            #we want to list the node couples
            couples_dict = collector.list_couples()
            print("list of all the couples:\n")
            for couples_name in couples_dict.keys():
                couple_header = COUPLES_NAMES_DICT[couples_name]
                print(couple_header + ":")
                couples_of_certain_kind = couples_dict[couples_name]
                for couple in couples_of_certain_kind:
                    print(couple[0] + "\t\t\t\t" + couple[1])

                print()
        return

    def show_price(self, param):
        """
        show-price ID               -> if ID is the ID of a PriceDisplay, returns the current_price shown by that node
        """
        if(len(param) < 1):
            print("[!] please specify a nodeID!")
            return
        target_node_id = param[0]
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        if(node_infos["kind"] != PRICE_DISPLAY):
            print("[!] the node of ID " + target_node_id + " is not a PriceDisplay!")
            return
        current_price = collector.get_current_price(node_id = target_node_id)

        if current_price == False:
            print("[!]get_current_price: an error occurred in the collector")
            return
        else:
            print("The current price for the node of ID " + target_node_id + " is " + str(current_price))

        return

    def show_prices(self, param):
        """
        show-prices                 -> returns the current_price for each PriceDisplay node
        """

        print("list of all the PriceDisplay nodes")
        print("NodeID\t\t\tNode Current Price")

        price_device_infos = collector.get_all_prices()
        for node_id in price_device_infos:
            row = bold(node_id) + "\t\t\t" + blue(str(price_device_infos[node_id]))
            print(row)

        return

    def set_price(self, param):
        assert isinstance(param, list)
        if len(param) < 2:
            print("[!] set-price: missing parameter!")
            print("[+] set-price expected syntax: set-price NODE-ID DESIRED-PRICE")
            return
        target_node_id = param[0]
        #here we have to check that the specified node_id is actually a node_id of a connected PriceDisplay
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        if(node_infos["kind"] != PRICE_DISPLAY):
            print("[!] the node of ID " + target_node_id + " is not a PriceDisplay!")
            return
        
        new_desired_price = float(param[1])

        ret = collector.set_new_price(node_id=target_node_id, new_price=new_desired_price)

        if not ret:
            print("[!]set_price: an error occurred in the collector")

        return

    def temp_info(self, param):
        """
        temp-info ID               -> if ID is the ID of a FridgeTempSensor, returns the current_temp acquired by that node
        """
        if(len(param) < 1):
            print("[!] please specify a nodeID!")
            return
        target_node_id = param[0]
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        if(node_infos["kind"] != FRIDGE_TEMPERATURE_SENSOR):
            print("[!] the node of ID " + target_node_id + " is not a FridgeTempSensor!")
            return
        fridge_infos = collector.get_fridge_sensor_info(node_id = target_node_id)

        if fridge_infos == False:
            print("[!]temp-info: an error occurred in the collector")
            return
        else:
            print("The current temperature for the node of ID " + target_node_id + " is " + str(fridge_infos["current_temp"]))
            print("The desired temperature for the node of ID " + target_node_id + " is " + str(fridge_infos["desired_temp"]))
        return

    def temp_infos(self, param):
        """
        temp_infos          ->  returns current temperature and desired temperature for each connected FridgeTemperatureSensor
        """
        print("list of all the FridgeTemperature nodes")
        print("NodeID\t\t\tNode Current Temperature\t\t\tNode Desired Temperature")

        fridge_devices_infos = collector.get_all_temperatures()
        for node_id in fridge_devices_infos:
            current_temp = fridge_devices_infos[node_id]["current_temp"]
            desired_temp = fridge_devices_infos[node_id]["desired_temp"]
            row = bold(node_id) + "\t\t\t\t" + blue(str(current_temp)) + "\t\t\t\t\t" + purple(str(desired_temp))
            print(row)
        
        return
    
    def set_desired_temp(self, param):
        """
        set-desired-temp ID value   -> if ID is the ID of a FridgeTemperatureSensor, set a new desired temperature for that node
        """

        assert isinstance(param, list)
        if len(param) < 2:
            print("[!] set_desired_temp: missing parameter!")
            print("[+] set_desired_temp expected syntax: set-price NODE-ID DESIRED-TEMPERATURE")
            return
        target_node_id = param[0]
        #here we have to check that the specified node_id is actually a node_id of a connected FridgeTemperatureSensor
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        if(node_infos["kind"] != FRIDGE_TEMPERATURE_SENSOR):
            print("[!] the node of ID " + target_node_id + " is not a FridgeTemperatureSensor!")
            return
        
        new_desired_temp = float(param[1])

        ret = collector.set_new_temperature(node_id=target_node_id, new_temp=new_desired_temp)

        if not ret:
            print("[!]set_desired_temperature: an error occurred in the collector")
        return

    def get_fridge_alarm_states(self, param):
        """
        get-fridge-alarm-states            -> returns current alarm state and last state change for each connected FridgeAlarmLight
        """
        print("list of all the " + colored_print_kind(FRIDGE_ALARM_LIGHT) + " nodes")
        print("NodeID\t\t\tNode Current State\t\t\tLast state change")

        fridge_devices_infos = collector.get_all_fridge_alarm_states()
        for node_id in fridge_devices_infos:
            current_state = fridge_devices_infos[node_id]["current_state"]
            last_state_change = fridge_devices_infos[node_id]["last_state_change"]
            row = bold(node_id) + "\t\t\t\t" + blue(str(current_state)) + "\t\t\t\t\t" + purple(str(last_state_change))
            print(row)
        return

    def get_fridge_alarm_state(self, param):
        """
        get-fridge-alarm-state  ID         -> if ID is the ID of a FridgeAlarmState, returns current alarm state and last state change for that FridgeAlarmLight
        """
        if(len(param) < 1):
            print("[!] please specify a nodeID!")
            return
        target_node_id = param[0]
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        if(node_infos["kind"] != FRIDGE_ALARM_LIGHT):
            print("[!] the node of ID " + target_node_id + " is not a " + colored_print_kind(FRIDGE_ALARM_LIGHT) + "!")
            return
        fridge_alarm_infos = collector.get_fridge_alarm_state(node_id = target_node_id)

        if fridge_alarm_infos == False:
            print("[!]get-fridge-alarm-state: an error occurred in the collector")
            return
        else:
            print("The current state for the node of ID " + target_node_id + " is " + str(fridge_alarm_infos["current_state"]))
            print("The last state change for the node of ID " + target_node_id + " is " + str(fridge_alarm_infos["last_state_change"]))
        return

    def set_fridge_alarm_state(self, param):
        """
        set-fridge-alarm-state  ID VALUE   -> if ID is the ID of a FridgeAlarmState and if VALUE is one of ["ON", "OFF"] sets alarm state for that FridgeAlarmLight
        """

        ALLOWED_STATES = ["ON", "OFF"]

        if len(param) < 2:
            print("[!] set-fridge-alarm-state: missing parameter!")
            print("[+] set-fridge-alarm-state expected syntax: set-fridge-alarm-state NODE-ID STATE")
            return
        target_node_id = param[0]
        #here we have to check that the specified node_id is actually a node_id of a connected FridgeAlarmLight
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        if(node_infos["kind"] != FRIDGE_ALARM_LIGHT):
            print("[!] the node of ID " + target_node_id + " is not a " + colored_print_kind(FRIDGE_ALARM_LIGHT) + "!")
            return
        
        new_desired_state = param[1]

        if new_desired_state not in ALLOWED_STATES:
            print("[!] STATE can be one of \"ON\" or \"OFF\"")
            return


        ret = collector.set_fridge_alarm_state(node_id=target_node_id, new_state=new_desired_state)

        if not ret:
            print("[!]set_desired_temperature: an error occurred in the collector")
        return

    def shelf_info(self, param):
        """
        shelf-info ID               -> if ID is the ID of a ShelfScaleDevice, returns current weight, number of refills and last refill timestamp of that sensor
        """
        if(len(param) < 1):
            print("[!] please specify a nodeID!")
            return
        target_node_id = param[0]
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        if(node_infos["kind"] != SHELF_SCALE):
            print("[!] the node of ID " + target_node_id + " is not a ShelfScaleDevice!")
            return
        shelf_scale_infos = collector.get_scale_info(node_id = target_node_id)

        if shelf_scale_infos == False:
            print("[!]shelf-info: an error occurred in the collector")
            return
        else:
            print("The current weight for the node of ID " + target_node_id + " is " + str(shelf_scale_infos["current_weight"]))
            print("The number of refills for the node of ID " + target_node_id + " is " + str(shelf_scale_infos["number_of_refills"]))
            print("The last refill timestamp for the node of ID " + target_node_id + " is " + str(shelf_scale_infos["last_refill_ts"]))
        return

    def shelf_infos(self, param):
        print("list of all the ShelfScaleDevice nodes")
        print("NodeID\t\t\tCurrent Weight\t\t\tRefills Counter\t\t\tLast Refill")

        scale_devices_infos = collector.get_all_scales_infos()
        for node_id in scale_devices_infos:
            current_weight = scale_devices_infos[node_id]["current_weight"]
            number_of_refills = scale_devices_infos[node_id]["number_of_refills"]
            last_refill_ts = scale_devices_infos[node_id]["last_refill_ts"]
            row = bold(node_id) + "\t\t\t\t" + blue(str(current_weight)) + "\t\t\t\t" + purple(str(number_of_refills)) + "\t\t\t" + green(str(last_refill_ts))
            print(row)
        return

    def info(self, param):
        if(len(param) < 1):
            print("[!] please specify a nodeID!")
            return
        target_node_id = param[0]
        node_infos = collector.node_info(target_node_id)
        if(node_infos == False):
            print("[!] the ID " + target_node_id + " does not identify any connected node!")
            return
        print(str(node_infos))
        return

    def dummy(self, param):
        return

    def close(self, param):
        print("Now you can press CTRL + C")
        #stop_collector()
        #raise KeyboardInterrupt

    