#ifndef _QUIC_CONFIG_
#define _QUIC_CONFIG_

#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>

//QUIC Configuration Information
#define ALPN_NAME "echo-protocol"

//We commonly use bit fields to represent protocol states
//                 16  8  4  2  1
// EP_IDLE          0  0  0  0  0
// EP_CONNECTED     0  0  0  0  1
// EP_ECHO          0  0  0  1  0
// EP_CLOSED        0  0  1  0  0
// EP_ERROR         0  1  0  0  0
// EP_ACK           1  0  0  0  0

//ECHO PROTOCOL INFORMATION
//Protocol States
typedef uint8_t         ep_mtype_t;
#define EP_IDLE         0x00
#define EP_CONNECTED    0x01
#define EP_ECHO         0x02
#define EP_CLOSED       0x04
#define EP_ERROR        0x08
#define EP_ACK          0x10
#define EP_STATE_SZ     sizeof(uint8_t)

//ACK IS TO ACKNOLEDGE SO WE CAN COMBINE AND CHECK FOR ITS
//PRESENCE
#define EP_CONN_ACK     EP_CONNECTED  | EP_ACK
#define EP_ECHO_ACK     EP_ECHO_STATE | EP_ACK
#define EP_CLOSED_ACK   EP_CLOSED     | EP_ACK
#define IS_ACK(x)       ((x & EP_ACK) == EP_ACK)

typedef struct echo_pdu{
    ep_mtype_t mtype;
    uint8_t    mlen;
    char       msg[256];
}echo_pdu_t;
//
// These variable are expected to be setup by the application
//
extern const QUIC_REGISTRATION_CONFIG RegConfig; 
extern const QUIC_BUFFER Alpn;
extern const uint16_t UdpPort;
extern const uint64_t IdleTimeoutMs;
extern const uint32_t SendBufferLength;
extern const QUIC_API_TABLE* MsQuic;
extern HQUIC Registration;
extern HQUIC Configuration;

#endif