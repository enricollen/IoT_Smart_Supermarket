from PriceDisplay import PriceDisplay
from ScaleDevice import ScaleDevice

PRICE_DISPLAY = "price_display"
SHELF_SCALE = "shelf_scale"

#TO DO:
#this class should be static
class Collector:
    price_display_array = [] #array of PriceDisplays
    shelf_scale_device_array = [] # [ScaleDevice1, ScaleDevice2...]
    coupled_scale_and_price = [] # [[Scale1, Price1], [Scale2, Price2], ...]
    
    devices = {}    #key: ip | value: kind_of_device

    def register_new_COAP_device(self, ip_addr, kind):
        self.devices[ip_addr] = kind
        return self
    
    def connected_ip_list(self):
        return list( self.devices.keys() )

    def register_new_price_display(self, ip_addr):

        try:
            price_display = PriceDisplay(ip_addr)
        except:
            return False

        self.register_new_COAP_device(self, ip_addr, PRICE_DISPLAY)

        self.price_display_array.append(price_display)

        #logic for binding a weight sensor with correspondent price display
        bind_price_and_scale(ip_addr_price_display=ip_addr) 

        return self

    def register_new_scale_device(self, ip_addr):
        try:
            scale_device = ScaleDevice(ip_addr)
        except:
            return False

        self.register_new_COAP_device(self, ip_addr, SHELF_SCALE)

        self.shelf_scale_device_array.append(scale_device)

        #logic for binding a weight sensor with correspondent price display
        bind_price_and_scale(ip_addr_scale_device=ip_addr) 

        return self

    #utility array to make bind prcess easier
    spare_price_displays = [] 
    spare_scale_devices = []

    def bind_price_and_scale(self, ip_addr_price_display="", ip_addr_scale_device=""):
        if ip_addr_price_display!="": #we want to bind price display with a spare scale device
            if len(spare_scale_devices)==0:
                spare_price_displays.append(ip_addr_price_display)
                return
            else:
                ip_addr_scale_device = spare_scale_devices.pop()
                coupled_scale_and_price.append([ip_addr_scale_device, ip_addr_price_display])

        if ip_addr_scale_device!="": #we want to bind scale device with a spare price display
            if len(spare_price_displays)==0:
                spare_scale_devices.append(ip_addr_scale_device)
                return
            else:
                ip_addr_price_display = spare_price_displays.pop()
                coupled_scale_and_price.append([ip_addr_scale_device, ip_addr_price_display])


collector = Collector()