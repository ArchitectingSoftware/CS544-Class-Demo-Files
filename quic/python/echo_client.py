import asyncio
from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from typing import Optional

import quic_client

import json

def create_msg_payload(msg):
    return json.dumps(msg).encode('utf-8')


async def run_client(server, server_port, configuration):
    async with connect(server, server_port, configuration=configuration, 
            create_protocol=quic_client.AsyncQuicClient) as client:
        
        #CLIENT APP PROTOCOL STARTS HERE
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
