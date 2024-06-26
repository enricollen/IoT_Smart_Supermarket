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

#include "random.h"

#include <string.h>
#include <strings.h>
/*---------------------------------------------------------------------------*/
#define LOG_MODULE "mqtt-client"
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
#define NODE_KIND "fridge_temp_sensor"

static const char *broker_ip = MQTT_CLIENT_BROKER_IP_ADDR;

char broker_address[CONFIG_IP_ADDR_STR_LEN];

// Defaukt config values
#define DEFAULT_BROKER_PORT         1883
#define DEFAULT_PUBLISH_INTERVAL    (30 * CLOCK_SECOND)


// We assume that the broker does not require authentication

/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/
#define ENABLE_SENSE_TEMPERATURE true
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

enum PUBLISH_TOPIC {DISCOVERY, TEMPERATURE};

const char* string_last_publish_topic[] = {"DISCOVERY", "TEMPERATURE"};

static enum PUBLISH_TOPIC last_publish_topic = TEMPERATURE;

/*---------------------------------------------------------------------------*/
PROCESS(mqtt_client_process, "MQTT Client");


#if ENABLE_SENSE_TEMPERATURE

#define HIGH_TEMP_TRESHOLD 8.0
#define LOW_TEMP_TRESHOLD -4.0
#define MAX_DIFF 20    //10 times maximum diff
#define THERMOSTAT_DELTA 1
#define INERTIAL_DELTA THERMOSTAT_DELTA + 0.5

enum binary_state {OFF, ON};

const char* string_compressor_state[] = {"OFF", "ON"};

enum binary_state compressor_state = OFF;

float desired_temperature = 0.0;

float current_temperature = 0.0;

enum DOOR_STATE {OPEN, CLOSED};

const char* string_door_state[] = {"OPEN", "CLOSED"};

enum DOOR_STATE door_state = CLOSED;

static int consecutive_open_state_counter = 0;

#define DEFAULT_PROBABILITY 50

bool roll_dice(int probability){

    if(random_rand() % 100 <= probability){
        return true;
    }
    else
        return false;
}

bool door_is_open(){

    int open_probability = 10;

    if(door_state == OPEN){
        //still open probability is higher than normal open probability
        open_probability = 80;
        
      if(consecutive_open_state_counter > 5){
          open_probability = 50;
      }else if (consecutive_open_state_counter > 10){
          open_probability = 30;
      }else if (consecutive_open_state_counter > 20){
          open_probability = 10;
      }
    }

    if(roll_dice(open_probability)){
        door_state = OPEN;
        consecutive_open_state_counter++;
        LOG_DBG("[door_is_open]: the door is OPEN since %d cycles \n", consecutive_open_state_counter);
    }else{
        door_state = CLOSED;
        consecutive_open_state_counter = 0;
    }

    if(door_state == OPEN)
        return true;
    else
        return false;
}

#define COMPRESSOR_TEMPERATURE_CHANGE_PER_CYCLE 0.3
#define DISPERSION_TEMPERATURE_CHANGE_PER_CYCLE 0.2
#define OPEN_DOOR_TEMPERATURE_CHANGE_PER_CYCLE 0.5

#define ROOM_TEMPERATURE 22.0

bool is_temperature_raising = true;

void sense_temperature(){

    if(door_is_open()){

        current_temperature += OPEN_DOOR_TEMPERATURE_CHANGE_PER_CYCLE;

    }else{
       if(current_temperature > desired_temperature){
         compressor_state = ON;
         if(current_temperature > desired_temperature + INERTIAL_DELTA || ! is_temperature_raising){
           current_temperature -= COMPRESSOR_TEMPERATURE_CHANGE_PER_CYCLE;
           is_temperature_raising = false;
         }
         else{
           current_temperature += DISPERSION_TEMPERATURE_CHANGE_PER_CYCLE;
           is_temperature_raising = true;
         }
       }
       else{
         if(current_temperature + THERMOSTAT_DELTA < desired_temperature){
           compressor_state = OFF;
         }
         if(compressor_state==ON){
           current_temperature -= COMPRESSOR_TEMPERATURE_CHANGE_PER_CYCLE;
           is_temperature_raising = false;
         }
         else{
           current_temperature += DISPERSION_TEMPERATURE_CHANGE_PER_CYCLE;
           is_temperature_raising = true;
         }
       }
    }
    if(current_temperature > ROOM_TEMPERATURE){
      current_temperature = ROOM_TEMPERATURE;
    }
}

void update_desired_temp(float new_desired_temperature){
  desired_temperature = new_desired_temperature;
}

#endif

#include "../../nodes-utilities.h"

#ifndef PRINT_NODE_IP_DEFINED

#define PRINT_NODE_IP_DEFINED

void print_node_ip(){
  char buffer[40];
  size_t size = 40;

  uip_ds6_addr_t *addr_struct = uip_ds6_get_global(ADDR_PREFERRED);

  if(addr_struct != NULL){
    uip_ipaddr_t * 	addr = & addr_struct->ipaddr;

    uiplib_ipaddr_snprint	(	buffer, size, addr);

    LOG_INFO("[print_node_ip] current_ip: %s \n", buffer);
  }
}

#endif

#ifndef PRINT_CLIENT_ID_DEFINED

#define PRINT_CLIENT_ID_DEFINED

//extern char * client_id;

void print_client_id(){
  LOG_INFO("[MQTT client_id]: %s\n", client_id);
}
#endif
  
/*---------------------------------------------------------------------------*/
static void
pub_handler(const char *topic, uint16_t topic_len, const uint8_t *chunk,
            uint16_t chunk_len)
{
  printf("Pub Handler: topic='%s' (len=%u), chunk_len=%u\n", topic,
          topic_len, chunk_len);

  if(strcmp(topic, sub_topic) == 0) {
    printf("Received Desired Temperature: %s\n", chunk);
	  float received_temp = atof((const char *) chunk);
    if(received_temp==0.0){
      if(chunk[0]=='0')
        update_desired_temp(received_temp);
      else
        LOG_DBG("[pub_handler]: Received temperature is not acceptable.\n");
    }
    else{
      update_desired_temp(received_temp);
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

    print_node_ip();
    print_client_id();

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
        last_publish_topic = TEMPERATURE;
    }else{
      //here we assume that the last message was published on fridge/id/temperature
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
        sprintf(sub_topic, "fridge/%s/desired_temp", client_id);

        #else
        strcpy(sub_topic,"actuator");
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
      if (period%60==0){  //publishes every 60 ticks
			
        #if ENABLE_SENSE_TEMPERATURE
        sense_temperature();
        
        LOG_DBG("[sense_temperature]: door_state = %s | compressor_state = %s | current_temperature = %s | desired_temperature = %s \n", string_door_state[door_state], string_compressor_state[compressor_state], (char*)  float_to_string(current_temperature, 2), (char*) float_to_string(desired_temperature, 2) );
        
        #endif
      }
      if(period%30 == 0){
        #if ENABLE_PUBLISH_CURRENT_STATE
        // Publish something
        if(last_publish_topic != TEMPERATURE){
            sprintf(pub_topic, "fridge/%s/temperature", client_id); //a different topic for each temperature sensor node
            LOG_DBG("[Publish Topic]: %s\n", pub_topic);
            sprintf(app_buffer, "{\"temperature\": %s, \"timestamp\": %lu, \"unit\": \"celsius\", \"desired_temp\":%s}", (char*) float_to_string(current_temperature, 2) , clock_seconds(), (char*) float_to_string(desired_temperature, 2) );
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
    period++;
		
		etimer_set(&periodic_timer, STATE_MACHINE_PERIODIC); 
    }
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
