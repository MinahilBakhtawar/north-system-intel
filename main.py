"""
Complete MCP Server for System Intelligence Monitor
Exposes system diagnostics and workload control to North/Cohere
"""

from north_mcp_python_sdk import NorthMCPServer
from mcp_tools import cpu_metrics, memory_metrics, network_metrics
import subprocess
import psutil
import signal
import atexit
import time


_default_port = 3001

mcp = NorthMCPServer("System Intelligence Monitor", host="0.0.0.0", port=_default_port)

# Track running workload process globally
_workload_process = None

# Store process references globally
running_processes = {}


# ============================================================================
# MONITORING TOOLS
# ============================================================================

@mcp.tool()
def cpu_status() -> dict:
    """Get current CPU metrics and top processes consuming CPU."""
    metrics = cpu_metrics.cpu_metrics()
    top_procs = cpu_metrics.top_processes()
    return {
        "cpu_metrics": metrics,
        "top_processes": top_procs
    }


@mcp.tool()
def memory_status() -> dict:
    """Get current memory usage metrics."""
    metrics = memory_metrics.memory_metrics()
    return {"memory_metrics": metrics}


@mcp.tool()
def bandwidth_status(interval: float = 1.0) -> dict:
    """Get current bandwidth usage (bytes/sec, packets/sec)."""
    return network_metrics.bandwidth_metrics(interval=interval)


@mcp.tool()
def bandwidth_alert(threshold_mb_s: float = 10.0) -> dict:
    """Check if inbound bandwidth exceeds threshold."""
    return network_metrics.bandwidth_alert(threshold_mb_s=threshold_mb_s)


@mcp.tool()
def bandwidth_by_interface(interval: float = 1.0) -> dict:
    """Get bandwidth usage breakdown by network interface (WiFi vs Ethernet)."""
    return network_metrics.bandwidth_by_interface(interval=interval)


# ============================================================================
# WORKLOAD CONTROL TOOLS
# ============================================================================

