#!/usr/bin/env python3
"""
Test script to profile process scanning performance.
Tests the difference between batch vs per-file process scanning.
"""

import time
import subprocess
import psutil
from typing import Dict, List
import os
import tempfile

def method_1_batch_fuser(file_paths: List[str]) -> Dict[str, List[int]]:
    """CURRENT SLOW METHOD: Calls fuser for all files, then AGAIN for each file individually"""
    file_to_pids = {path: [] for path in file_paths}
    
    if not file_paths:
        return file_to_pids
    
    try:
        # First call: fuser with all files (this is redundant)
        result = subprocess.run(
            ['fuser'] + file_paths,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Second calls: fuser AGAIN for EACH file individually (THIS IS THE BUG!)
        for file_path in file_paths:
            try:
                single_result = subprocess.run(
                    ['fuser', file_path],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if single_result.returncode == 0 and single_result.stdout.strip():
                    file_pids = [int(pid) for pid in single_result.stdout.strip().split() if pid.strip()]
                    file_to_pids[file_path] = file_pids
            except (subprocess.TimeoutExpired, ValueError):
                pass
                
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return file_to_pids


def method_2_optimized_fuser(file_paths: List[str]) -> Dict[str, List[int]]:
    """OPTIMIZED METHOD: Parse fuser output properly in one call"""
    file_to_pids = {path: [] for path in file_paths}
    
    if not file_paths:
        return file_to_pids
    
    try:
        # Single lsof call to get all files at once (lsof outputs one line per file)
        result = subprocess.run(
            ['lsof'] + file_paths,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        pid = int(parts[1])
                        # Find which file this line refers to
                        # The file path is typically in parts[-1] or reconstructed from line
                        for file_path in file_paths:
                            if file_path in line:
                                if pid not in file_to_pids[file_path]:
                                    file_to_pids[file_path].append(pid)
                    except ValueError:
                        pass
                        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return file_to_pids


def method_3_psutil_batch(file_paths: List[str]) -> Dict[str, List[int]]:
    """ALTERNATIVE: Use psutil to scan all processes once"""
    file_to_pids = {path: [] for path in file_paths}
    file_set = set(file_paths)
    
    try:
        # Single process scan
        for proc in psutil.process_iter(['pid', 'open_files']):
            try:
                if proc.info['open_files']:
                    for file_info in proc.info['open_files']:
                        if file_info.path in file_set:
                            pid = proc.info['pid']
                            if pid not in file_to_pids[file_info.path]:
                                file_to_pids[file_info.path].append(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    
    return file_to_pids


def benchmark_methods():
    """Run benchmarks on all methods"""
    
    # Create test files
    print("📝 Creating test files...")
    test_files = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(4):
            filepath = os.path.join(tmpdir, f"test_file_{i}.txt")
            with open(filepath, 'w') as f:
                f.write(f"Test file {i}")
            test_files.append(filepath)
        
        print(f"✅ Created {len(test_files)} test files")
        print(f"   Files: {test_files}\n")
        
        # Benchmark current slow method
        print("=" * 60)
        print("METHOD 1: CURRENT (SLOW) - Per-file fuser calls")
        print("=" * 60)
        start = time.time()
        result1 = method_1_batch_fuser(test_files)
        elapsed1 = time.time() - start
        print(f"⏱️  Time: {elapsed1:.4f}s")
        print(f"   Result: {result1}\n")
        
        # Benchmark optimized lsof method
        print("=" * 60)
        print("METHOD 2: OPTIMIZED - Single lsof call")
        print("=" * 60)
        start = time.time()
        result2 = method_2_optimized_fuser(test_files)
        elapsed2 = time.time() - start
        print(f"⏱️  Time: {elapsed2:.4f}s")
        print(f"   Result: {result2}\n")
        
        # Benchmark psutil method
        print("=" * 60)
        print("METHOD 3: ALTERNATIVE - psutil batch scan")
        print("=" * 60)
        start = time.time()
        result3 = method_3_psutil_batch(test_files)
        elapsed3 = time.time() - start
        print(f"⏱️  Time: {elapsed3:.4f}s")
        print(f"   Result: {result3}\n")
        
        # Summary
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Current (slow method):  {elapsed1:.4f}s  (BASELINE)")
        print(f"Optimized (lsof):       {elapsed2:.4f}s  ({elapsed1/max(elapsed2, 0.001):.1f}x faster)")
        print(f"Alternative (psutil):   {elapsed3:.4f}s  ({elapsed1/max(elapsed3, 0.001):.1f}x faster)")
        
        print("\n💡 ISSUE ANALYSIS:")
        print("   The current method calls 'fuser' TWICE:")
        print("   1. First call: fuser [file1] [file2] [file3] [file4]")
        print("   2. Then for EACH file: fuser [file1], fuser [file2], etc.")
        print(f"   Total: {len(test_files) + 1} subprocess calls instead of 1!")
        print(f"   This causes exponential CPU usage with more files.")


if __name__ == "__main__":
    print("\n🔍 FadCrypt Process Scanning Performance Test\n")
    benchmark_methods()
