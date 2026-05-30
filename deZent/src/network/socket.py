import asyncio
from asyncio import AbstractEventLoop, Server, StreamReader, StreamWriter
import threading
from dataclasses import dataclass
import ssl

from deZent.src.utils.sys_utils import run


VNetStackID = int
class VirtualNetStack():

    def __init__(self, client_id: VNetStackID, ) -> None:
        pass

IPAddr = str
default_port: int = 9000
@dataclass(frozen=True) # immutable -> hashable
class NetAddr():
    ip: IPAddr
    port: int = default_port

class NetStack():

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
                 cert: str = "cert.pem",
                 key: str = "key.pem"):
        self.addr = host

        self.server: Server
        self.server_ssl_ctx = ssl.create_default_context(purpose = ssl.Purpose.CLIENT_AUTH)
        self.server_ssl_ctx.load_cert_chain(certfile = cert, keyfile = key)

        self.client_ssl_ctx = ssl.create_default_context(purpose = ssl.Purpose.SERVER_AUTH)
        self.client_ssl_ctx.check_hostname = False
        self.client_ssl_ctx.verify_mode = ssl.CERT_NONE  # TODO: for testing only

        self.connections: dict[NetAddr, tuple[StreamReader, StreamWriter]] = { }

        self.event_loop: AbstractEventLoop = asyncio.new_event_loop()
        self.thread = threading.Thread(
            target=self.__thread_runner__,
            daemon=True
        )

    def open(self) -> None:
        self.thread.start()

    def close(self) -> None:
        pass

    def connect(self, addr: NetAddr) -> None:
        future = asyncio.run_coroutine_threadsafe(
            self.__connect_to_peer__(addr),
            self.event_loop
        )
        return future.result()
    
    def write(self, addr: NetAddr, msg: bytes) -> None:
        future = asyncio.run_coroutine_threadsafe(
            self.__connection_write__(addr, msg),
            self.event_loop
        )
        return future.result()
    
    def get_peers(self) -> list[NetAddr]:
        return list(self.connections.keys())

    def __thread_runner__(self) -> None:
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.create_task(self.__run__())
        self.event_loop.run_forever()

    async def __run__(self) -> None:
        self.server = await asyncio.start_server(
            client_connected_cb = self.__connection_open_cb__,
            host = self.addr.ip,
            port = self.addr.port,
            ssl= self.server_ssl_ctx
        )
        addr = self.server.sockets[0].getsockname()
        print(f"[NetStack] Serving on {addr}")
        async with self.server:
            await self.server.serve_forever()

    async def __connect_to_peer__(self, addr: NetAddr) -> None:
        if addr == self.addr:
            raise RuntimeError(f"[NetStack] Cannot connect to self. ({self.addr})")
        try:
            rw: tuple[StreamReader, StreamWriter] = await asyncio.open_connection(
                host = addr.ip,
                port = addr.port,
                ssl = self.client_ssl_ctx
            )
            await self.__connection_open_cb__(rw[0], rw[1])
        except Exception as e:
            print(f"[NetStack] Failed to connect to {addr} with error:\n {e}")

    async def __connection_write__(self, addr: NetAddr, msg: bytes) -> None:
        if not addr in self.get_peers():
            raise RuntimeError(f"Peer {addr} is not known.")
        rw: tuple[StreamReader, StreamWriter] = self.connections[addr]
        writer: StreamWriter = rw[1]
        try:
            writer.write(msg)
        except:
            raise RuntimeError(f"Failed to write to peer ({addr}).")

    async def __connection_open_cb__(self, reader: StreamReader, writer: StreamWriter) -> None:
        addr = NetAddr(*writer.get_extra_info('peername'))
        self.connections[addr] = (reader, writer)
        print(f"[NetStack] Open connection to: {addr}")
        self.event_loop.create_task(self.__listen_connection__(addr))
    
    async def __connection_close_cb__(self, addr: NetAddr) -> None:
        rw: tuple[StreamReader, StreamWriter] = self.connections[addr]
        writer: StreamWriter = rw[1]

        writer.close()
        await writer.wait_closed()
        if addr in self.connections.keys():
            del self.connections[addr]
        
        print(f"[NetStack] Connection closed: {addr}")

    async def __listen_connection__(self, addr: NetAddr) -> None:
        rw: tuple[StreamReader, StreamWriter] = self.connections[addr]
        reader: StreamReader = rw[0]

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                print(f"[NetStack] Received from {addr}: {data.decode().strip()}")
        except Exception as e:
            print(f"[NetStack] Error with {addr}: {e}")
        finally:
            await self.__connection_close_cb__(addr)