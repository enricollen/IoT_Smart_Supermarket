#include "contiki.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "sys/etimer.h"
#include <time.h>


#include "node-id.h"
#include "net/ipv6/simple-udp.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/uip-ds6.h"
#include "net/ipv6/uip-debug.h"
#include "routing/routing.h"

#define SENSOR_TYPE "PriceDisplay"
const char* node_name = "Price Display and CoAP Server";
#include "../network_config.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

#define DEFAULT_PRICE 20.5
#define MINIMUM_PRICE 0.90

/* Declare and auto-start this file's process */
PROCESS(contiki_ng_br_coap_server, "[Price Display and CoAP Server]: exposed resources: '/price'");
AUTOSTART_PROCESSES(&contiki_ng_br_coap_server);

extern coap_resource_t res_price;

//------------------------------
//SENSOR INFOS:
//those are initialized inside PROCESS_THREAD
float current_price = 0;
long last_price_change = -1; 
//------------------------------

void change_price(float updated_price){

  //refill the shelf
  current_price = updated_price;

  //saves the last refill timestamp
  last_price_change = clock_seconds();

}

bool check_price_validity(float price){

  if(price < MINIMUM_PRICE){
    return false;
  }

  return true;
}

PROCESS_THREAD(contiki_ng_br_coap_server, ev, data){

  PROCESS_BEGIN();

  change_price(DEFAULT_PRICE);   //when the sensor is restarted, we reset the current price to DEFAULT PRICE

	coap_activate_resource(&res_price, "price");

  wait_connectivity();

  if(!initialize_node_id())
    LOG_ERR("[%.*s]: Unable to initialize Node ID", node_name);

  LOG_DBG("[%.*s]: up and running", node_name);

  register_to_collector();

  LOG_DBG("[%.*s]: Registration to Collector succeded", node_name);
		
  PROCESS_END();
}
