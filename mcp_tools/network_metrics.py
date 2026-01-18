import psutil

def bandwidth_metrics():
    bandwidth_info = psutil.net_io_counters()
    bytes_sent = bandwidth_info.bytes_sent
    bytes_recv = bandwidth_info.bytes_recv
    # maybe load avg or othe important info
    metrics = {"bytes sent": bytes_sent, 
               "bytes received": bytes_received,
               }
    return metrics