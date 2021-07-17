#include "contiki.h"
#include "coap-engine.h"
//#include "dev/leds.h"
#include <string.h>

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

//maybe it is better to create a globals.h file for those things
extern long last_price_change;
extern float current_price;
extern void change_price(float updated_price);
extern bool check_price_validity(float price);
//--------------------------------------------------------------

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);
static void res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset);

EVENT_RESOURCE(res_price,
		"title=\"price handler\";",
		res_get_handler,
		res_post_put_handler,
		res_post_put_handler,
		NULL,
		NULL);


static void
res_get_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset)
{
	coap_set_header_content_format(response, APPLICATION_JSON);
	snprintf((char *)buffer, COAP_MAX_CHUNK_SIZE, "{\"price\": %.2f, \"current_ts\": %lu, \"last_change_ts\": %lu}", current_price, clock_seconds(), last_price_change);
    coap_set_payload(response, (uint8_t *)buffer, strlen((char *)buffer));
}

static void res_post_put_handler(coap_message_t *request, coap_message_t *response, uint8_t *buffer, uint16_t preferred_size, int32_t *offset){

	if(request != NULL) {
		LOG_DBG("POST Request Received\n");
	}

	//check if in the body of the request is present "new_price", parse float and updates the current_price

	size_t len = 0;
	const char *new_price_str = NULL;
	float new_price = 0;
	int success = 1;
	bool is_acceptable = 0;



	if((len = coap_get_post_variable(request, "new_price", &new_price_str))) {

		//use atof() to parse float from the received string		| atof() is from <string.h> library
		new_price = atof(new_price_str);

		//we need to check if the received price is acceptable
		is_acceptable = check_price_validity(new_price);
		
		LOG_DBG("[price-resource | POST/PUT HANDLER] received 'new_price' | str_value : %.*s \t float_value : %f\n", (int)len, new_price_str, new_price);
		
		if( is_acceptable ) {
			//do update
			change_price(new_price);

		} else {
			success = 0;
			LOG_DBG("[price-resource | POST/PUT HANDLER] ERROR: the received price is not acceptable");
		}

	} else {
		//if len of post variable "new_price" is 0
		success = 0;
		LOG_DBG("[price-resource | POST/PUT HANDLER] ERROR: missing required parameter 'new_price'");
	}
	
	if(!success) {
		coap_set_status_code(response, BAD_REQUEST_4_00);
		return;
	}

	snprintf((char *)buffer, COAP_MAX_CHUNK_SIZE, "{\"price_updated\": true, \"last_change_ts\": %lu}", last_price_change);
	coap_set_payload(response, (uint8_t *)buffer, strlen((char *)buffer));

}