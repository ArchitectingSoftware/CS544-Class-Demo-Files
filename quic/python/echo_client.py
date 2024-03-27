import asyncio
from typing import Coroutine,Dict, Callable
import json


async def echo_client_proto(scope:Dict, get_stream:Callable,
        receive:Coroutine, send:Coroutine, close:Coroutine):
    
    #START CLIENT HERE
    print('starting client')
    new_stream_id = get_stream()
    msg_with_pdu = {
        "stream_type": "cmd",
        "stream_id": new_stream_id,
        "state": "start_stream",
        "data": "This is the cmd stream"
    }
    rsp_msg = json.dumps(msg_with_pdu).encode('utf-8')
    await send({
                "type": "echo.send",
                "stream_id": new_stream_id,
                "message": rsp_msg,
                "more_data": False
    })
    message = await receive()
    print('got message', message)
    