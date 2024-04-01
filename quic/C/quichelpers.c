#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>
#include "hashmap.h"
#include "quichelpers.h"
#include "echo_config.h"
#include "echo_proto.h"

static struct hashmap_s hashmap;

uint8_t init_proto_state(uint32_t initial_size) {
    return hashmap_create(initial_size, &hashmap);
}
uint8_t get_proto_state(HQUIC Connection) {
    //GET PROTOCOL STATE FROM HASHMAP
    uintptr_t pval = (uintptr_t)EP_NO_STATE;
    void *pstate = hashmap_get(&hashmap, Connection, sizeof(Connection)); 
    if ( pstate != NULL ) {
        pval= (uintptr_t)pstate;
    } 
    return (uint8_t)pval;
}

int set_proto_state(HQUIC Connection, uint8_t state) {
    uintptr_t pval = (uintptr_t)state;
    int rc = hashmap_put(&hashmap, Connection, 
        sizeof(Connection), (void *)pval);
    return rc;
}

int remove_proto_state(HQUIC Connection) {
    int rc = hashmap_remove(&hashmap, Connection, 
        sizeof(Connection));
    return rc;
}


//
// Helper functions to look up a command line arguments.
//


void PrintUsage()
{
    printf(
        "\n"
        "echo runs a simple client or server.\n"
        "\n"
        "Usage:\n"
        "\n"
        "  echo -client -unsecure -target:{IPAddress|Hostname} [-ticket:<ticket>]\n"
        "  echo -server -cert_hash:<...>\n"
        "  echo -server -cert_file:<...> -key_file:<...> [-password:<...>]\n"
        );
}

BOOLEAN
GetFlag(
    int argc,
    char* argv[],
    char* name
    )
{
    const size_t nameLen = strlen(name);
    for (int i = 0; i < argc; i++) {
        if (_strnicmp(argv[i] + 1, name, nameLen) == 0
            && strlen(argv[i]) == nameLen + 1) {
            return TRUE;
        }
    }
    return FALSE;
}

const char*
GetValue(
    int argc,
    char* argv[],
    const char* name
    )
{
    const size_t nameLen = strlen(name);
    for (int i = 0; i < argc; i++) {
        if (_strnicmp(argv[i] + 1, name, nameLen) == 0
            && strlen(argv[i]) > 1 + nameLen + 1
            && *(argv[i] + 1 + nameLen) == ':') {
            return argv[i] + 1 + nameLen + 1;
        }
    }
    return NULL;
}

//
// Helper function to convert a hex character to its decimal value.
//
uint8_t
DecodeHexChar(
    char c
    )
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return 10 + c - 'A';
    if (c >= 'a' && c <= 'f') return 10 + c - 'a';
    return 0;
}

//
// Helper function to convert a string of hex characters to a byte buffer.
//
uint32_t
DecodeHexBuffer(
    const char* HexBuffer,
    uint32_t OutBufferLen,
    uint8_t* OutBuffer
    )
{
    uint32_t HexBufferLen = (uint32_t)strlen(HexBuffer) / 2;
    if (HexBufferLen > OutBufferLen) {
        return 0;
    }

    for (uint32_t i = 0; i < HexBufferLen; i++) {
        OutBuffer[i] =
            (DecodeHexChar(HexBuffer[i * 2]) << 4) |
            DecodeHexChar(HexBuffer[i * 2 + 1]);
    }

    return HexBufferLen;
}


