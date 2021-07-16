#include "contiki.h"
#include "coap-engine.h"
//#include "dev/leds.h"
#include <string.h>

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

extern long last_refill_ts;
extern void refill_shelf();

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_refill_obs_handler(void);

EVENT_RESOURCE(res_refill,
		"title=\"weight value\";obs",
		res_get_handler,
		NULL,
		NULL,
		NULL,
		res_refill_obs_handler);

//risposta alla get standard
static void
res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
	coap_set_header_content_format(response, APPLICATION_JSON);
	snprintf((char *)buffer, COAP_MAX_CHUNK_SIZE, "{\"current_ts\": %lu, \"last_refill_ts\": %lu, \"unit\": \"seconds\"}", clock_seconds(), last_refill_ts);
    coap_set_payload(response, (uint8_t *)buffer, strlen((char *)buffer));
}

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){

	//check if in the body of the request "refill" == true

	if(request != NULL) {
		LOG_DBG("POST Request Received\n");
	}
		
	size_t len = 0;
	const char *refill = NULL;
	int success = 1;

	if((len = coap_get_query_variable(request, "refill", &refill))) {
		LOG_DBG("refill %.*s\n", (int)len, refill);
		
		if(strncmp(refill, "ON", len) == 0 || strncmp(refill, "on", len) == 0  ) {
			
			//do refill
			refill_shelf();
			
		} else if( strncmp(refill, "OFF", len) == 0 || strncmp(refill, "off", len) == 0 ){

			success = 1;

		} else {
			success = 0;
		}

	} else {
		//if len of query variable "refill" is 0
		success = 0;
	}
	
	if(!success) {
		coap_set_status_code(response, BAD_REQUEST_4_00);
		return;
	}

	memset(buffer, 0x0, sizeof(buffer));
	snprintf((char *)buffer, COAP_MAX_CHUNK_SIZE, "{\"refilled\": true, \"last_refill_ts\": %lu, \"unit\": \"seconds\"}", last_refill_ts);
	coap_set_payload(response, (uint8_t *)buffer, strlen((char *)buffer));

}

//handler dell'observing
static void res_refill_obs_handler(void)
{
	// Notify all the observers
	// Before sending the notification the handler associated with the GET methods is called
	//chiama la get qui
	coap_notify_observers(&res_refill);
}
