#include "contiki.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "coap-engine.h"
#include "sys/etimer.h"
#include <time.h>


#include "node-id.h"
#include "net/ipv6/simple-udp.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/uip-ds6.h"
#include "net/ipv6/uip-debug.h"
#include "routing/routing.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "PriceDisplay"
#define LOG_LEVEL LOG_LEVEL_APP

#define SENSOR_TYPE "PriceDisplay"
const char* node_name = "Price Display and CoAP Server";
#include "../network_config.h"



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

  //if you want to avoid error, please add a check to be sure that res_price is active!
  res_price.trigger(); //calls obs_handler

}

bool check_price_validity(float price){

  if(price < MINIMUM_PRICE){
    return false;
  }

  return true;
}

PROCESS_THREAD(contiki_ng_br_coap_server, ev, data){

  PROCESS_BEGIN();

	coap_activate_resource(&res_price, "price");
  //NOTE: you can call change_price only after the activation of res_price, because inside change_price there is a call to res_price.trigger();
  change_price(DEFAULT_PRICE);   //when the sensor is restarted, we reset the current price to DEFAULT PRICE

  etimer_set(&status_check, CLOCK_SECOND* CHECK_STATUS_PERIOD);
  while(true){
      //wait_connectivity();
      if(status == WAITING_NETWORK){
        LOG_INFO("Waiting connectivity...\n");
        etimer_set(&wait_connectivity_timer, CLOCK_SECOND* CONNECTION_TRY_INTERVAL);
          while(!have_connectivity()){
              PROCESS_WAIT_UNTIL(etimer_expired(&wait_connectivity_timer));
              etimer_reset(&wait_connectivity_timer);
          }
        LOG_DBG("[%.*s]: Successfully connected to network\n");
        status = CONNECTED_TO_NETWORK;
      }
      //
      if(status == CONNECTED_TO_NETWORK){
          if(id_initialized == false)
            if(!initialize_node_id())
              LOG_ERR("[%.*s]: Unable to initialize Node ID\n", node_name);

          LOG_INFO("[%.*s]: Connected to network\n", node_name);
      
          //register_to_collector();
          LOG_INFO("Connecting to collector...\n");
          
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
          status = CONNECTED_TO_COLLECTOR;
          LOG_INFO("[%.*s]: Registration to Collector succeded\n", node_name);
          //
      }
      if(status == CONNECTED_TO_COLLECTOR){
          //we want to ping the collector to check the presence of this node
          coap_endpoint_parse(SERVER_EP, strlen(SERVER_EP), &server_ep);	
            
          coap_init_message(request, COAP_TYPE_CON, COAP_GET, 0);
          coap_set_header_uri_path(request, service_url);
            
          coap_set_payload(request, (uint8_t *)SENSOR_TYPE, sizeof(SENSOR_TYPE) - 1);
          //TO DO: it will be useful to make a non blocking request and / or decrease the CoAP connection timeout
          COAP_BLOCKING_REQUEST(&server_ep, request, client_status_checker);
      }

      etimer_reset(&status_check);
      PROCESS_WAIT_UNTIL(etimer_expired(&status_check));
      
  }
  PROCESS_END();
}
