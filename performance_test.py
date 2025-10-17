#!/usr/bin/env python3
"""
Performance test script for FadCrypt file locking operations.
Tests locking/unlocking performance with increasing number of files.
"""

import time
import tempfile
import os
import sys
from typing import List, Dict, Tuple
import statistics

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.linux.file_lock_manager_linux import FileLockManagerLinux


def create_test_files(count: int, temp_dir: str) -> List[Dict]:
    """Create test files for performance testing."""
    test_files = []
    for i in range(count):
        file_path = os.path.join(temp_dir, f'test_file_{i:03d}.py')
        with open(file_path, 'w') as f:
            f.write(f'# Test file {i}\nprint("Hello from test file {i}")\n')
        test_files.append({
            'name': f'test_file_{i:03d}.py',
            'path': file_path,
            'type': 'file'
        })
    return test_files


def benchmark_operation(operation_name: str, operation_func, iterations: int = 3) -> Dict:
    """Benchmark an operation and return timing statistics."""
    times = []

    for i in range(iterations):
        start_time = time.perf_counter()
        result = operation_func()
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        times.append(elapsed)
        print(".1f")

    return {
        'operation': operation_name,
        'iterations': iterations,
        'times': times,
        'min_time': min(times),
        'max_time': max(times),
        'avg_time': statistics.mean(times),
        'median_time': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0
    }


def run_performance_test():
    """Run comprehensive performance tests."""
    print("🚀 FadCrypt File Locking Performance Test")
    print("=" * 50)

    # Test with different file counts
    file_counts = [5, 10, 20, 50, 100]

    results = []

    for file_count in file_counts:
        print(f"\n📊 Testing with {file_count} files")
        print("-" * 30)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = create_test_files(file_count, temp_dir)

            # Initialize the file lock manager
            manager = FileLockManagerLinux(temp_dir)
            manager.locked_items = test_files

            # Benchmark locking
            def lock_operation():
                return manager.lock_all_with_configs()

            lock_result = benchmark_operation(f"Lock {file_count} files", lock_operation)
            results.append(lock_result)

            # Benchmark unlocking
            def unlock_operation():
                return manager.unlock_all_with_configs(silent=True)

            unlock_result = benchmark_operation(f"Unlock {file_count} files", unlock_operation)
            results.append(unlock_result)

    # Print summary results
    print("\n📈 PERFORMANCE SUMMARY")
    print("=" * 80)
    print("<12")
    print("-" * 80)

    for result in results:
        print("<12")

    # Analyze scaling performance
    print("\n📊 SCALING ANALYSIS")
    print("-" * 50)

    lock_results = [r for r in results if r['operation'].startswith('Lock')]
    unlock_results = [r for r in results if r['operation'].startswith('Unlock')]

    if lock_results:
        lock_times = [r['avg_time'] for r in lock_results]
        lock_counts = [int(r['operation'].split()[1]) for r in lock_results]

        print("Locking performance:")
        for count, avg_time in zip(lock_counts, lock_times):
            per_file = avg_time / count
            print(".1f")

    if unlock_results:
        unlock_times = [r['avg_time'] for r in unlock_results]
        unlock_counts = [int(r['operation'].split()[1]) for r in unlock_results]

        print("\nUnlocking performance:")
        for count, avg_time in zip(unlock_counts, unlock_times):
            per_file = avg_time / count
            print(".1f")


if __name__ == "__main__":
    run_performance_test()