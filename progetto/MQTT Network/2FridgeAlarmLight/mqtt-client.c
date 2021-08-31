#include "contiki.h"
#include "net/routing/routing.h"
#include "mqtt.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/uip-icmp6.h"
#include "net/ipv6/sicslowpan.h"
#include "sys/etimer.h"
#include "sys/ctimer.h"
#include "lib/sensors.h"
#include "dev/button-hal.h"
#include "dev/leds.h"
#include "os/sys/log.h"
#include "mqtt-client.h"

#include <string.h>
#include <strings.h>
/*---------------------------------------------------------------------------*/
#define LOG_MODULE "fridge_alarm_light"
#ifdef MQTT_CLIENT_CONF_LOG_LEVEL
#define LOG_LEVEL MQTT_CLIENT_CONF_LOG_LEVEL
#else
#define LOG_LEVEL LOG_LEVEL_DBG
#endif
#undef LOG_LEVEL
#define LOG_LEVEL LOG_LEVEL_DBG

/*---------------------------------------------------------------------------*/
/* MQTT broker address. */
#define MQTT_CLIENT_BROKER_IP_ADDR "fd00::1"
#define CONFIG_IP_ADDR_STR_LEN   16 //64

#define DISCOVERY_TOPIC "discovery"
#define NODE_KIND "fridge_alarm_light"

static const char *broker_ip = MQTT_CLIENT_BROKER_IP_ADDR;

char broker_address[CONFIG_IP_ADDR_STR_LEN];

// Defaukt config values
#define DEFAULT_BROKER_PORT         1883
#define DEFAULT_PUBLISH_INTERVAL    (30 * CLOCK_SECOND)


// We assume that the broker does not require authentication

/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/
#define ENABLE_MQTT_PUBLISH true
#define ENABLE_PERIODIC_PUBLISH true
#define ENABLE_HANDLE_MQTT_CONNECT_RETURN_STATUS true
#define ENABLE_PUBLISH_CURRENT_STATE true
#define ENABLE_PREPARE_MQTT_TOPIC_STRING true
#define ENABLE_PUBLISH_DISCOVERY_MESSAGE true
/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/

/*---------------------------------------------------------------------------*/
/* Various states */
static uint8_t state;

#define STATE_INIT    		  0
#define STATE_NET_OK    	  1
#define STATE_CONNECTING      2
#define STATE_CONNECTED       3
#define STATE_SUBSCRIBED      4
#define STATE_DISCONNECTED    5

/*---------------------------------------------------------------------------*/
PROCESS_NAME(mqtt_client_process);
AUTOSTART_PROCESSES(&mqtt_client_process);

/*---------------------------------------------------------------------------*/
/* Maximum TCP segment size for outgoing segments of our socket */
#define MAX_TCP_SEGMENT_SIZE    32
/*---------------------------------------------------------------------------*/
/*
 * Buffers for Client ID and Topics.
 * Make sure they are large enough to hold the entire respective string
 */
#define BUFFER_SIZE 64

static char client_id[BUFFER_SIZE];
#if ENABLE_PUBLISH_CURRENT_STATE
static char pub_topic[BUFFER_SIZE];
#endif
static char sub_topic[BUFFER_SIZE];


// Periodic timer to check the state of the MQTT client
#define STATE_MACHINE_PERIODIC     (CLOCK_SECOND >> 1)
static struct etimer periodic_timer;

/*---------------------------------------------------------------------------*/
/*
 * The main MQTT buffers.
 * We will need to increase if we start publishing more data.
 */
#define APP_BUFFER_SIZE 512
#if ENABLE_PUBLISH_CURRENT_STATE
static char app_buffer[APP_BUFFER_SIZE];
#endif
/*---------------------------------------------------------------------------*/
static struct mqtt_message *msg_ptr = 0;

static struct mqtt_connection conn;

static int period = 0;

enum PUBLISH_TOPIC {DISCOVERY, STATE};

const char* string_last_publish_topic[] = {"DISCOVERY", "STATE"};

static enum PUBLISH_TOPIC last_publish_topic = STATE;

/*---------------------------------------------------------------------------*/
PROCESS(mqtt_client_process, "MQTT Client");
/*
pub_topic : alarm/id/state
sub_topic : alarm/id/actuator-cmd
*/

#define ON_STRING "ON"
#define ON_STATE 1
#define OFF_STRING "OFF"
#define OFF_STATE 0

enum BINARY_STATE {OFF, ON};

static enum BINARY_STATE alarm_state = OFF;

