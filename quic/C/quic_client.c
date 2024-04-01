#ifdef _WIN32
//
// The conformant preprocessor along with the newest SDK throws this warning for
// a macro in C mode. As users might run into this exact bug, exclude this
// warning here. This is not an MsQuic bug but a Windows SDK bug.
//
#pragma warning(disable:5105)
#endif
#include "msquic.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#include "quic_client.h"
#include "quichelpers.h"
#include "echo_config.h"
#include "echo_proto.h"


//
// The clients's callback for stream events from MsQuic.
//
QUIC_STATUS ClientStreamCallback(
    HQUIC Stream,
    void* Context,
    QUIC_STREAM_EVENT* Event
    )
{
    UNREFERENCED_PARAMETER(Context);
    int rc = 0;
    switch (Event->Type) {
    case QUIC_STREAM_EVENT_START_COMPLETE:
        printf("[strm][%p] Stream started\n", Stream);

        rc = set_proto_state(Stream, EP_ECHO);
        if (rc != 0) {
            printf("[hmap] error inserting connection key...\n");
        }
        printf("[hmap] state set to EP_ECHO...\n");  

        break;
    case QUIC_STREAM_EVENT_SEND_COMPLETE:
        //
        // A previous StreamSend call has completed, and the context is being
        // returned back to the app.
        //
        free(Event->SEND_COMPLETE.ClientContext);
        printf("[strm][%p] Data sent\n", Stream);

        rc = set_proto_state(Stream, EP_ECHO | EP_CLOSED);
        if (rc != 0) {
            printf("[hmap] error changing state to EP_ECHO | EP_CLOSED..\n");
        }
        printf("[hmap] state set to EP_ECHO or EP_CLOSED...\n");  
        break;
    case QUIC_STREAM_EVENT_RECEIVE:
        //
        // Data was received from the peer on the stream.
        //
        printf("[strm][%p] Data received\n", Stream);

        rc = set_proto_state(Stream, EP_ECHO);
        if (rc != 0) {
            printf("[hmap] error changing state to EP_ECHO...\n");
        }
        printf("[hmap] state set to EP_ECHO\n"); 

        break;
    case QUIC_STREAM_EVENT_PEER_SEND_ABORTED:
        //
        // The peer gracefully shut down its send direction of the stream.
        //
        printf("[strm][%p] Peer aborted\n", Stream);

        rc = set_proto_state(Stream, EP_CLOSED);
        if (rc != 0) {
            printf("[hmap] error changing state to EP_CLOSED...\n");
        }
        printf("[hmap] state set to EP_CLOSED\n"); 

        break;
    case QUIC_STREAM_EVENT_PEER_SEND_SHUTDOWN:
        //
        // The peer aborted its send direction of the stream.
        //
        rc = set_proto_state(Stream, EP_CLOSED);
        if (rc != 0) {
            printf("[hmap] error changing state to EP_CLOSED...\n");
        }
        printf("[hmap] state set to EP_CLOSED\n"); 
        printf("[strm][%p] Peer shut down\n", Stream);
        break;
    case QUIC_STREAM_EVENT_SHUTDOWN_COMPLETE:
        //
        // Both directions of the stream have been shut down and MsQuic is done
        // with the stream. It can now be safely cleaned up.
        //
        rc = remove_proto_state(Stream);
        if (rc != 0) {
            printf("[hmap] error removing stream key...\n");
        }
        printf("[hmap] stream key removed, state is EP_NO_STATE...\n");
        printf("[strm][%p] All done\n", Stream);
        if (!Event->SHUTDOWN_COMPLETE.AppCloseInProgress) {
            MsQuic->StreamClose(Stream);
        }
        printf("[strm][%p] Stream closed\n", Stream);
        break;
    default:
        break;
    }
    return QUIC_STATUS_SUCCESS;
}

