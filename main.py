from north_mcp_python_sdk import NorthMCPServer
from mcp_tools import cpu_metrics

_default_port = 3001

mcp = NorthMCPServer("CPU Monitor", host="0.0.0.0", port=_default_port)

@mcp.tool()
def cpu_status() -> dict:
    metrics = cpu_metrics.cpu_metrics()
    top_procs = cpu_metrics.top_processes()
    return {
        "cpu_metrics": metrics,
        "top_processes": top_procs
    }

    
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