static void turn_alarm(const enum BINARY_STATE new_state){
  if(new_state == ON){
    alarm_state = ON;
    //call a method to turn ON the lights of the node (or make them blink)
  }
  else if(new_state == OFF){
    alarm_state = OFF;
    //call a method to turn OFF the lights of the node (or stop them to blink)
  }
}

static const char* get_current_state_as_string(){
  switch (alarm_state)
  {
  case ON:
    return "ON";

  case OFF:
    return "OFF";
  
  default:
    return "ERR";
  }
}

void led_state_handler(){
  if(alarm_state == ON){
    leds_toggle(LEDS_ALL);
  }
  else if(alarm_state == OFF){
    leds_off(LEDS_ALL);
  }
}

/*---------------------------------------------------------------------------*/
static void
pub_handler(const char *topic, uint16_t topic_len, const uint8_t *chunk,
            uint16_t chunk_len)
{
  printf("Pub Handler: topic='%s' (len=%u), chunk_len=%u\n", topic,
          topic_len, chunk_len);

  if(strcmp(topic, sub_topic) == 0) {
    printf("Received New Command: %s\n", chunk);
	  
    if(strcmp((char *) chunk, ON_STRING) == 0){
      turn_alarm(ON);
    }
    else if(strcmp((char *) chunk, OFF_STRING) == 0){
      turn_alarm(OFF);
    }
    return;
  }
}
/*---------------------------------------------------------------------------*/
static void
mqtt_event(struct mqtt_connection *m, mqtt_event_t event, void *data)
{
  switch(event) {
  case MQTT_EVENT_CONNECTED: {
    
    printf("[+] Connected to MQTT broker!\n");

    state = STATE_CONNECTED;
    break;
  }
  case MQTT_EVENT_DISCONNECTED: {
    printf("MQTT Disconnect. Reason %u\n", *((mqtt_event_t *)data));

    state = STATE_DISCONNECTED;
    process_poll(&mqtt_client_process);
    break;
  }
  case MQTT_EVENT_PUBLISH: {
    msg_ptr = data;

    pub_handler(msg_ptr->topic, strlen(msg_ptr->topic),
                msg_ptr->payload_chunk, msg_ptr->payload_length);
    break;
  }
  case MQTT_EVENT_SUBACK: {
#if MQTT_311
    mqtt_suback_event_t *suback_event = (mqtt_suback_event_t *)data;

    if(suback_event->success) {
      printf("Application is subscribed to topic successfully\n");
    } else {
      printf("Application failed to subscribe to topic (ret code %x)\n", suback_event->return_code);
    }
#else
    printf("Application is subscribed to topic successfully\n");
#endif
    break;
  }
  case MQTT_EVENT_UNSUBACK: {
    printf("Application is unsubscribed to topic successfully\n");
    break;
  }
  case MQTT_EVENT_PUBACK: {
    //printf("Publishing complete.\n");
    if(last_publish_topic == DISCOVERY){
        last_publish_topic = STATE;
    }else{
      //here we assume that the last message was published on alarm/id/state
      last_publish_topic = DISCOVERY;
    }
    //LOG_DBG("[MQTT_EVENT_PUBACK]: last_publish_topic = %s\n", string_last_publish_topic[last_publish_topic]);
    break;
  }
  default:
    printf("Application got a unhandled MQTT event: %i\n", event);
    break;
  }
}

static bool
have_connectivity(void)
{
  if(uip_ds6_get_global(ADDR_PREFERRED) == NULL ||
     uip_ds6_defrt_choose() == NULL) {
    return false;
  }
  return true;
}

