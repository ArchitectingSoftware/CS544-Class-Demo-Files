#pragma once

#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>

void PrintClientUsage();
QUIC_STATUS ClientStreamCallback(HQUIC Stream,void* Context,QUIC_STREAM_EVENT* Event);
void ClientSend(HQUIC Connection);
QUIC_STATUS ClientConnectionCallback(HQUIC Connection,void* Context,QUIC_CONNECTION_EVENT* Event);
BOOLEAN ClientLoadConfiguration(BOOLEAN Unsecure,const char* Cert);
void RunClient(int argc, char* argv[]);