from multiprocessing import shared_memory
import struct
import threading

# Layout: 4 unsigned 64-bit integers
STRUCT = struct.Struct("QQQQ")
SIZE = STRUCT.size  # 32 bytes

class SharedCounters:
    def __init__(self, name="proxy_counters"):
        self.shm = shared_memory.SharedMemory(create=True, size=SIZE, name=name)
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        with self.lock:
            self.shm.buf[:] = b"\x00" * SIZE

    def read(self):
        with self.lock:
            return STRUCT.unpack(self.shm.buf[:])

    def write(self, values):
        with self.lock:
            self.shm.buf[:] = STRUCT.pack(*values)

    def add(self, sent=0, recv=0, psent=0, precv=0):
        with self.lock:
            cur = STRUCT.unpack(self.shm.buf[:])
            self.shm.buf[:] = STRUCT.pack(
                cur[0] + sent,
                cur[1] + recv,
                cur[2] + psent,
                cur[3] + precv,
            )
