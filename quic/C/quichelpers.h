#pragma once

#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>

#ifndef UNREFERENCED_PARAMETER
#define UNREFERENCED_PARAMETER(P) (void)(P)
#endif

void PrintUsage();
BOOLEAN
GetFlag(int argc,char* argv[],char* name);
const char*
GetValue(int argc,char* argv[],const char* name);
uint8_t DecodeHexChar(char c);
uint32_t DecodeHexBuffer(const char* HexBuffer, uint32_t OutBufferLen, uint8_t* OutBuffer);

uint8_t init_proto_state(uint32_t initial_size);
uint8_t get_proto_state(HQUIC Connection);
int set_proto_state(HQUIC Connection, uint8_t state);
int remove_proto_state(HQUIC Connection);