@mcp.tool()
def start_workload(
    matrix_size: int = 1000, 
    iterations: int = 50, 
    parallel_tasks: int = 2, 
    batch_size: int = 8
) -> dict:
    """
    Start a CPU-intensive workload with specified parameters.
    
    Args:
        matrix_size: Dimension of matrices (e.g., 1000 for 1000x1000)
        iterations: Number of iterations to run
        parallel_tasks: Number of parallel tasks per iteration
        batch_size: Batch size per task
    
    Returns:
        Status and process information
    """
    global _workload_process
    
    # Validate parameters
    if matrix_size <= 0 or iterations <= 0 or parallel_tasks <= 0 or batch_size <= 0:
        return {
            "success": False,
            "error": "All parameters must be positive integers"
        }
    
    if matrix_size > 5000 or iterations > 1000 or parallel_tasks > 16 or batch_size > 100:
        return {
            "success": False,
            "error": "Parameters exceed safe limits (matrix_size<=5000, iterations<=1000, parallel_tasks<=16, batch_size<=100)"
        }
    
    # Check if workload already running
    if _workload_process and _workload_process.poll() is None:
        return {
            "success": False,
            "error": "Workload already running",
            "pid": _workload_process.pid
        }
    
    # Start new workload
    cmd = [
        "python", "stress_workload.py",
        "--matrix-size", str(matrix_size),
        "--iterations", str(iterations),
        "--parallel-tasks", str(parallel_tasks),
        "--batch-size", str(batch_size)
    ]
    
    try:
        _workload_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return {
            "success": True,
            "message": "Workload started successfully",
            "pid": _workload_process.pid,
            "parameters": {
                "matrix_size": matrix_size,
                "iterations": iterations,
                "parallel_tasks": parallel_tasks,
                "batch_size": batch_size,
                "total_matrices": iterations * parallel_tasks * batch_size
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start workload: {str(e)}"
        }


@mcp.tool()
def stop_workload() -> dict:
    """
    Stop the currently running workload gracefully.
    
    Returns:
        Status of termination
    """
    global _workload_process
    
    if not _workload_process or _workload_process.poll() is not None:
        return {
            "success": False,
            "message": "No workload currently running"
        }
    
    try:
        # Graceful termination
        _workload_process.terminate()
        _workload_process.wait(timeout=5)
        
        return {
            "success": True,
            "message": "Workload stopped gracefully"
        }
    except subprocess.TimeoutExpired:
        # Force kill if graceful termination fails
        _workload_process.kill()
        _workload_process.wait()
        
        return {
            "success": True,
            "message": "Workload force-stopped (did not respond to graceful termination)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to stop workload: {str(e)}"
        }


@mcp.tool()
def workload_status() -> dict:
    """
    Check if workload is running and get its current status.
    
    Returns:
        Current workload status including PID, CPU usage, and memory
    """
    global _workload_process
    
    if not _workload_process:
        return {
            "running": False,
            "message": "No workload has been started yet"
        }
    
    # Store PID before checking if running to avoid race condition
    pid = _workload_process.pid
    is_running = _workload_process.poll() is None
    
    if is_running:
        try:
            # Get process info
            proc = psutil.Process(pid)
            return {
                "running": True,
                "pid": pid,
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_mb": round(proc.memory_info().rss / (1024 * 1024), 2),
                "status": proc.status()
            }
        except psutil.NoSuchProcess:
            return {
                "running": False,
                "message": "Process terminated unexpectedly"
            }
    else:
        return_code = _workload_process.returncode
        return {
            "running": False,
            "message": "Workload completed",
            "return_code": return_code,
            "success": return_code == 0
        }


@mcp.tool()
def get_system_capacity() -> dict:
    """
    Analyze current system state and recommend workload parameters.
    Uses current CPU and memory load to suggest appropriate intensity.
    
    Returns:
        Current system state and recommended parameters
    """
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    cpu_count = psutil.cpu_count(logical=True)
    
    # Calculate recommended parameters based on current load
    if cpu_percent > 80 or mem.percent > 80:
        intensity = "low"
        params = {
            "matrix_size": 500,
            "iterations": 30,
            "parallel_tasks": 1,
            "batch_size": 5
        }
        reasoning = "System is currently under high load - recommend light workload"
    elif cpu_percent > 50 or mem.percent > 60:
        intensity = "medium"
        params = {
            "matrix_size": 800,
            "iterations": 50,
            "parallel_tasks": 2,
            "batch_size": 8
        }
        reasoning = "System is moderately loaded - recommend medium workload"
    elif cpu_percent > 25:
        intensity = "high"
        params = {
            "matrix_size": 1000,
            "iterations": 75,
            "parallel_tasks": 3,
            "batch_size": 10
        }
        reasoning = "System has good capacity - recommend high workload"
    else:
        intensity = "maximum"
        params = {
            "matrix_size": 1200,
            "iterations": 100,
            "parallel_tasks": 4,
            "batch_size": 12
        }
        reasoning = "System is mostly idle - can handle maximum workload"
    
    return {
        "current_state": {
            "cpu_percent": round(cpu_percent, 1),
            "cpu_count": cpu_count,
            "memory_percent": round(mem.percent, 1),
            "available_memory_gb": round(mem.available / (1024**3), 2),
            "total_memory_gb": round(mem.total / (1024**3), 2)
        },
        "recommended_intensity": intensity,
        "recommended_parameters": params,
        "reasoning": reasoning
    }


@mcp.tool()
def app_deploy():
    """Deploy the application stack"""
    global running_processes
    
    try:
        # Start server first
        server = subprocess.Popen(
            ["python", "demo/server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        running_processes['server'] = server
        time.sleep(2)  # Give server time to start
        
        # Start proxy
        proxy = subprocess.Popen(
            ["python", "demo/proxy.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        running_processes['proxy'] = proxy
        time.sleep(4)
        
        # Start app
        app = subprocess.Popen(
            ["python", "demo/dummy_app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        running_processes['app'] = app
        
        # Verify all are running
        for name, proc in running_processes.items():
            if proc.poll() is not None:
                raise RuntimeError(f"{name} failed to start")
        
        return "Deployment successful: server, proxy, and app are running"
    
    except Exception as e:
        # Cleanup on failure
        app_shutdown()
        return f"Deployment failed: {str(e)}"


@mcp.tool()
def app_shutdown():
    """Stop all running processes"""
    global running_processes
    
    for name, proc in running_processes.items():
        if proc.poll() is None:  # Still running
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    running_processes.clear()
    return "All processes stopped"


@mcp.tool()
def app_bandwidth() -> dict:
    """Get bandwidth metrics for the application"""
    metrics = network_metrics.app_bandwidth_metrics()
    return {"app_bandwidth": metrics}


# ============================================================================
# CLEANUP FUNCTIONS
# ============================================================================

def cleanup_all():
    """Cleanup all processes on exit"""
    global _workload_process
    
    # Shutdown app processes
    app_shutdown()
    
    # Shutdown workload process
    if _workload_process and _workload_process.poll() is None:
        _workload_process.terminate()
        try:
            _workload_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _workload_process.kill()
            _workload_process.wait()


# Ensure cleanup on exit
atexit.register(cleanup_all)


# ============================================================================
# START SERVER
# ============================================================================

if __name__ == "__main__":
    print("Starting System Intelligence Monitor MCP Server...")
    print(f"Host: 0.0.0.0")
    print(f"Port: {_default_port}")
    mcp.run(transport="streamable-http")