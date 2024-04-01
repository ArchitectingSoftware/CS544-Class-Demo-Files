#ifndef _QUIC_CONFIG_
#define _QUIC_CONFIG_

#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>

//QUIC Configuration Information
#define ALPN_NAME "echo-protocol"

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