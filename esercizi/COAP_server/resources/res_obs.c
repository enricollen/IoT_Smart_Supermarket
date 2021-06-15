#include "contiki.h"
#include "coap-engine.h"
#include "dev/leds.h"

#include <string.h>

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_event_handler(void);

EVENT_RESOURCE(res_event,
		"title=\"Event demo\";obs",
		res_get_handler,
		NULL,
		NULL,
		NULL,
		res_event_handler);

static int counter = 0;

//risposta alla get standard
static void
res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
	coap_set_header_content_format(response, TEXT_PLAIN);
  	coap_set_payload(response, buffer, snprintf((char *)buffer, preferred_size, "EVENT %lu", (unsigned long) counter));
}

//handler dell'observing
static void res_event_handler(void)
{
	// Notify all the observers
	// Before sending the notification the handler associated with the GET methods is called
	counter++;
	//chiama la get qui
	coap_notify_observers(&res_event);
}
