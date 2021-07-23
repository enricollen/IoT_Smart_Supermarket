#include "coap-blocking-api.h"

//#include "routing/routing.h"

#define CONNECTION_TRY_INTERVAL 1
#define REGISTRATION_TRY_INTERVAL 5
#define SERVER_EP "coap://[fd00::1]:5683"

#define REGISTRATION_SUCCESSFULL "Registration Successfull"
#define ALREADY_REGISTERED "Already Registered"
#define WRONG_PAYLOAD "Invalid Sensor Type"

static struct etimer wait_connectivity_timer;
static struct etimer wait_registration;
static bool registered = false;
static char* service_url = "/register";
static coap_endpoint_t server_ep;
static coap_message_t request[1]; /* This way the packet can be treated as pointer as usual. */

#define CLIENT_ID_SIZE 6
char sensor_id[CLIENT_ID_SIZE];

static bool have_connectivity(void)
{
  if(uip_ds6_get_global(ADDR_PREFERRED) == NULL ||
     uip_ds6_defrt_choose() == NULL) {
    return false;
  }
  return true;
}

void wait_connectivity(){
    etimer_set(&wait_connectivity_timer, CLOCK_SECOND* CONNECTION_TRY_INTERVAL);
    while(!have_connectivity()){
        PROCESS_WAIT_UNTIL(etimer_expired(&wait_connectivity_timer));
        etimer_reset(&wait_connectivity_timer);
    }
    LOG_DBG("[%.*s]: Successfully connected to network");
}

bool initialize_node_id(){
    if(!have_connectivity())
      return false;
    
    snprintf(sensor_id, CLIENT_ID_SIZE, "%02x%02x%02x", 
          linkaddr_node_addr.u8[5], linkaddr_node_addr.u8[6], linkaddr_node_addr.u8[7]);
    return true;
}

void client_chunk_handler(coap_message_t *response)
{
	const uint8_t *chunk;
	if(response == NULL) {
		LOG_INFO("Request timed out\n");
		etimer_set(&wait_registration, CLOCK_SECOND* REGISTRATION_TRY_INTERVAL);
		return;
	}
	
	int len = coap_get_payload(response, &chunk);
	printf("|%.*s", len, (char *)chunk);

	if(strncmp((char*)chunk, REGISTRATION_SUCCESSFULL, len) == 0){ 
		registered = true;
	}
    else if(strncmp((char*)chunk, ALREADY_REGISTERED, len) == 0){
        registered = true;
    }
    else if(strncmp((char*)chunk, WRONG_PAYLOAD, len) == 0){
        registered = false;
        LOG_ERR("[network_config: client_chunk_handler] Invalid node type\n");
    }  
    else
		etimer_set(&wait_registration, CLOCK_SECOND* REGISTRATION_TRY_INTERVAL);
}

void register_to_collector(){
    while(!registered){
		
		coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &server_ep);	

		coap_init_message(request, COAP_TYPE_CON, COAP_POST, 0);
		coap_set_header_uri_path(request, service_url);
			
		coap_set_payload(request, (uint8_t *)SENSOR_TYPE, sizeof(SENSOR_TYPE) - 1);
		COAP_BLOCKING_REQUEST(&server_ep, request, client_chunk_handler);
		
        PROCESS_WAIT_UNTIL(etimer_expired(&wait_registration));
  }
}

