#include "contiki.h"
#include "coap-blocking-api.h"

#define WAITING_NETWORK 0
#define CONNECTED_TO_NETWORK 1
#define CONNECTED_TO_COLLECTOR 2

uint8_t status = WAITING_NETWORK;

#define CHECK_STATUS_PERIOD 30

static struct etimer status_check;

#define CONNECTION_TRY_INTERVAL 1
#define REGISTRATION_TRY_INTERVAL 10
#define SERVER_EP "coap://[fd00::1]:5683"

#define REGISTRATION_SUCCESSFULL "Registration Successfull"
#define ALREADY_REGISTERED "Already Registered"
#define NOT_REGISTERED "Not registered"
#define WRONG_PAYLOAD "Invalid Sensor Type"
#define INTERNAL_SERVER_ERROR "Internal error while handling the request"

static struct etimer wait_connectivity_timer;
static struct etimer wait_registration;

static bool registered = false;
static char* service_url = "/register";
static coap_endpoint_t server_ep;
static coap_message_t request[1];

#define CLIENT_ID_SIZE 6 + 1 //becaus of \0
char sensor_id[CLIENT_ID_SIZE];
bool id_initialized = false;

static bool have_connectivity(void)
{
  if(uip_ds6_get_global(ADDR_PREFERRED) == NULL ||
     uip_ds6_defrt_choose() == NULL) {
    return false;
  }
  return true;
}

bool initialize_node_id(){
    if(id_initialized)
      return true;
    if(!have_connectivity())
      return false;
    
    snprintf(sensor_id, CLIENT_ID_SIZE, "%02x%02x%02x", 
          linkaddr_node_addr.u8[5], linkaddr_node_addr.u8[6], linkaddr_node_addr.u8[7]);
    id_initialized = true;
    return true;
}

void client_status_checker(coap_message_t * response){
  const uint8_t * chunk = NULL;
  if(response == NULL){
    LOG_INFO("[client_status_checker]: Request timed out\n");
		status = WAITING_NETWORK;
    registered = false;
		return;
  }
  int len = coap_get_payload(response, &chunk);
	LOG_INFO("[client_status_checker]: payload len = %d | payload: %s\n", len, (char * ) chunk);
  
	if(strncmp((char*)chunk, ALREADY_REGISTERED, len) == 0){ 
		LOG_INFO("[client_status_checker]: ping ok\n");
	}
  else if(strncmp((char*)chunk, NOT_REGISTERED, len) == 0){
    status = CONNECTED_TO_NETWORK;
    registered = false;
  }
}



void client_chunk_handler(coap_message_t * response)
{
	const uint8_t *chunk = NULL;
	if(response == NULL) {
		LOG_INFO("Request timed out\n");
		return;
	}
	int len = coap_get_payload(response, &chunk);
	LOG_INFO("[client_chunk_handler]: called coap_get_payload. len = %d | payload: %s\n", len, (char * ) chunk);
  
	if(strncmp((char*)chunk, REGISTRATION_SUCCESSFULL, len) == 0){ 
		registered = true;
	}
    else if(strncmp((char*)chunk, ALREADY_REGISTERED, len) == 0){
        registered = true;
    }
    else if(strncmp((char*)chunk, WRONG_PAYLOAD, len) == 0){
        registered = false;
        LOG_ERR("[network_config: client_chunk_handler] Invalid node type\n");
    }else if(strncmp((char*)chunk, INTERNAL_SERVER_ERROR, len) == 0){
        registered = false;
        LOG_ERR("[network_config: client_chunk_handler] Collector internal error!\n");
    }else{
      LOG_WARN("[client_chunk_handler]: unrecognized response from Collector\n");
      registered = false;
    }
}
/*
inline void wait_connectivity(){
    etimer_set(&wait_connectivity_timer, CLOCK_SECOND* CONNECTION_TRY_INTERVAL);
    while(!have_connectivity()){
        //Important NOTE: we cannot use the macro PROCESS_WAIT_UNTIL inside a function, beacause in this way the compiler does not see the process_pt and raises an error
          //src: https://groups.google.com/g/osdeve_mirror_rtos_contiki-developers/c/XdOXnXsgj38
        //PROCESS_WAIT_UNTIL(etimer_expired(&wait_connectivity_timer));
        //etimer_reset(&wait_connectivity_timer);
        //searching online it seems that the best way to achieve this is to use a ctimer
          //new note: the ctimer does not fit our case because we want to block the execution of the process, we do not want it to go to the next state (when the network is ok)
            //the best way we've found is to copy paste this code directly in the process_Thread
    }
    LOG_DBG("[%.*s]: Successfully connected to network");
}
*/
/*
DOES NOT WORK BECAUSE COAP_BLOCKING_REQUEST CANNOT BE CALLED INSIDE A FUNCTION
*/
