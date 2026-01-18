"""
CPU-intensive data generation script.
North will start this with different parameters based on system load.

Usage:
  python stress_workload.py --intensity high
  python stress_workload.py --matrix-size 1000 --iterations 100
"""

import numpy as np
import time
import argparse
import sys


def run_workload(matrix_size, iterations, parallel_tasks, batch_size):
    """Execute CPU-intensive matrix operations."""
    print(f"\n{'='*60}")
    print(f"STARTING WORKLOAD")
    print(f"{'='*60}")
    print(f"Matrix size: {matrix_size}x{matrix_size}")
    print(f"Iterations: {iterations}")
    print(f"Parallel tasks: {parallel_tasks}")
    print(f"Batch size: {batch_size}")
    print(f"Total matrices: {iterations * parallel_tasks * batch_size}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    matrices_processed = 0
    
    try:
        for iteration in range(iterations):
            iter_start = time.time()
            
            # Process batches in parallel tasks
            for task in range(parallel_tasks):
                for batch in range(batch_size):
                    # Create random matrix
                    matrix = np.random.randn(matrix_size, matrix_size)
                    
                    # CPU-intensive operations
                    result = np.dot(matrix, matrix.T)  # Matrix multiplication
                    result = np.linalg.svd(result, compute_uv=False)  # SVD
                    result = np.fft.fft2(matrix)  # 2D FFT
                    
                    matrices_processed += 1
            
            iter_time = time.time() - iter_start
            
            # Progress update every 10 iterations
            if (iteration + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = matrices_processed / elapsed
                print(f"[{iteration+1}/{iterations}] "
                      f"Time: {iter_time:.2f}s | "
                      f"Rate: {rate:.1f} matrices/sec | "
                      f"Total: {matrices_processed}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user!")
    
    finally:
        total_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"WORKLOAD COMPLETE")
        print(f"{'='*60}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Matrices processed: {matrices_processed}")
        print(f"Average rate: {matrices_processed/total_time:.2f}/sec")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="CPU stress test workload")
    
    # Preset intensity levels
    parser.add_argument(
        "--intensity",
        choices=["low", "medium", "high", "extreme"],
        help="Preset intensity level"
    )
    
    # Custom parameters
    parser.add_argument("--matrix-size", type=int, help="Matrix dimension")
    parser.add_argument("--iterations", type=int, help="Number of iterations")
    parser.add_argument("--parallel-tasks", type=int, help="Parallel tasks per iteration")
    parser.add_argument("--batch-size", type=int, help="Batch size per task")
    
    args = parser.parse_args()
    
    # Preset configurations
    presets = {
        "low": {
            "matrix_size": 500,
            "iterations": 30,
            "parallel_tasks": 1,
            "batch_size": 5
        },
        "medium": {
            "matrix_size": 800,
            "iterations": 50,
            "parallel_tasks": 2,
            "batch_size": 8
        },
        "high": {
            "matrix_size": 1200,
            "iterations": 100,
            "parallel_tasks": 4,
            "batch_size": 10
        },
        "extreme": {
            "matrix_size": 1500,
            "iterations": 200,
            "parallel_tasks": 8,
            "batch_size": 15
        }
    }
    
    # Determine parameters
    if args.intensity:
        params = presets[args.intensity]
    else:
        params = {
            "matrix_size": args.matrix_size or 1000,
            "iterations": args.iterations or 50,
            "parallel_tasks": args.parallel_tasks or 2,
            "batch_size": args.batch_size or 8
        }
    
    run_workload(**params)


if __name__ == "__main__":
    main()