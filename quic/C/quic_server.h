#pragma once

#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>

void ServerSend(HQUIC Stream);
QUIC_STATUS ServerStreamCallback(HQUIC Stream, void* Context, QUIC_STREAM_EVENT* Event);
QUIC_STATUS ServerConnectionCallback(HQUIC Connection, void* Context, QUIC_CONNECTION_EVENT* Event);
QUIC_STATUS ServerListenerCallback(HQUIC Listener, void* Context, QUIC_LISTENER_EVENT* Event);
BOOLEAN ServerLoadConfiguration(int argc,char* argv[]);
void RunServer(int argc,char* argv[]);
