#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"

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

extern coap_resource_t res_weight;

//------------------------------
//SENSOR INFOS:
//those are initialized inside PROCESS_THREAD
int current_weight = 0;
int last_refill_ts = -1; 
//------------------------------


void measure_weight(){
  
  current_weight = ( rand() % (MAX_WEIGHT - MIN_WEIGHT + 1) ) + MIN_WEIGHT;

  if(current_weight < TRESHOLD_WEIGHT){
    //internal automation that refills the shelf whenever it is nearly empty
    refill_shelf();

  }
}

void refill_shelf(){

  //refill the shelf
  current_weight = MAX_WEIGHT;

  
  //saves the last refill timestamp
  last_refill_ts = clock_seconds();

}

static struct etimer etimer;


etimer_set(&etimer, 5*CLOCK_SECOND);

PROCESS_THREAD(contiki_ng_br_coap_server, ev, data){

  PROCESS_BEGIN();

	coap_activate_resource(&res_weight, "weight");

  refill_shelf();   //when the sensor is restarted, we reset the current weight to MAX_WEIGHT
	
  while(1){
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&etimer));
    res_weight.trigger(); //calls obs_handler
    etimer_reset(&etimer);
  }
	
  PROCESS_END();
}
