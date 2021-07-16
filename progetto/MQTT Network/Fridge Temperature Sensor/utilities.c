#ifndef BUFFER_SIZE
    #define BUFFER_SIZE 64
#endif
//it works only if is included inside node.c because of some dependencies

void initialize_client_id(char * client_id){
  snprintf(client_id, BUFFER_SIZE, "%02x%02x%02x%02x%02x%02x",
                     linkaddr_node_addr.u8[0], linkaddr_node_addr.u8[1],
                     linkaddr_node_addr.u8[2], linkaddr_node_addr.u8[5],
                     linkaddr_node_addr.u8[6], linkaddr_node_addr.u8[7]);
}