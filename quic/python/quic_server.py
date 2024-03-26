import asyncio
from aioquic.asyncio import connect, serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from typing import Optional, Dict, Callable, Deque, List
from aioquic.tls import SessionTicket

from collections import deque

import json

import echo_server

ALPN_PROTOCOL = "echo-protocol"

def build_server_quic_config(cert_file, key_file) -> QuicConfiguration:
    configuration = QuicConfiguration(
        alpn_protocols=[ALPN_PROTOCOL], 
        is_client=False
    )
    configuration.load_cert_chain(cert_file, key_file)
  
    return configuration

def create_msg_payload(msg):
    return json.dumps(msg).encode('utf-8')


class AsyncQuicServer(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handlers: Dict[int, EchoServerRequestHandler] = {}
        
    def remove_handler(self, stream_id):
        self._handlers.pop(stream_id)

    def quic_event_received(self, event):
        handler = None
        if isinstance(event, StreamDataReceived):
            if event.stream_id not in self._handlers:
                 handler = EchoServerRequestHandler(
                        authority=self._quic.configuration.server_name,
                        connection=self._quic,
                        protocol=self,
                        scope={},
                        stream_ended=False,
                        stream_id=event.stream_id,
                        transmit=self.transmit
                 )
                 self._handlers[event.stream_id] = handler
                 handler.quic_event_received(event)
                 asyncio.ensure_future(handler.launch_echo())
            else:
                handler = self._handlers[event.stream_id]
                handler.quic_event_received(event)
                 



class SessionTicketStore:
    """
    Simple in-memory store for session tickets.
    """

    def __init__(self) -> None:
        self.tickets: Dict[bytes, SessionTicket] = {}

    def add(self, ticket: SessionTicket) -> None:
        self.tickets[ticket.ticket] = ticket

    def pop(self, label: bytes) -> Optional[SessionTicket]:
        return self.tickets.pop(label, None)


async def run_server(server, server_port, configuration):    
    await serve(server, server_port, configuration=configuration, 
            create_protocol=AsyncQuicServer,
            session_ticket_fetcher=SessionTicketStore().pop,
            session_ticket_handler=SessionTicketStore().add)
    await asyncio.Future()
    
    
async def read_data(reader: asyncio.StreamReader) -> bytes:
        data = await reader.read()
        return data

        
class EchoServerRequestHandler:
    def __init__(
        self,
        *,
        authority: bytes,
        connection: AsyncQuicServer,
        protocol: QuicConnectionProtocol,
        scope: Dict,
        stream_ended: bool,
        stream_id: int,
        transmit: Callable[[], None],
    ) -> None:
        self.authority = authority
        self.connection = connection
        self.protocol = protocol
        self.queue: asyncio.Queue[Dict] = asyncio.Queue()
        self.scope = scope
        self.stream_id = stream_id
        self.transmit = transmit

        if stream_ended:
            self.queue.put_nowait({"type": "quic.stream_end"})
        
    def quic_event_received(self, event: StreamDataReceived) -> None:
        self.queue.put_nowait(
            {
                "type": "quic.request",
                "stream_id": event.stream_id,
                "body": event.data,
                "more_data": not event.end_stream,
            }
        )
    async def receive(self) -> Dict:
        return await self.queue.get()
    
    async def send(self, message: Dict) -> None:
        print("ABOUT TO SND ", message)
        self.connection.send_stream_data(
                stream_id=self.stream_id,
                data=message.get("message", b""),
                end_stream=not message.get("more_body", False),
            )
        self.transmit()
        
    def close(self) -> None:
        self.protocol.remove_handler(self.stream_id)
        self.connection.close()
        
        
    async def launch_echo(self):
        await echo_server.echo_server_proto(self.scope, 
            self.receive, self.send, self.close)
        
        
    
    
        