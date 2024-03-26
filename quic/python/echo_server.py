import asyncio
from typing import Coroutine,Dict
import json

#
# MESSAGES TAKE THE TYPE OF
# msg = {
#     "type": "quic.*",
#     "message": bytes containing the message,
#     "more_data": boolean
# }
#

async def echo_server_proto(scope:Dict, 
        receive:Coroutine, send:Coroutine, close:Coroutine):
        message = await receive()
        raw_data = message.get("body", b"{}")
        packet = json.loads(raw_data.decode('utf-8'))
        print("[svr] received message", packet)
        
        stream_id = message.get("stream_id",-1)
        
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
        await send({
                "type": "echo.response",
                "stream_id": stream_id,
                "message": rsp_msg,
                "more_data": False
        })