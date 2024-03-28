import asyncio
from aioquic.asyncio import connect, serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from typing import Optional, Dict, Callable, Coroutine, Deque, List
from aioquic.tls import SessionTicket

from collections import deque

import json

from echo_quic import EchoQuicConnection, QuicStreamEvent
import echo_server, echo_client

ALPN_PROTOCOL = "echo-protocol"

def build_server_quic_config(cert_file, key_file) -> QuicConfiguration:
    configuration = QuicConfiguration(
        alpn_protocols=[ALPN_PROTOCOL], 
        is_client=False
    )
    configuration.load_cert_chain(cert_file, key_file)
  
    return configuration

def build_client_quic_config(cert_file = None):
    configuration = QuicConfiguration(alpn_protocols=[ALPN_PROTOCOL], 
                                      is_client=True)
    if cert_file:
        configuration.load_verify_locations(cert_file)
  
    return configuration

def create_msg_payload(msg):
    return json.dumps(msg).encode('utf-8')

SERVER_MODE = 0
CLIENT_MODE = 1

class AsyncQuicServer(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handlers: Dict[int, EchoServerRequestHandler] = {}
        self._client_handler: Optional[EchoClientRequestHandler] = None
        self._is_client: bool = self._quic.configuration.is_client
        self._mode: int = SERVER_MODE if not self._is_client else CLIENT_MODE
        if self._mode == CLIENT_MODE:
            self._attach_client_handler()
        
    def _attach_client_handler(self): 
        if self._mode == CLIENT_MODE:
            self._client_handler = EchoClientRequestHandler(
                       authority=self._quic.configuration.server_name,
                        connection=self._quic,
                        protocol=self,
                        scope={},
                        stream_ended=False,
                        stream_id=None,
                        transmit=self.transmit
                 )
        
    def remove_handler(self, stream_id):
        self._handlers.pop(stream_id)
        
    def _quic_client_event_dispatch(self, event):
        if isinstance(event, StreamDataReceived):
            self._client_handler.quic_event_received(event)
        
    def _quic_server_event_dispatch(self, event):
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

    def quic_event_received(self, event):
        if self._mode == SERVER_MODE:
            self._quic_server_event_dispatch(event)
        else:
            self._quic_client_event_dispatch(event)
                        
    def is_client(self) -> bool:
        return self._quic.configuration.is_client

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
    print("[svr] Server starting...")  
    await serve(server, server_port, configuration=configuration, 
            create_protocol=AsyncQuicServer,
            session_ticket_fetcher=SessionTicketStore().pop,
            session_ticket_handler=SessionTicketStore().add)
    await asyncio.Future()
  
              
async def run_client(server, server_port, configuration):    
    async with connect(server, server_port, configuration=configuration, 
            create_protocol=AsyncQuicServer) as client:
        await asyncio.ensure_future(client._client_handler.launch_echo())

        
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
        self.queue: asyncio.Queue[QuicStreamEvent] = asyncio.Queue()
        self.scope = scope
        self.stream_id = stream_id
        self.transmit = transmit

        if stream_ended:
            self.queue.put_nowait({"type": "quic.stream_end"})
        
    def quic_event_received(self, event: StreamDataReceived) -> None:
        self.queue.put_nowait(
            QuicStreamEvent(event.stream_id, event.data, 
                            event.end_stream)
        )
    async def receive(self) -> QuicStreamEvent:
        queue_item = await self.queue.get()
        return queue_item
    
    async def send(self, message: QuicStreamEvent) -> None:
        self.connection.send_stream_data(
                stream_id=message.stream_id,
                data=message.data,
                end_stream=message.end_stream
        )
        
        self.transmit()
        
    def close(self) -> None:
        self.protocol.remove_handler(self.stream_id)
        self.connection.close()
        
    async def launch_echo(self):
        qc = EchoQuicConnection(self.send, 
                self.receive, self.close, None)
        await echo_server.echo_server_proto(self.scope, 
            qc)
        
        
class EchoClientRequestHandler(EchoServerRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_next_stream_id(self) -> int:
        return self.connection.get_next_available_stream_id()
    
    async def launch_echo(self):
        qc = EchoQuicConnection(self.send, 
                self.receive, self.close, 
                self.get_next_stream_id)
        await echo_client.echo_client_proto(self.scope, 
            qc)