/*---------------------------------------------------------------------------*/
PROCESS_THREAD(mqtt_client_process, ev, data)
{

  PROCESS_BEGIN();
  
  mqtt_status_t status;
  //char broker_address[CONFIG_IP_ADDR_STR_LEN];

  printf("MQTT Client Process\n");

  // Initialize the ClientID as MAC address
  snprintf(client_id, BUFFER_SIZE, "%02x%02x%02x",
                     linkaddr_node_addr.u8[5],
                     linkaddr_node_addr.u8[6], linkaddr_node_addr.u8[7]);

  // Broker registration					 
  mqtt_register(&conn, &mqtt_client_process, client_id, mqtt_event,
                  MAX_TCP_SEGMENT_SIZE);
				  
  state=STATE_INIT;
				    
  // Initialize periodic timer to check the status 
  etimer_set(&periodic_timer, STATE_MACHINE_PERIODIC);

  /* Main loop */
  while(1) {

    PROCESS_YIELD();

    if((ev == PROCESS_EVENT_TIMER && data == &periodic_timer) || 
	      ev == PROCESS_EVENT_POLL){
			  			  
		  if(state==STATE_INIT){
			 if(have_connectivity()==true){  
          state = STATE_NET_OK;
          LOG_DBG("have_connectivity() returned true\n");
        }
		  } 
		  
		  if(state == STATE_NET_OK){
			  // Connect to MQTT server
			  printf("Connecting to MQTT broker...\n");
			  
			  memcpy(broker_address, broker_ip, strlen(broker_ip)); 
			  
			  #if ENABLE_HANDLE_MQTT_CONNECT_RETURN_STATUS
        status = mqtt_connect(&conn, broker_address, DEFAULT_BROKER_PORT,
						   (DEFAULT_PUBLISH_INTERVAL * 3) / CLOCK_SECOND,
						   MQTT_CLEAN_SESSION_ON);
        if(status == MQTT_STATUS_OK){
            LOG_INFO("[mqtt_connect]: connected successfully!\n");
            state = STATE_CONNECTING;

        }else{
            LOG_DBG("[mqtt_connect]: an error occurred :(\n");
            if(status == MQTT_STATUS_ERROR){
                LOG_DBG("[mqtt_connect]: status == MQTT_STATUS_ERROR\n");
                LOG_DBG("[mqtt_connect] using IP broker_address = '%s' | broker_ip = '%s'\n", broker_address, broker_ip);
            }else{
                LOG_DBG("[mqtt_connect] ERROR NUMBER: %d \n", (int) status);
            }
            
        }
        #else
        mqtt_connect(&conn, broker_address, DEFAULT_BROKER_PORT,
						   (DEFAULT_PUBLISH_INTERVAL * 3) / CLOCK_SECOND,
						   MQTT_CLEAN_SESSION_ON);

        state = STATE_CONNECTING;

        #endif
        
		  }
		  
		  if(state==STATE_CONNECTED){
		  
        printf("Subscribing...\n");

			  // Subscribe to a topic
			  #if ENABLE_PREPARE_MQTT_TOPIC_STRING
        sprintf(sub_topic, "alarm/%s/actuator-cmd", client_id);
        #endif

			  status = mqtt_subscribe(&conn, NULL, sub_topic, MQTT_QOS_LEVEL_0);

			  printf("Subscribed!\n");
			  if(status == MQTT_STATUS_OUT_QUEUE_FULL) {
				LOG_ERR("Tried to subscribe but command queue was full!\n");
				PROCESS_EXIT();
			  }
			  
			  state = STATE_SUBSCRIBED;

        printf("Subscribed successfully to topic '%s'! \n", sub_topic);
		  }

			  
		if(state == STATE_SUBSCRIBED){
      #if ENABLE_PERIODIC_PUBLISH
      
      if(period%30 == 0){
        #if ENABLE_PUBLISH_CURRENT_STATE
        // Publish something
        if(last_publish_topic != STATE){
            sprintf(pub_topic, "alarm/%s/state", client_id); //a different topic for each alarm actuator node
            LOG_DBG("[Publish Topic]: %s\n", pub_topic);
            sprintf(app_buffer, "{\"alarm_state\": \"%s\", \"timestamp\": %lu}", get_current_state_as_string(), clock_seconds());
            mqtt_publish(&conn, NULL, pub_topic, (uint8_t *)app_buffer,
                    strlen(app_buffer), MQTT_QOS_LEVEL_1, MQTT_RETAIN_OFF);
        }
        #if ENABLE_PUBLISH_DISCOVERY_MESSAGE
        else if(last_publish_topic != DISCOVERY){
            sprintf(pub_topic, "%s", DISCOVERY_TOPIC); //a different topic for each temperature sensor node
            LOG_DBG("[Publish Topic]: %s\n", pub_topic);
            memset(app_buffer, 0, sizeof(app_buffer));
            sprintf(app_buffer, "{\"id\": \"%s\", \"kind\": \"%s\"}", client_id, NODE_KIND);
            mqtt_publish(&conn, NULL, pub_topic, (uint8_t *)app_buffer,
                    strlen(app_buffer), MQTT_QOS_LEVEL_1, MQTT_RETAIN_OFF);
        }
        #endif
        #endif
      }      

      #endif
		} else if ( state == STATE_DISCONNECTED ){
		   LOG_ERR("Disconnected from MQTT broker\n");	
		   // Recover from error
       mqtt_disconnect(&conn);
       state = STATE_INIT;
		}

    led_state_handler();

    period++;
		
		etimer_set(&periodic_timer, STATE_MACHINE_PERIODIC); 
    }
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
