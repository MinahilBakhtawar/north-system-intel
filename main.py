from north_mcp_python_sdk import NorthMCPServer
from mcp_tools import cpu_metrics, memory_metrics, network_metrics

_default_port = 3001

mcp = NorthMCPServer("System Intelligence Monitor", host="0.0.0.0", port=_default_port)


@mcp.tool()
def cpu_status() -> dict:
    metrics = cpu_metrics.cpu_metrics()
    top_procs = cpu_metrics.top_processes()
    return {
        "cpu_metrics": metrics,
        "top_processes": top_procs
    }


@mcp.tool()
def memory_status() -> dict:
    metrics = memory_metrics.memory_metrics()
    return {"memory_metrics": metrics}


@mcp.tool()
def bandwidth_status(interval: float = 1.0) -> dict:
    # Get current bandwidth usage (bytes/sec, packets/sec).
    return network_metrics.bandwidth_metrics(interval=interval)


@mcp.tool()
def bandwidth_alert(threshold_mb_s: float = 10.0) -> dict:
    #high inbound bandwidth usage
    return network_metrics.bandwidth_alert(threshold_mb_s=threshold_mb_s)


@mcp.tool()
def bandwidth_by_interface(interval: float = 1.0) -> dict:
    # breakdown usage by interface
    return network_metrics.bandwidth_by_interface(interval=interval)

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
