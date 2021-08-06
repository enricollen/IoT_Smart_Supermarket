PRICE_DISPLAY = "price_display"
SHELF_SCALE = "shelf_scale"
FRIDGE_TEMPERATURE_SENSOR = "fridge_temp_sensor"

KINDS_LIST = [PRICE_DISPLAY, SHELF_SCALE, FRIDGE_TEMPERATURE_SENSOR]

KIND_NOT_RECOGNISED = "kind not recognised"
NO_CHANGE = "fenom"

CANNOT_PARSE_JSON = "landrier"

#----------------------------------------------


REGISTRATION_SUCCESSFULL = "Registration Successfull"
ALREADY_REGISTERED = "Already Registered"
NOT_REGISTERED = "Not registered"
WRONG_PAYLOAD = "Invalid Sensor Type"
INTERNAL_ERROR = "Internal error while handling the request"

ADDRESS_ALREADY_IN_USE = "Address already in use"
#----------------------------------------------

DEFAULT_STYLE = "\033[0;37;40m" #white
RED_STYLE = "\033[1;31;40m"
GREEN_STYLE = "\033[1;32;40m"
YELLOW_STYLE = "\033[1;33;40m"
BLUE_STYLE = "\033[1;34;40m"
PURPLE_STYLE = "\033[1;35;40m"
CYAN_STYLE = "\033[1;36;40m"

BLACK_COLOR = "\033[90m"
RED_COLOR = "\033[91m"
GREEN_COLOR = "\033[92m"
YELLOW_COLOR = "\033[93m"
BLUE_COLOR = "\033[94m"
PURPLE_COLOR = "\033[95m"
CYAN_COLOR = "\033[96m"
WHITE_COLOR = "\033[97m"
DEFAULT_COLOR = WHITE_COLOR

BOLD_STYLE = "\033[1m"
UNDERLINE_STYLE = "\033[2m"
ITALIC_STYLE = "\033[3m"
STOP_STYLE = "\033[0m"

def underline(string):
    return UNDERLINE_STYLE + string + STOP_STYLE

def bold(string):
    return BOLD_STYLE + string + STOP_STYLE

def italic(string):
    return ITALIC_STYLE + string + STOP_STYLE

def green(string):
    return GREEN_COLOR + string + DEFAULT_COLOR

def red(string):
    return RED_COLOR + string + DEFAULT_COLOR

def blue(string):
    return BLUE_COLOR + string + DEFAULT_COLOR