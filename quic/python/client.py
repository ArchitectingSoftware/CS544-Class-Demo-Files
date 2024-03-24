import asyncio
from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from typing import Optional

import json

def create_msg_payload(msg):
    return json.dumps(msg).encode('utf-8')


class EchoClientProtocol(QuicConnectionProtocol):
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
            #self._ack_waiter = None
            waiter.set_result(answer)

async def main():
    # Establish QUIC connection
    configuration = QuicConfiguration(alpn_protocols=["echo-protocol"], 
                                      is_client=True)
    configuration.load_verify_locations('./certs/quic_certificate.pem')
    
    async with connect('localhost', 4433, configuration=configuration, 
            create_protocol=EchoClientProtocol) as client:
         
        s1 = client._quic.get_next_available_stream_id()
        msg_with_pdu = {
            "stream_type": "cmd",
            "stream_id": s1,
            "state": "start_stream",
            "data": "This is the cmd stream"
        }
        msg = create_msg_payload(msg_with_pdu)
        rsp = await client.send_message(msg, s1)
        print("<--",rsp, "\n")
        
        s2 = client._quic.get_next_available_stream_id()
        data_with_pdu = {
            "stream_type": "data",
            "stream_id": s2,
            "state": "start_stream",
            "data": "This is the data stream"
        }
        msg = create_msg_payload(data_with_pdu)
        rsp = await client.send_message(msg, s2)
        print("<--",rsp, "\n")


asyncio.run(main())