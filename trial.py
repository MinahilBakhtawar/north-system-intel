# cpu_burn_multicore.py
import threading

def burn():
    x = 0
    while True:
        x += 1

# Spawn one thread per core (adjust to your core count)
threads = []
for _ in range(8):  # change 8 to number of cores you want
    t = threading.Thread(target=burn)
    t.start()
    threads.append(t)

# Threads run indefinitely; stop with Ctrl+C
