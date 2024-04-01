#include <stdbool.h>
#include "echo_proto.h"

bool validate_next_client_state(ep_mtype_t current_state, ep_mtype_t proposed_next_state){
    ep_mtype_t allowed_next_state = advance_state_client(current_state);

    if ((allowed_next_state & proposed_next_state) != 0)
        return true;
    return false;
}
ep_mtype_t  advance_state_client(ep_mtype_t current_state){
    switch(current_state){
        case EP_IDLE:
            return EP_CONNECTED;        
        case EP_CONNECTED:
            return EP_ECHO;
        case EP_ECHO:
            return EP_ECHO_PENDING;
        case EP_ECHO_PENDING:
            return EP_ECHO_ACK_PENDING;
        case EP_ECHO_ACK_PENDING:
            return EP_ECHO_ACK;
        case EP_ECHO_ACK:
            return EP_ECHO | EP_CLOSED;     
        case EP_CLOSED:
            return EP_CLOSED;   
        case EP_ERROR:    
            return EP_ERROR;
        default:
            return EP_ERROR;     
    }
}

bool validate_next_server_state(ep_mtype_t current_state, ep_mtype_t proposed_next_state){
    ep_mtype_t allowed_next_state = advance_state_server(current_state);

    if ((allowed_next_state & proposed_next_state) != 0)
        return true;
    return false;
}
ep_mtype_t  advance_state_server(ep_mtype_t current_state){
    switch(current_state){
        case EP_IDLE:    
        case EP_CONNECTED:
            return EP_ECHO;
        case EP_ECHO:
            return EP_ECHO_PENDING;
        case EP_ECHO_PENDING:
            return EP_ECHO | EP_CLOSED;  
        case EP_CLOSED:
            return EP_CLOSED;   
        case EP_ERROR:    
            return EP_ERROR;
        default:
            return EP_ERROR;     
    }
}
