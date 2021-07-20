#include "contiki.h"
#include "net/routing/routing.h"
#include "mqtt.h"
#include "mqtt-client.h"
#include "net/ipv6/uip.h"
#include "net/ipv6/uip-icmp6.h"
#include "net/ipv6/sicslowpan.h"

#include "sys/etimer.h"
//#include "lib/sensors.h"
#include "os/sys/log.h"
#include <sys/node-id.h>

#include <string.h>

#define LOG_MODULE "mqtt-client"
#define LOG_LEVEL LOG_LEVEL_DBG


#include "mqtt_config.h"
#include "utilities.c"


//PROCESS_NAME(mqtt_client_process);
PROCESS(mqtt_client_process, "MQTT Client");
AUTOSTART_PROCESSES(&mqtt_client_process);


 
#define HIGH_TEMP_TRESHOLD 8.0
#define LOW_TEMP_TRESHOLD -4.0
#define MAX_DIFF 20    //10 times maximum diff

float current_temperature = 2.5;

enum DOOR_STATE {OPEN, CLOSED};

enum DOOR_STATE door_state = CLOSED;

#define DEFAULT_PROBABILITY 50

bool roll_dice(int probability){

    if(random() % 100 <= probability){
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
    }

    if(roll_dice(open_probability)){
        door_state = OPEN;
    }else{
        door_state = CLOSED;
    }

    if(door_state == OPEN)
        return true;
    else
        return false;
}

void sense_temperature(){

    if(door_is_open()){

        current_temperature += 1.0;

    }else{
        float diff = ((float)(random() % MAX_DIFF)) / 10.0;

        if(roll_dice(DEFAULT_PROBABILITY)){
            diff *= -1.0;
        }

        current_temperature += diff;
    }
}


// Periodic timer to check the state of the MQTT client
#define STATE_MACHINE_PERIODIC     (CLOCK_SECOND >> 1)
static struct etimer periodic_timer;
static int period = 0;

/*---------------------------------------------------------------------------*/
static struct mqtt_message *msg_ptr = 0;
static struct mqtt_connection conn;


#include "mqtt_event_handler.c"


int ip_str_len = 0;

void test_function(const char * host){
    //char broker_address[CONFIG_IP_ADDR_STR_LEN];
    //char * broker_address = MQTT_CLIENT_BROKER_IP_ADDR;

    uip_ip6addr_t ip6addr;

    printf("[test_function] begin\n");
    printf("[test_function]: trying on : '%s'\n", host);

    
    /* convert the string IPv6 address to a numeric IPv6 address */
    if(uiplib_ip6addrconv(host, &ip6addr) == 0) {
        printf("[test_function] ERROR: uiplib_ip6addrconv returned 0\n");
        return;
    }
    printf("[test_function] ok | IP6ADDR \n"); //, (int) uip_ip6addr_t);
    ip_str_len = strlen(host);
    printf("[test_function]: trew on : '%s' | len = %d\n", host, ip_str_len);
}

void check_broker_ip_string(char * broker_address){
    int len = strlen(broker_address);
    if(len != ip_str_len){
        printf("[check_broker_ip_string] broker_address strlen = %d\n REPASTING :@\n", len);
        
        snprintf((char *) broker_address, CONFIG_IP_ADDR_STR_LEN, "%s", broker_ip);

    }
    else{
        printf("[check_broker_ip_string]: ok | strlen = %d\n", len);
    }

    printf("[check_broker_ip_string] END | broker_address is now: '%s'\n");
}


PROCESS_THREAD(mqtt_client_process, ev, data)
{
  PROCESS_BEGIN();

  mqtt_status_t status;
  char broker_address[CONFIG_IP_ADDR_STR_LEN];

  printf("MQTT Client Process\n");

  // Initialize the ClientID as MAC address
  initialize_client_id(client_id);

  snprintf((char *) broker_address, CONFIG_IP_ADDR_STR_LEN, "%s", broker_ip);

  //int counter_checks = 0;
  test_function(broker_address);

/*
  char t[11];
  sprintf(t, "fridge/%d/desidered_temp", node_id);
  strcpy(sub_topic,t);
*/ 

  // Broker registration
  mqtt_register(&conn, &mqtt_client_process, client_id, mqtt_event, MAX_TCP_SEGMENT_SIZE);


  state=STATE_INIT;

  // Initialize periodic timer to check the status
  etimer_set(&periodic_timer, STATE_MACHINE_PERIODIC);
  
  
  while(1) {

    PROCESS_YIELD();
    
    if((ev == PROCESS_EVENT_TIMER && data == &periodic_timer) || (ev == PROCESS_EVENT_POLL)){

        if(state==STATE_INIT){
            if(have_connectivity()==true)
                state = STATE_NET_OK;
        }

        if(state == STATE_NET_OK){
            // Connect to MQTT broker

            /*if(counter_checks < 10){
                check_broker_ip_string(broker_address);
                counter_checks++;
            }*/  

            printf("Connecting to MQTT broker IP:'%s'...\n", MQTT_CLIENT_BROKER_IP_ADDR);   //broker_address

            status = mqtt_connect(&conn, MQTT_CLIENT_BROKER_IP_ADDR, DEFAULT_BROKER_PORT, (DEFAULT_PUBLISH_INTERVAL * 3 )/ CLOCK_SECOND, MQTT_CLEAN_SESSION_ON);
            
            if(status == MQTT_STATUS_OK){
                printf("[mqtt_connect]: connected successfully!\n");
                state = STATE_CONNECTING;

            }else{
                printf("[mqtt_connect]: an error occurred :(\n");
                if(status == MQTT_STATUS_ERROR){
                    printf("[mqtt_connect]: status == MQTT_STATUS_ERROR\n");
                }else{
                    printf("[mqtt_connect] ERROR NUMBER: %d \n", (int) status);
                }
                
            }

        }

        //mqtt_event() function will update 'state' to STATE_CONNECTED whenever it will receives a MQTT_EVENT_CONNECTED event

        if(state==STATE_CONNECTED){

        // Subscribe to the topic as it is not subscribed yet

        printf("Subscribing...\n");

        status = mqtt_subscribe(&conn, NULL, sub_topic, MQTT_QOS_LEVEL_0);

        if(status == MQTT_STATUS_OUT_QUEUE_FULL) {
        LOG_ERR("Tried to subscribe but command queue was full!\n");
        PROCESS_EXIT();
        }

        state = STATE_SUBSCRIBED;

        printf("Subscribed successfully to topic '%s'! \n", sub_topic);

        }else if (state == STATE_SUBSCRIBED && (period%60==0)){
                        
                        sense_temperature();
                        
                        // Publish something
                        sprintf(pub_topic, "fridge/%s/temperature", client_id); //a different topic for each temperature sensor node

                        sprintf(app_buffer, "{\"temperature\": %.2f, \"timestamp\": %lu, \"unit\": \"celsius\"}", current_temperature, clock_seconds());
                        mqtt_publish(&conn, NULL, pub_topic, (uint8_t *)app_buffer,
                                strlen(app_buffer), MQTT_QOS_LEVEL_0, MQTT_RETAIN_OFF);
                }
        else if ( state == STATE_DISCONNECTED ){
        LOG_ERR("Disconnected form MQTT broker\n");
        state = STATE_INIT;
        // Recover from error
        }

        etimer_set(&periodic_timer, STATE_MACHINE_PERIODIC);
        period++;

    }
  }

  PROCESS_END();
}