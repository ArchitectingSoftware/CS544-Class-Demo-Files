#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>
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


