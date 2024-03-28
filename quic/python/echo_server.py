import asyncio
from typing import Coroutine,Dict
import json
from echo_quic import EchoQuicConnection, QuicStreamEvent



async def echo_server_proto(scope:Dict, conn:EchoQuicConnection):
        
        message:QuicStreamEvent = await conn.receive()
        raw_data = message.data
        packet = json.loads(raw_data.decode('utf-8'))
        print("[svr] received message", packet)
        
        stream_id = message.stream_id
        
        rsp_msg = {
                    "stream_type": "error",
                    "stream_id": stream_id,
                    "state": "error_state",
                    "data": "This is an error message"
                }
        if packet['stream_type'] == 'cmd':
                rsp_msg = {
                        "stream_type": "cmd",
                        "stream_id": stream_id,
                        "state": "start_stream_ack",
                        "data": "This is the cmd stream starting"
                }
        elif packet['stream_type'] == 'data':
                rsp_msg = {
                        "stream_type": "data",
                        "stream_id": stream_id,
                        "state": "start_stream_ack",
                        "data": "This is the data stream starting"
                }
                
        
        rsp_msg = json.dumps(rsp_msg).encode('utf-8')
        rsp_evnt = QuicStreamEvent(stream_id, rsp_msg, False)
        await conn.send(rsp_evnt)