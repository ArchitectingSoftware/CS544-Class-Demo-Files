#pragma once

#include <stdint.h>
#include <stdbool.h>

//We commonly use bit fields to represent protocol states
//                 64 32 16  8  4  2  1
// EP_NO_STATE      0  0  0  0  0  0  0
// EP_IDLE          0  0  0  0  0  0  1
// EP_CONNECTED     0  0  0  0  0  1  0
// EP_ECHO          0  0  0  0  1  0  0
// EP_CLOSED        0  0  0  1  0  0  0
// EP_ERROR         0  0  1  0  0  0  0
// EP_PENDING       0  1  0  0  0  0  0
// EP_ACK           1  0  0  0  0  0  0

//ECHO PROTOCOL INFORMATION
//Protocol States
typedef uint8_t         ep_mtype_t;
#define EP_INITIAL_STATE EP_IDLE
#define EP_NO_STATE     0x00
#define EP_IDLE         0x01
#define EP_CONNECTED    0x02
#define EP_ECHO         0x04
#define EP_CLOSED       0x08
#define EP_ERROR        0x10
#define EP_PENDING      0x20
#define EP_ACK          0x40

#define EP_STATE_SZ     sizeof(uint8_t)

//ACK IS TO ACKNOLEDGE SO WE CAN COMBINE AND CHECK FOR ITS
//PRESENCE
#define EP_CONN_ACK      EP_CONNECTED  | EP_ACK
#define EP_ECHO_ACK      EP_ECHO       | EP_ACK
#define EP_CLOSED_ACK    EP_CLOSED     | EP_ACK
#define EP_ECHO_PENDING  EP_ECHO       | EP_PENDING
#define EP_ECHO_ACK_PENDING EP_ECHO_PENDING| EP_ACK
#define IS_ACK(x)        ((x & EP_ACK) == EP_ACK)
#define SET_ACK(x)       (x | EP_ACK)
#define CLEAR_ACK(x)     (x & !EP_ACK)
#define IS_PENDING(x)    ((x & EP_PENDING) == EP_PENDING)
#define SET_PENDING(x)   (x | EP_PENDING)
#define CLEAR_PENDING(x) (x & !EP_PENDING)

typedef struct echo_pdu{
    ep_mtype_t mtype;
    uint8_t    mlen;
    char       msg[256];
}echo_pdu_t;

ep_mtype_t  advance_state_client(ep_mtype_t current_state);
ep_mtype_t  advance_state_server(ep_mtype_t current_state);
bool validate_next_server_client(ep_mtype_t current_state, ep_mtype_t proposed_next_state);
bool validate_next_server_state(ep_mtype_t current_state, ep_mtype_t proposed_next_state);