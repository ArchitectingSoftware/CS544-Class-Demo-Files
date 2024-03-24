import asyncio
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from typing import Optional

import quic_server

import json



async def run_server(server, server_port, configuration):
    # server = 'localhost'
    # configuration = QuicConfiguration(
    #     alpn_protocols=["echo-protocol"], 
    #     is_client=False
    # )
    # configuration.load_cert_chain('./certs/quic_certificate.pem', 
    #                               './certs/quic_private_key.pem')
    # await serve(server, 4433, configuration=configuration, 
    #             create_protocol=quic_server.AsyncQuicServer)
    # await asyncio.Future()
    
    await serve(server, server_port, configuration=configuration, 
            create_protocol=quic_server.AsyncQuicServer,
            stream_handler=stream_handler)
    await asyncio.Future()
    
    
async def read_data(reader: asyncio.StreamReader) -> bytes:
        data = await reader.read()
        return data

def stream_handler(reader: asyncio.StreamReader, writer:asyncio.StreamWriter):
        print("STREAM HANDLER", reader, writer)
        
        data = read_data(reader)
        print("DATA ", data.decode('utf-8'))
        writer.write(b'Hello World')
        #data = b''
        #while not reader.at_eof():
        #        data += yield from reader.read()
        #print("DATA ", data.decode('utf-8'))
        