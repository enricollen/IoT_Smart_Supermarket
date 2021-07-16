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


#define MAX_WEIGHT 2000
#define MIN_WEIGHT 0
#define TRESHOLD_WEIGHT 200

/* Declare and auto-start this file's process */
PROCESS(contiki_ng_br_coap_server, "Contiki-NG Border Router and CoAP Server");
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

}

void measure_weight(){
  
  current_weight = ( rand() % (MAX_WEIGHT - MIN_WEIGHT + 1) ) + MIN_WEIGHT;

  if(current_weight < TRESHOLD_WEIGHT){
    //internal automation that refills the shelf whenever it is nearly empty
    refill_shelf();

  }
}

PROCESS_THREAD(contiki_ng_br_coap_server, ev, data){

  PROCESS_BEGIN();
  etimer_set(&timer, 5*CLOCK_SECOND);

	coap_activate_resource(&res_weight, "weight");
  coap_activate_resource(&res_refill, "refill");

  refill_shelf();   //when the sensor is restarted, we reset the current weight to MAX_WEIGHT
	
  while(1){
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    measure_weight();
    res_weight.trigger(); //calls obs_handler
    etimer_reset(&timer);
  }
	
  PROCESS_END();
}