void
ClientSend(
    HQUIC Connection
    )
{
    QUIC_STATUS Status;
    HQUIC Stream = NULL;
    uint8_t* SendBufferRaw;
    QUIC_BUFFER* SendBuffer;

    //
    // Create/allocate a new bidirectional stream. The stream is just allocated
    // and no QUIC stream identifier is assigned until it's started.
    //
     
    printf("[conn] In client send...\n");
    if (QUIC_FAILED(Status = MsQuic->StreamOpen(Connection, QUIC_STREAM_OPEN_FLAG_NONE, ClientStreamCallback, NULL, &Stream))) {
        printf("StreamOpen failed, 0x%x!\n", Status);
        goto Error;
    }
    int rc = get_proto_state(Stream);
    if (rc != EP_NO_STATE) {
        printf("[hmap] error stream has existing state\n");
        goto Error;
    }
    printf("[hmap] new stream OK, state is EP_NO_STATE\n");

    rc = set_proto_state(Stream, EP_IDLE);
    if (rc != 0) {
        printf("[hmap] error changing state to EP_IDLE...\n");
    }
    printf("[hmap] state set to EP_IDLE\n");
    printf("[strm][%p] Starting...\n", Stream);

    //
    // Starts the bidirectional stream. By default, the peer is not notified of
    // the stream being started until data is sent on the stream.
    //
    if (QUIC_FAILED(Status = MsQuic->StreamStart(Stream, QUIC_STREAM_START_FLAG_NONE))) {
        printf("StreamStart failed, 0x%x!\n", Status);
        MsQuic->StreamClose(Stream);
        goto Error;
    }
    rc = set_proto_state(Stream, EP_CONNECTED);
    if (rc != 0) {
        printf("[hmap] error changing state to EP_CONNECTED...\n");
    }
    printf("[hmap] state set to EP_CONNECTED\n");

    //
    // Allocates and builds the buffer to send over the stream.
    //
    SendBufferRaw = (uint8_t*)malloc(sizeof(QUIC_BUFFER) + SendBufferLength);
    if (SendBufferRaw == NULL) {
        printf("SendBuffer allocation failed!\n");
        Status = QUIC_STATUS_OUT_OF_MEMORY;
        goto Error;
    }
    SendBuffer = (QUIC_BUFFER*)SendBufferRaw;
    SendBuffer->Buffer = SendBufferRaw + sizeof(QUIC_BUFFER);
    SendBuffer->Length = SendBufferLength;

    printf("[strm][%p] Sending data...\n", Stream);

    //
    // Sends the buffer over the stream. Note the FIN flag is passed along with
    // the buffer. This indicates this is the last buffer on the stream and the
    // the stream is shut down (in the send direction) immediately after.
    //
    if (QUIC_FAILED(Status = MsQuic->StreamSend(Stream, SendBuffer, 1, QUIC_SEND_FLAG_FIN, SendBuffer))) {
        printf("StreamSend failed, 0x%x!\n", Status);
        free(SendBufferRaw);
        goto Error;
    }

Error:

    if (QUIC_FAILED(Status)) {
        MsQuic->ConnectionShutdown(Connection, QUIC_CONNECTION_SHUTDOWN_FLAG_NONE, 0);
    }
}

//
// The clients's callback for connection events from MsQuic.
//
QUIC_STATUS ClientConnectionCallback(
    HQUIC Connection,
    void* Context,
    QUIC_CONNECTION_EVENT* Event
    )
{
    UNREFERENCED_PARAMETER(Context);
    switch (Event->Type) {
    case QUIC_CONNECTION_EVENT_CONNECTED:
        //
        // The handshake has completed for the connection.
        //
        printf("[conn][%p] Connected\n", Connection); 

        ClientSend(Connection);
        break;
    case QUIC_CONNECTION_EVENT_SHUTDOWN_INITIATED_BY_TRANSPORT:
        //
        // The connection has been shut down by the transport. Generally, this
        // is the expected way for the connection to shut down with this
        // protocol, since we let idle timeout kill the connection.
        //
        if (Event->SHUTDOWN_INITIATED_BY_TRANSPORT.Status == QUIC_STATUS_CONNECTION_IDLE) {
            printf("[conn][%p] Successfully shut down on idle.\n", Connection);
        } else {
            printf("[conn][%p] Shut down by transport, 0x%x\n", Connection, Event->SHUTDOWN_INITIATED_BY_TRANSPORT.Status);
        }
        break;
    case QUIC_CONNECTION_EVENT_SHUTDOWN_INITIATED_BY_PEER:
        //
        // The connection was explicitly shut down by the peer.
        //
        printf("[conn][%p] Shut down by peer, 0x%llu\n", Connection, (unsigned long long)Event->SHUTDOWN_INITIATED_BY_PEER.ErrorCode);
        break;
    case QUIC_CONNECTION_EVENT_SHUTDOWN_COMPLETE:
        //
        // The connection has completed the shutdown process and is ready to be
        // safely cleaned up.
        //
        printf("[conn][%p] All done\n", Connection);
        if (!Event->SHUTDOWN_COMPLETE.AppCloseInProgress) {
            MsQuic->ConnectionClose(Connection);
        }
        break;
    case QUIC_CONNECTION_EVENT_RESUMPTION_TICKET_RECEIVED:
        //
        // A resumption ticket (also called New Session Ticket or NST) was
        // received from the server.
        //
        printf("[conn][%p] Resumption ticket received (%u bytes):\n", Connection, Event->RESUMPTION_TICKET_RECEIVED.ResumptionTicketLength);
        //for (uint32_t i = 0; i < Event->RESUMPTION_TICKET_RECEIVED.ResumptionTicketLength; i++) {
        //    printf("%.2X", (uint8_t)Event->RESUMPTION_TICKET_RECEIVED.ResumptionTicket[i]);
        //}
        //printf("\n");
        break;
    default:
        break;
    }
    return QUIC_STATUS_SUCCESS;
}

