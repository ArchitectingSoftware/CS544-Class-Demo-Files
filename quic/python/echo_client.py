import asyncio
from typing import Coroutine,Dict, Callable
import json
from echo_quic import EchoQuicConnection, QuicStreamEvent


async def echo_client_proto(scope:Dict, conn:EchoQuicConnection):
    
    #START CLIENT HERE
    print('starting client')
    new_stream_id = conn.new_stream()
    msg_with_pdu = {
        "stream_type": "cmd",
        "stream_id": new_stream_id,
        "state": "start_stream",
        "data": "This is the cmd stream"
    }
    rsp_msg = json.dumps(msg_with_pdu).encode('utf-8')
    qs = QuicStreamEvent(new_stream_id, rsp_msg, False)
    await conn.send(qs)
    message:QuicStreamEvent = await conn.receive()
    print('got message', message.data)
    
    stream2 = conn.new_stream()
    data_with_pdu = {
        "stream_type": "data",
        "stream_id": stream2,
        "state": "start_stream",
        "data": "This is the data stream"
    }
    rsp_msg = json.dumps(data_with_pdu).encode('utf-8')
    qs = QuicStreamEvent(stream2, rsp_msg, False)
    await conn.send(qs)
    message:QuicStreamEvent = await conn.receive()
    print('got message', message.data)
