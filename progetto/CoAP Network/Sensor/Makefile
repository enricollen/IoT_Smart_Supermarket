CONTIKI_PROJECT = coap-server
all: $(CONTIKI_PROJECT)
CONTIKI = ../../../..

# The BR is either native or embedded, and in the latter case must support SLIP
PLATFORMS_EXCLUDE = nrf52dk z1
MODULES_REL += ./resources

MODULES += $(CONTIKI_NG_APP_LAYER_DIR)/coap

# Include optional target-specific module
include $(CONTIKI)/Makefile.identify-target
include $(CONTIKI)/Makefile.include
