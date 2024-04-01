#ifndef _ECHO_CONFIG_
#define _ECHO_CONFIG_

#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>

//QUIC Configuration Information
#define ALPN_NAME "echo-protocol"


//
// The (optional) registration configuration for the app. This sets a name for
// the app (used for persistent storage and for debugging). It also configures
// the execution profile, using the default "low latency" profile.
//
const QUIC_REGISTRATION_CONFIG RegConfig = { ALPN_NAME, QUIC_EXECUTION_PROFILE_LOW_LATENCY };

//
// The protocol name used in the Application Layer Protocol Negotiation (ALPN).
//
const QUIC_BUFFER Alpn = { sizeof(ALPN_NAME) - 1, (uint8_t*)ALPN_NAME };

//
// The UDP port used by the server side of the protocol.
//
const uint16_t UdpPort = 4567; 

//
// The default idle timeout period (1 second) used for the protocol.
//
const uint64_t IdleTimeoutMs = 1000;

//
// The length of buffer sent over the streams in the protocol.
//
const uint32_t SendBufferLength = 100;

//
// The QUIC API/function table returned from MsQuicOpen2. It contains all the
// functions called by the app to interact with MsQuic.
//
const QUIC_API_TABLE* MsQuic;

//
// The QUIC handle to the registration object. This is the top level API object
// that represents the execution context for all work done by MsQuic on behalf
// of the app.
//
HQUIC Registration;

//
// The QUIC handle to the configuration object. This object abstracts the
// connection configuration. This includes TLS configuration and any other
// QUIC layer settings.
//
HQUIC Configuration;

//Prototype adds due to issues with msquic.h, see below

//See here:  https://github.com/microsoft/msquic/issues/3012
//Some issue in msquic headers, so we need to define here.  If other exports
//are misssing they can be found here: 
// https://github.com/microsoft/msquic/blob/main/src/platform/inline.c
void
QuicAddrSetFamily(
    _In_ QUIC_ADDR* Addr,
    _In_ QUIC_ADDRESS_FAMILY Family
    );

uint16_t
QuicAddrGetPort(
    _In_ const QUIC_ADDR* const Addr
    );

void
QuicAddrSetPort(
    _Out_ QUIC_ADDR* Addr,
    _In_ uint16_t Port
    );

#endif