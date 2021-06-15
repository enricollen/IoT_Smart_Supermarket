#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "contiki.h"
#include "coap-engine.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "App"
#define LOG_LEVEL LOG_LEVEL_APP

/* Declare and auto-start this file's process */
PROCESS(contiki_ng_br_coap_server, "Contiki-NG Border Router and CoAP Server");
AUTOSTART_PROCESSES(&contiki_ng_br_coap_server);

extern coap_resource_t res_obs;
static struct etimer etimer;
etimer_set(&etimer, 5*CLOCK_SECOND);

PROCESS_THREAD(contiki_ng_br_coap_server, ev, data){

  PROCESS_BEGIN();

#if BORDER_ROUTER_CONF_WEBSERVER
  PROCESS_NAME(webserver_nogui_process);
  process_start(&webserver_nogui_process, NULL);
#endif /* BORDER_ROUTER_CONF_WEBSERVER */

	LOG_INFO("Contiki-NG Border Router started\n");
	LOG_INFO("Starting Erbium Example Server\n");
	coap_activate_resource(&res_obs, "observable_res");
	
  while(1){
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&etimer));
    res_obs.trigger();
    etimer_reset(&etimer);
  }
	
  PROCESS_END();
}
