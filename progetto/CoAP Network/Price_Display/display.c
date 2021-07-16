#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"
#include "sys/etimer.h"
#include <time.h>

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

#define DEFAULT_PRICE 20.5
#define MINIMUM_PRICE 0.90

/* Declare and auto-start this file's process */
PROCESS(contiki_ng_br_coap_server, "Contiki-NG Border Router and CoAP Server");
AUTOSTART_PROCESSES(&contiki_ng_br_coap_server);
static struct etimer timer;

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

	coap_activate_resource(&res_price, "price");

  change_price(DEFAULT_PRICE);   //when the sensor is restarted, we reset the current weight to MAX_WEIGHT
		
  PROCESS_END();
}
