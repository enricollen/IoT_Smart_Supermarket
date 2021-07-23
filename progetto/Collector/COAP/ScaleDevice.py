import WeightSensor
import RefillSensor

class ScaleDevice:
    
    weight_sensor = 0
    refill_sensor = 0   
    linked_price_display = ""
    ip_addr = ""

    def __init__(self, ip_addr):
        self.weight_sensor = WeightSensor(ip_addr)
        self.refill_sensor = RefillSensor(ip_addr)
        self.ip_addr = ip_addr
    
    def bind_price_display(self, price_display_ip):
        if(self.linked_price_display!=""):
            logging.warning("[ScaleDevice: bind_scale_device] Scale Device has already been associated with Price Display")
            return False

        self.linked_price_display = price_display_ip