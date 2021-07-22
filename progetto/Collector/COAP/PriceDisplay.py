from COAPModel import COAPModel

DEFAULT_PRICE = 10.0

class PriceDisplay(COAPModel):
    
    current_price = DEFAULT_PRICE

    def get_current_state(self):
        return super().get_current_state()