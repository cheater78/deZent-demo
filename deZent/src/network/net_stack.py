import asyncio
from asyncio import Server, StreamReader, StreamWriter
from dataclasses import dataclass
import ssl
from typing import Callable

from deZent.src.utils.sys_utils import run
from deZent.src.utils.async_thread import AsyncThread

NetworkMessage = bytes

IPAddr = str
default_port: int = 9000
@dataclass(frozen=True) # immutable -> hashable
class NetAddr():
    ip: IPAddr
    port: int = default_port

NetworkMessageCB = Callable[[NetAddr, NetworkMessage], None]
NetworkStateChangeCB = Callable[[NetAddr], None]

class NetworkStack(AsyncThread):

    @staticmethod
    def create_cert(key: str, cert: str, domain:str, ip_addr: IPAddr, ttl_days: int = 365) -> None:
        width: int = 2048

        run([
            "openssl", "req", "-x509", "-newkey", f"rsa:{width}", "-nodes",
            "-keyout", f"{key}",
            "-out", f"{cert}",
            "-days", f"{ttl_days}",
            "-subj", f"/CN={domain}",
            "-addext", f"subjectAltName=DNS:{domain},IP: {ip_addr}"
        ])

    def __init__(self,
                 host: NetAddr,
                 msg_cb: NetworkMessageCB,
                 connection_closed_cb: NetworkStateChangeCB,
                 cert: str = "cert.pem",
                 key: str = "key.pem"):
        self._addr_ = host
        self._msg_cb_: NetworkMessageCB = msg_cb
        self._connection_closed_cb_ = connection_closed_cb

        self._server_: Server
        self._server_ssl_ctx_ = ssl.create_default_context(purpose = ssl.Purpose.CLIENT_AUTH)
        self._server_ssl_ctx_.load_cert_chain(certfile = cert, keyfile = key)

        self._client_ssl_ctx_ = ssl.create_default_context(purpose = ssl.Purpose.SERVER_AUTH)
        self._client_ssl_ctx_.check_hostname = False
        self._client_ssl_ctx_.verify_mode = ssl.CERT_NONE  # TODO: for testing only

        self._connections_: dict[NetAddr, tuple[StreamReader, StreamWriter]] = { }

        AsyncThread.__init__(self, auto_start = True)

    def connect(self, addr: NetAddr) -> None:
        self.dispatch_sync(self.__connect_to_peer__(addr))

    def connections(self) -> list[NetAddr]:
        return list(self._connections_.keys())

    def write(self, addr: NetAddr, msg: NetworkMessage) -> None:
        self.dispatch_sync(self.__connection_write__(addr, msg))

    async def __run__(self) -> None:
        self._server_ = await asyncio.start_server(
            client_connected_cb = self.__connection_open_cb__,
            host = self._addr_.ip,
            port = self._addr_.port,
            ssl = self._server_ssl_ctx_
        )
        print(f"[NetStack] Serving on {self._server_.sockets[0].getsockname()}")
        async with self._server_:
            await self._server_.serve_forever()

    async def __connect_to_peer__(self, addr: NetAddr) -> None:
        if addr == self._addr_:
            raise RuntimeError(f"[NetStack] Cannot connect to self. ({self._addr_})")
        try:
            rw: tuple[StreamReader, StreamWriter] = await asyncio.open_connection(
                host = addr.ip,
                port = addr.port,
                ssl = self._client_ssl_ctx_
            )
            await self.__connection_open_cb__(rw[0], rw[1])
        except Exception as e:
            print(f"[NetStack] Failed to connect to {addr} with error:\n {e}")

    async def __connection_write__(self, addr: NetAddr, msg: bytes) -> None:
        if not addr in self._connections_.keys():
            raise RuntimeError(f"Peer {addr} is not known.")
        rw: tuple[StreamReader, StreamWriter] = self._connections_[addr]
        writer: StreamWriter = rw[1]
        try:
            writer.write(msg)
        except:
            raise RuntimeError(f"Failed to write to peer ({addr}).")

    async def __connection_open_cb__(self, reader: StreamReader, writer: StreamWriter) -> None:
        addr = NetAddr(*writer.get_extra_info('peername'))
        self._connections_[addr] = (reader, writer)
        print(f"[NetStack] Open connection to: {addr}")
        self.event_loop.create_task(self.__listen_connection__(addr))
    
    async def __connection_close_cb__(self, addr: NetAddr) -> None:
        self._connection_closed_cb_(addr)
        
        rw: tuple[StreamReader, StreamWriter] = self._connections_[addr]
        writer: StreamWriter = rw[1]
        writer.close()
        await writer.wait_closed()
        if addr in self._connections_.keys():
            del self._connections_[addr]
        
        print(f"[NetStack] Connection closed: {addr}")

    async def __listen_connection__(self, addr: NetAddr) -> None:
        rw: tuple[StreamReader, StreamWriter] = self._connections_[addr]
        reader: StreamReader = rw[0]
        try:
            while True:
                data: NetworkMessage = await reader.read(1024)
                if not data:
                    break
                print(f"[NetStack] Received from {addr}: {data.decode().strip()}")
                self._msg_cb_(addr, data)
        except Exception as e:
            print(f"[NetStack] Error with {addr}: {e}")
        finally:
            await self.__connection_close_cb__(addr)