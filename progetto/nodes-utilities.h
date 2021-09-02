#ifndef NODES_UTILITIES_INCLUDED

#define NODES_UTILITIES_INCLUDED true


#include "net/ipv6/uip.h"
#include "net/ipv6/uiplib.h"
#include "net/ipv6/uip-icmp6.h"
#include "net/ipv6/uip-ds6.h"


// returns a char* to a buffer containing the base10 representation of a float as string
#define FLOAT_TO_STRING_BUFFERS_NUMBER 2

static unsigned short rotate = 0;

static char str_float[FLOAT_TO_STRING_BUFFERS_NUMBER][20];

// Converts a floating-point/double number to a string.
static char* float_to_string(float n, int afterpoint)
{

    char temp[10];
    
    char * res = (char*) str_float[rotate];
    
    // Extract integer part
    int ipart = (int)n;
  
    // Extract floating part
    float fpart = n - (float)ipart;
  
    // convert integer part to string
    //int i = intToStr(ipart, res, 0);
  
    sprintf(res, "%d", ipart);
    sprintf(temp, "%d", ipart);

    //int i = strlen(res);

    // check for display option after point
    if (afterpoint != 0) {
        //res[i] = '.'; // add dot

        // Get the value of fraction part upto given no.
        // of points after dot. The third parameter 
        // is needed to handle cases like 233.007
        
        for(int a = 0; a < afterpoint; a++){
          fpart *= (float) 10.0F;
        }
        //fpart = fpart * pow(10, afterpoint);

        sprintf(res, "%s.%d", temp, (int) fpart);
    }

    rotate = (rotate + 1) % FLOAT_TO_STRING_BUFFERS_NUMBER;

    return res;
}
/*
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

extern char * client_id;

void print_client_id(){
  LOG_INFO("[MQTT client_id]: %s\n", client_id);
}
#endif
*/

#endif