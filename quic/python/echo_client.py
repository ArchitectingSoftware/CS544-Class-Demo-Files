
from typing import Dict
import json
from echo_quic import EchoQuicConnection, QuicStreamEvent
import pdu


async def echo_client_proto(scope:Dict, conn:EchoQuicConnection):
    
    #START CLIENT HERE
    print('[cli] starting client')
    datagram = pdu.Datagram(pdu.MSG_TYPE_DATA, "This is a test message")
    
    new_stream_id = conn.new_stream()

    qs = QuicStreamEvent(new_stream_id, datagram.to_bytes(), False)
    await conn.send(qs)
    message:QuicStreamEvent = await conn.receive()
    dgram_resp = pdu.Datagram.from_bytes(message.data)
    print('[cli] got message: ', dgram_resp.msg)
    print('[cli] msg as json: ', dgram_resp.to_json())
    #END CLIENT HERE