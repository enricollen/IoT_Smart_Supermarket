#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "sys/etimer.h"
#include <time.h>

#include "net/ipv6/simple-udp.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/uip-ds6.h"
#include "net/ipv6/uip-debug.h"
#include "routing/routing.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "Shelf Scale"
#define LOG_LEVEL LOG_LEVEL_APP

#define SENSOR_TYPE "ShelfScale"
const char* node_name = "Weight&Refill Sensors and CoAP Server";
#include "../network_config.h"


#define MAX_WEIGHT 2000
#define MIN_WEIGHT 0
#define TRESHOLD_WEIGHT 200


/* Declare and auto-start this file's process */
PROCESS(contiki_ng_br_coap_server, "[Weight&Refill Sensors and CoAP Server]: exposed resources: '/weight', '/refill'"); //"Weight&Refill Sensors and CoAP Server"
AUTOSTART_PROCESSES(&contiki_ng_br_coap_server);
static struct etimer timer;

extern coap_resource_t res_weight;
extern coap_resource_t res_refill;

//------------------------------
//SENSOR INFOS:
//those are initialized inside PROCESS_THREAD
long current_weight = 0;
long last_refill_ts = -1; 
//------------------------------

void refill_shelf(){

  //refill the shelf
  current_weight = MAX_WEIGHT;

  
  //saves the last refill timestamp
  last_refill_ts = clock_seconds();

  LOG_INFO("[refill_shelf]: just refilled shelf (ts: %lu) | current_weight = %lu \n", last_refill_ts, current_weight);

  res_refill.trigger();

}

void measure_weight(){
  long previous = current_weight;
  current_weight = ( rand() % (current_weight - MIN_WEIGHT + 1) ) + MIN_WEIGHT; //the weight can only decrease by a random value

  LOG_INFO("[measure_weight] the weight has just changed to %ld | (previously %lu) \n", current_weight, previous);

  if(current_weight < TRESHOLD_WEIGHT){
    //internal automation that refills the shelf whenever it is nearly empty
    refill_shelf();

  }
}

PROCESS_THREAD(contiki_ng_br_coap_server, ev, data){

  PROCESS_BEGIN();

	coap_activate_resource(&res_weight, "weight");
  coap_activate_resource(&res_refill, "refill");

  refill_shelf();   //when the sensor is restarted, we reset the current weight to MAX_WEIGHT

  
  //wait_connectivity();
  etimer_set(&wait_connectivity_timer, CLOCK_SECOND* CONNECTION_TRY_INTERVAL);
    while(!have_connectivity()){
        PROCESS_WAIT_UNTIL(etimer_expired(&wait_connectivity_timer));
        etimer_reset(&wait_connectivity_timer);
    }
  LOG_DBG("[%.*s]: Successfully connected to network\n");
  //

  if(!initialize_node_id())
    LOG_ERR("[%.*s]: Unable to initialize Node ID\n", node_name);

  LOG_DBG("[%.*s]: up and running\n", node_name);

  //register_to_collector();
  etimer_set(&wait_registration, CLOCK_SECOND* REGISTRATION_TRY_INTERVAL);

  while(!registered){
		
		coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &server_ep);	
    
		coap_init_message(request, COAP_TYPE_CON, COAP_POST, 0);
		coap_set_header_uri_path(request, service_url);
			
		coap_set_payload(request, (uint8_t *)SENSOR_TYPE, sizeof(SENSOR_TYPE) - 1);
    //TO DO: it will be useful to make a non blocking request and / or decrease the CoAP connection timeout
		COAP_BLOCKING_REQUEST(&server_ep, request, client_chunk_handler);
    
		etimer_reset(&wait_registration);
    PROCESS_WAIT_UNTIL(etimer_expired(&wait_registration));
  }
  //


  LOG_DBG("[%.*s]: Registration to Collector succeded\n", node_name);
  
  etimer_set(&timer, 5*CLOCK_SECOND);

  while(1){
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    measure_weight();
    res_weight.trigger(); //calls obs_handler
    etimer_reset(&timer);
  }
	
  PROCESS_END();
}
