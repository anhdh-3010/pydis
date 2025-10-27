import socket
import selectors

from pydis.commands import execute_command
from pydis.protocol import decode_resp

HOST = "127.0.0.1"
PORT = 65432

sel: selectors.BaseSelector = selectors.DefaultSelector()


def accept_connection(server_sock: socket.socket) -> None:
    """Handle when have new connection"""
    conn, addr = server_sock.accept()
    print(f"[NEW CONNECTION] {addr}")
    conn.setblocking(False)  # non-blocking socket
    sel.register(conn, selectors.EVENT_READ, read_client)


def read_client(conn: socket.socket) -> None:
    """Handle data send from client"""
    try:
        data = conn.recv(1024)
    except ConnectionResetError:
        data = b""
    except BlockingIOError:
        return

    if data:
        print(f"[RECEIVE] {conn.getpeername()}: {data!r}")
        parts = decode_resp(data)
        if parts:
            response = execute_command(parts)
        else:
            response = b"-ERR invalid RESP\r\n"

        conn.sendall(response)

    else:
        print(f"[CLOSE] {conn.getpeername()}")
        sel.unregister(conn)
        conn.close()


def main() -> None:
    """Init and run main server"""
    server_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    server_sock.setblocking(False)
    sel.register(server_sock, selectors.EVENT_READ, accept_connection)

    # Register socket server to listen new connection
    print(f"[SERVER] Server running on {HOST}:{PORT}")

    try:
        while True:
            events = sel.select(timeout=None)
            for key, _ in events:
                callback = key.data
                sock = key.fileobj
                callback(sock)
    except KeyboardInterrupt:
        print("\n[SERVER] Closing...")
    finally:
        sel.close()
        server_sock.close()


if __name__ == "__main__":
    main()