//
// Helper function to load a client configuration.
//
BOOLEAN ClientLoadConfiguration(
    BOOLEAN Unsecure,
    const char* Cert
    )
{
    QUIC_SETTINGS Settings = {0};
    //
    // Configures the client's idle timeout.
    //
    Settings.IdleTimeoutMs = IdleTimeoutMs;
    Settings.IsSet.IdleTimeoutMs = TRUE;

    //
    // Configures a default client configuration, optionally disabling
    // server certificate validation.
    //
    QUIC_CREDENTIAL_CONFIG CredConfig;
    memset(&CredConfig, 0, sizeof(CredConfig));

    //Update for cert file


    CredConfig.Type = QUIC_CREDENTIAL_TYPE_NONE;
    CredConfig.Flags = QUIC_CREDENTIAL_FLAG_CLIENT;
    if (Unsecure) {
        CredConfig.Flags |= QUIC_CREDENTIAL_FLAG_NO_CERTIFICATE_VALIDATION;
    }
    if (Cert != NULL) {
        printf("[cfg ] Cert File: %s\n", Cert);
        CredConfig.Flags |= QUIC_CREDENTIAL_FLAG_SET_CA_CERTIFICATE_FILE;
        CredConfig.CaCertificateFile = Cert;
    }
    
    //
    // Allocate/initialize the configuration object, with the configured ALPN
    // and settings.
    //
    QUIC_STATUS Status = QUIC_STATUS_SUCCESS;
    if (QUIC_FAILED(Status = MsQuic->ConfigurationOpen(Registration, &Alpn, 1, &Settings, sizeof(Settings), NULL, &Configuration))) {
        printf("ConfigurationOpen failed, 0x%x!\n", Status);
        return FALSE;
    }

    //
    // Loads the TLS credential part of the configuration. This is required even
    // on client side, to indicate if a certificate is required or not.
    //
    if (QUIC_FAILED(Status = MsQuic->ConfigurationLoadCredential(Configuration, &CredConfig))) {
        printf("ConfigurationLoadCredential failed, 0x%x!\n", Status);
        return FALSE;
    }

    return TRUE;
}

//
// Runs the client side of the protocol.
//
void
RunClient(
    int argc,
    char* argv[]
    )
{
    //
    // Load the client configuration based on the "unsecure" command line option.
    //
    const char* Cert;
    BOOLEAN unsecure_flag;

    printf("DEBUG: Client Configuration: %d\n", GetFlag(argc, argv, "unsecure"));

    if ((Cert = GetValue(argc, argv, "cert_file")) != NULL) {
        printf("[cfg ] Cert File: %s\n", Cert);
    } else {
        printf("[cfg ] NO CERT File\n");
    }

    unsecure_flag = GetFlag(argc, argv, "unsecure");

    if  (unsecure_flag && Cert != NULL) {
        printf("[cfg ] Must specify -cert-flag or -unsecure, not both, exiting...\n");
        return;
    }

    if (!ClientLoadConfiguration(unsecure_flag, Cert)) {
        printf("ClientLoadConfiguration Unsecure Flag Early Exit!\n");
        return;
    }

    //Create protocol hashmap
    const unsigned initial_size = 2;
    int rc = init_proto_state(initial_size);
    if (rc != 0) {
        printf("[hmap] error creating hashmap, exiting...\n");
        return;
    }
    printf("[hmap] hashmap created...\n");

    QUIC_STATUS Status;
    const char* ResumptionTicketString = NULL;
    HQUIC Connection = NULL;

    //
    // Allocate a new connection object.
    //
    if (QUIC_FAILED(Status = MsQuic->ConnectionOpen(Registration, ClientConnectionCallback, NULL, &Connection))) {
        printf("ConnectionOpen failed, 0x%x!\n", Status);
        goto Error;
    }

    if ((ResumptionTicketString = GetValue(argc, argv, "ticket")) != NULL) {
        //
        // If provided at the command line, set the resumption ticket that can
        // be used to resume a previous session.
        //
        uint8_t ResumptionTicket[10240];
        uint16_t TicketLength = (uint16_t)DecodeHexBuffer(ResumptionTicketString, sizeof(ResumptionTicket), ResumptionTicket);
        if (QUIC_FAILED(Status = MsQuic->SetParam(Connection, QUIC_PARAM_CONN_RESUMPTION_TICKET, TicketLength, ResumptionTicket))) {
            printf("SetParam(QUIC_PARAM_CONN_RESUMPTION_TICKET) failed, 0x%x!\n", Status);
            goto Error;
        }
    }

    //
    // Get the target / server name or IP from the command line.
    //
    const char* Target;
    if ((Target = GetValue(argc, argv, "target")) == NULL) {
        printf("Must specify '-target' argument!\n");
        Status = QUIC_STATUS_INVALID_PARAMETER;
        goto Error;
    }

    printf("[conn][%p] Connecting...\n", Connection);

    //
    // Start the connection to the server.
    //
    if (QUIC_FAILED(Status = MsQuic->ConnectionStart(Connection, Configuration, QUIC_ADDRESS_FAMILY_UNSPEC, Target, UdpPort))) {
        printf("ConnectionStart failed, 0x%x!\n", Status);
        goto Error;
    }
    printf("[conn][%p] Connectection ended\n", Connection);

Error:

    if (QUIC_FAILED(Status) && Connection != NULL) {
        MsQuic->ConnectionClose(Connection);
    }
}
