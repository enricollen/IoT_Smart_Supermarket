from DatabaseConnection import DatabaseConnection
from abc import ABC, abstractmethod

#classe astratta con alcuni metodi da implementare

class COAPModel:
    ip_address = ""
    is_observable = False

    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.get_current_state()
        if(self.is_observable()):
            self.start_observing(self.observe_handler)

    def is_observable(self):
        return self.is_observable

    @abstractmethod #not sure if it should be abstract or not
    def start_observing(self, observe_handler):
        #TO DO:
        #implement COAPthon method to register as observer and bind observe_handler to handle notifies
        pass

    @abstractmethod #not sure if it should be abstract or not
    def observe_handler(self):
        #TO DO:
        #in some ways receives current node state, update object state and stores it in the database
        pass

    @abstractmethod
    def get_current_state(self):
        pass

    @abstractmethod
    def set_new_values(self):
        pass

    @abstractmethod
    def save_current_state(self):
        pass

    