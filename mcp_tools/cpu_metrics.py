import psutil

def cpu_metrics():
    total_percent = psutil.cpu_percent(interval=1)
    per_core = psutil.cpu_percent(interval=1, percpu=True)
    num_cores = psutil.cpu_count(logical=True)
    # maybe load avg or othe important info
    metrics = {"total percent": total_percent, 
               "per core percent": per_core,
               "num cores": num_cores}
    return metrics

def top_processes(n=5):
    # return top n processes by cpu usage
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        processes.append(proc.info)
    processes.sort(key=lambda p: p['cpu_percent'], reverse=True)
    return processes[:n]


