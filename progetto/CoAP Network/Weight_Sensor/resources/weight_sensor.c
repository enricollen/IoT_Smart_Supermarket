#include "contiki.h"
#include "coap-engine.h"
//#include "dev/leds.h"
#include <string.h>

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

extern long current_weight;
extern char sensor_id[];

//static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_weight_obs_handler(void);

EVENT_RESOURCE(res_weight,
		"title=\"weight value\";obs",
		res_get_handler,
		NULL,
		NULL,
		NULL,
		res_weight_obs_handler);

//risposta alla get standard
static void
res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
	coap_set_header_content_format(response, APPLICATION_JSON);
	snprintf((char *)buffer, COAP_MAX_CHUNK_SIZE, "{\"weight\": %ld, \"now\": %lu, \"id\": \"%s\"}", current_weight, clock_seconds(), sensor_id);
    coap_set_payload(response, (uint8_t *)buffer, strlen((char *)buffer));
}

//handler dell'observing
static void res_weight_obs_handler(void)
{
	// Notify all the observers
	// Before sending the notification the handler associated with the GET methods is called
	//chiama la get qui
	coap_notify_observers(&res_weight);
}