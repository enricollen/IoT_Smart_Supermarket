#define MQTT_CLIENT_BROKER_IP_ADDR "fd00:::::::1"
//"fd00::1"
#define DEFAULT_BROKER_PORT         1883
#define DEFAULT_PUBLISH_INTERVAL    (30 * CLOCK_SECOND)
//our broker does not require authentication


#define MAX_TCP_SEGMENT_SIZE    32
#define CONFIG_IP_ADDR_STR_LEN   64


static const char *broker_ip = MQTT_CLIENT_BROKER_IP_ADDR;  //"fd00:::::::1";

//-----------------------------------
static short state;

#define STATE_INIT              0
#define STATE_NET_OK            1
#define STATE_CONNECTING        2
#define STATE_CONNECTED         3
#define STATE_SUBSCRIBED        4
#define STATE_DISCONNECTED      5
//------------------------------------
#define BUFFER_SIZE 64

static char client_id[BUFFER_SIZE];
static char pub_topic[BUFFER_SIZE];
static char sub_topic[BUFFER_SIZE];
//------------------------------------

/*
 * The main MQTT buffers.
 * We will need to increase if we start publishing more data.
 */
#define APP_BUFFER_SIZE 512
static char app_buffer[APP_BUFFER_SIZE];