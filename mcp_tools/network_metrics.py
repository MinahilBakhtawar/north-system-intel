import psutil
import time

def bandwidth_metrics(interval: float = 1.0):
    before = psutil.net_io_counters()
    time.sleep(interval)
    after = psutil.net_io_counters()

    sent_per_sec = (after.bytes_sent - before.bytes_sent) / interval
    recv_per_sec = (after.bytes_recv - before.bytes_recv) / interval

    return {
        "bytes_sent_per_sec": sent_per_sec,
        "bytes_recv_per_sec": recv_per_sec,
        "packets_sent_per_sec": (after.packets_sent - before.packets_sent) / interval,
        "packets_recv_per_sec": (after.packets_recv - before.packets_recv) / interval,
    }


def bandwidth_alert(threshold_mb_s: float = 10.0):
    metrics = bandwidth_metrics()
    recv_mb_s = metrics["bytes_recv_per_sec"] / (1024 * 1024)

    return {
        "high_bandwidth_usage": recv_mb_s > threshold_mb_s,
        "recv_mb_per_sec": recv_mb_s,
        "raw_metrics": metrics
    }


def bandwidth_by_interface(interval: float = 1.0):
    before = psutil.net_io_counters(pernic=True)
    time.sleep(interval)
    after = psutil.net_io_counters(pernic=True)

    result = {}
    for nic in before:
        result[nic] = {
            "bytes_sent_per_sec": (after[nic].bytes_sent - before[nic].bytes_sent) / interval,
            "bytes_recv_per_sec": (after[nic].bytes_recv - before[nic].bytes_recv) / interval,
        }

    return result
