import asyncio
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
import json

def create_msg_payload(msg):
    return json.dumps(msg).encode('utf-8')

class QuicEchoProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            packet_data = event.data.decode('utf-8')
            
            packet = json.loads(packet_data)
            print("PACKET ",packet, "\n")
            
            rsp_msg = rsp_msg = {
                    "stream_type": "error",
                    "stream_id": event.stream_id,
                    "state": "error_state",
                    "data": "This is an error message"
                }
            if packet['stream_type'] == 'cmd':
                rsp_msg = {
                    "stream_type": "cmd",
                    "stream_id": event.stream_id,
                    "state": "start_stream_ack",
                    "data": "This is the cmd stream starting"
                }
            elif packet['stream_type'] == 'data':
                rsp_msg = {
                    "stream_type": "data",
                    "stream_id": event.stream_id,
                    "state": "start_stream_ack",
                    "data": "This is the data stream starting"
                }
                
            rsp_bytes = create_msg_payload(rsp_msg)

            # send answer
            self._quic.send_stream_data(event.stream_id, rsp_bytes)

async def main():
    # Create QUIC server
    configuration = QuicConfiguration(
        alpn_protocols=["doq"],
        is_client=False
    )
    configuration.load_cert_chain('./certs/quic_certificate.pem', 
                                  './certs/quic_private_key.pem')
    await serve('localhost', 4433, configuration=configuration, 
                create_protocol=QuicEchoProtocol)
    await asyncio.Future()

asyncio.run(main())
