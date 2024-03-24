import asyncio
from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from typing import Optional

ALPN_PROTOCOL = "echo-protocol"

def build_client_quic_config(cert_file = None):
    configuration = QuicConfiguration(alpn_protocols=[ALPN_PROTOCOL], 
                                      is_client=True)
    if cert_file:
        configuration.load_verify_locations(cert_file)
  
    return configuration


class AsyncQuicClient(QuicConnectionProtocol):
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ack_waiter: Optional[asyncio.Future[str]] = None
        
        
     async def send_message(self, message, stream_id):            
        print("-->",message, "\n")
        self._quic.send_stream_data(stream_id, message)
        waiter = self._loop.create_future()
        self._ack_waiter = waiter
        self.transmit()
        return await asyncio.shield(waiter)
        
     def quic_event_received(self, event):
        if isinstance(event, StreamDataReceived):
            answer = event.data.decode('utf-8')
            waiter = self._ack_waiter
            waiter.set_result(answer)
