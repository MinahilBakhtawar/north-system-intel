"""
CPU-intensive data generation script with configurable parameters.
This script can stress test your system and demonstrate adaptive parameter tuning.
"""

import numpy as np
import time
import argparse
import json
from pathlib import Path
from datetime import datetime


class DataGenerator:
    def __init__(self, matrix_size=1000, iterations=100, parallel_tasks=4, 
                 batch_size=10, output_dir="./data_output"):
        self.matrix_size = matrix_size
        self.iterations = iterations
        self.parallel_tasks = parallel_tasks
        self.batch_size = batch_size
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.stats = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "matrices_generated": 0,
            "parameters": {
                "matrix_size": matrix_size,
                "iterations": iterations,
                "parallel_tasks": parallel_tasks,
                "batch_size": batch_size
            }
        }
    
    def generate_complex_matrix(self):
        """Generate and process a complex matrix with multiple operations."""
        # Create random matrix
        matrix = np.random.randn(self.matrix_size, self.matrix_size)
        
        # Perform CPU-intensive operations
        result = matrix
        result = np.dot(result, result.T)  # Matrix multiplication
        result = np.linalg.svd(result, compute_uv=False)  # Singular value decomposition
        result = np.fft.fft2(matrix)  # 2D FFT
        result = np.abs(result)
        
        return result
    
    def simulate_data_processing(self):
        """Simulate complex data processing with multiple parallel tasks."""
        results = []
        
        for task in range(self.parallel_tasks):
            task_results = []
            for _ in range(self.batch_size):
                data = self.generate_complex_matrix()
                task_results.append(data.mean())
                self.stats["matrices_generated"] += 1
            results.append(np.mean(task_results))
        
        return results
    
    def run(self):
        """Execute the data generation workflow."""
        print(f"Starting data generation with parameters:")
        print(f"  Matrix size: {self.matrix_size}x{self.matrix_size}")
        print(f"  Iterations: {self.iterations}")
        print(f"  Parallel tasks: {self.parallel_tasks}")
        print(f"  Batch size: {self.batch_size}")
        print(f"\nThis will generate {self.iterations * self.parallel_tasks * self.batch_size} matrices total.\n")
        
        self.stats["start_time"] = datetime.now().isoformat()
        start = time.time()
        
        try:
            for i in range(self.iterations):
                iter_start = time.time()
                results = self.simulate_data_processing()
                iter_duration = time.time() - iter_start
                
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start
                    matrices_per_sec = self.stats["matrices_generated"] / elapsed
                    print(f"Iteration {i+1}/{self.iterations} | "
                          f"Time: {iter_duration:.2f}s | "
                          f"Rate: {matrices_per_sec:.1f} matrices/sec")
        
        except KeyboardInterrupt:
            print("\n\nProcess interrupted by user!")
        
        finally:
            end = time.time()
            self.stats["end_time"] = datetime.now().isoformat()
            self.stats["duration_seconds"] = end - start
            
            self.save_stats()
            self.print_summary()
    
    def save_stats(self):
        """Save execution statistics to file."""
        stats_file = self.output_dir / f"run_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        print(f"\nStats saved to: {stats_file}")
    
    def print_summary(self):
        """Print execution summary."""
        print("\n" + "="*60)
        print("EXECUTION SUMMARY")
        print("="*60)
        print(f"Total duration: {self.stats['duration_seconds']:.2f} seconds")
        print(f"Matrices generated: {self.stats['matrices_generated']}")
        print(f"Average rate: {self.stats['matrices_generated']/self.stats['duration_seconds']:.2f} matrices/sec")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description="CPU-intensive data generation for system diagnostics testing"
    )
    parser.add_argument(
        "--matrix-size", 
        type=int, 
        default=1000,
        help="Size of matrices to generate (default: 1000)"
    )
    parser.add_argument(
        "--iterations", 
        type=int, 
        default=100,
        help="Number of iterations (default: 100)"
    )
    parser.add_argument(
        "--parallel-tasks", 
        type=int, 
        default=4,
        help="Number of parallel tasks per iteration (default: 4)"
    )
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=10,
        help="Batch size per task (default: 10)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="./data_output",
        help="Output directory for stats (default: ./data_output)"
    )
    
    args = parser.parse_args()
    
    generator = DataGenerator(
        matrix_size=args.matrix_size,
        iterations=args.iterations,
        parallel_tasks=args.parallel_tasks,
        batch_size=args.batch_size,
        output_dir=args.output_dir
    )
    
    generator.run()


if __name__ == "__main__":
    main()
