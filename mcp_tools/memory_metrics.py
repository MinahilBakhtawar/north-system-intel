import psutil

#track RAM usage

def memory_metrics():
    mem = psutil.virtual_memory()
    total = mem.total
    available = mem.available
    used = mem.used
    percent = mem.percent
    return {
        "total": total,
        "available": available,
        "used": used,
        "percent": percent
    }


