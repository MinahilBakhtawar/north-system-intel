import socket
import threading
import time
from proxy_counters import SharedCounters

counter = SharedCounters()

# Optional throttle (bytes/sec), None = unlimited
RATE = 1024

# -------------------------
# Proxy connection handler
# -------------------------
def pipe(src, dst, direction: str):
    while True:
        data = src.recv(4096)
        if not data:
            break

        if direction == "recv":
            counter.add(recv=len(data), precv=1)
        else:
            counter.add(sent=len(data), psent=1)

        if RATE:
            time.sleep(len(data) / RATE)

        dst.sendall(data)

    src.close()
    dst.close()


# -------------------------
# HTTP proxy server
# -------------------------
def serve():
    listen = ("127.0.0.1", 8888)
    print("Proxy listening on", listen)

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(listen)
    s.listen()

    while True:
        client, _ = s.accept()

        request = client.recv(8192)
        if not request:
            client.close()
            continue

        first = request.split(b"\r\n", 1)[0]
        method, target, _ = first.split(b" ", 2)

        if method == b"CONNECT":
            host, port = target.split(b":")
            upstream = socket.create_connection((host.decode(), int(port)))
            client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
        else:
            host = target.split(b"://", 1)[1].split(b"/", 1)[0]
            if b":" in host:
                host, port = host.split(b":", 1)
                port = int(port)
            else:
                port = 80

            upstream = socket.create_connection((host.decode(), port))
            upstream.sendall(request)

        threading.Thread(
            target=pipe, args=(client, upstream, "recv"), daemon=True
        ).start()
        threading.Thread(
            target=pipe, args=(upstream, client, "sent"), daemon=True
        ).start()


if __name__ == "__main__":
    serve()

