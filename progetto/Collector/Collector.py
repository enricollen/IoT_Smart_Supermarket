from PriceDisplay import PriceDisplay

PRICE_DISPLAY = "price_display"
#TO DO:
#this class should be static so that we 
class Collector:
    price_display_array = []
    #array of PriceDisplays
    #...
    devices = {}    #key: ip | value: kind_of_device

    def register_new_COAP_device(self, ip_addr, kind):
        self.devices[ip_addr] = kind
        return self
    
    def connected_ip_list(self):
        return list( self.devices.keys() )

    def register_new_price_display(self, ip_addr):

        try:
            price_display = PriceDisplay()
        except:
            return False

        self.register_new_COAP_device(self, ip_addr, PRICE_DISPLAY)

        self.price_display_array.append(price_display)

        return self

    def register_new_weight_sensor(self, ip_addr):
        pass


collector = Collector()