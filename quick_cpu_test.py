#!/usr/bin/env python3
"""
Quick CPU Test for FadCrypt

This script does a quick test to estimate CPU usage before running full FadCrypt.
Helps verify if optimizations are working.

Usage: python3 quick_cpu_test.py
"""

import psutil
import time
import os

def test_process_scanning_methods():
    """Compare different process scanning methods"""
    
    print("🧪 FadCrypt CPU Usage Quick Test")
    print("=" * 60)
    
    # Method 1: Old approach (full scan with all attributes)
    print("\n1️⃣  Testing OLD method (full scan with 4 attributes)...")
    start = time.perf_counter()
    count1 = 0
    for proc in psutil.process_iter(['name', 'pid', 'cmdline', 'status']):
        count1 += 1
    time1 = time.perf_counter() - start
    print(f"   Scanned {count1} processes in {time1*1000:.2f}ms")
    
    # Method 2: New approach (name/pid only, then full details for matches)
    print("\n2️⃣  Testing NEW method (light scan, then full details for matches)...")
    start = time.perf_counter()
    count2 = 0
    matches = []
    # First pass: light scan
    for proc in psutil.process_iter(['name', 'pid']):
        count2 += 1
        # Simulate finding ~5 matches
        if proc.info['name'].lower() in ['chrome', 'firefox', 'python3']:
            matches.append(proc)
    # Second pass: full details for matches only
    for proc in matches:
        try:
            proc.as_dict(attrs=['name', 'pid', 'cmdline', 'status'])
        except:
            pass
    time2 = time.perf_counter() - start
    print(f"   Scanned {count2} processes in {time2*1000:.2f}ms")
    print(f"   Found {len(matches)} matching processes")
    
    # Comparison
    print("\n📊 COMPARISON:")
    print(f"   Old method: {time1*1000:.2f}ms")
    print(f"   New method: {time2*1000:.2f}ms")
    speedup = time1 / time2
    print(f"   Speedup: {speedup:.2f}x faster ✨")
    
    # CPU estimation
    print("\n💻 CPU USAGE ESTIMATE:")
    
    # With 0.1s sleep (10 checks/sec)
    cpu_old_01 = (time1 * 10) * 100
    cpu_new_01 = (time2 * 10) * 100
    print(f"\n   With 0.1s sleep (10 checks/sec):")
    print(f"   ├─ Old method: ~{cpu_old_01:.1f}% per app")
    print(f"   ├─ New method: ~{cpu_new_01:.1f}% per app")
    print(f"   └─ For 3 apps: {cpu_old_01*3:.1f}% → {cpu_new_01*3:.1f}% ✅")
    
    # With 0.5s sleep (2 checks/sec)
    cpu_new_05 = (time2 * 2) * 100
    print(f"\n   With 0.5s sleep (2 checks/sec) - RECOMMENDED:")
    print(f"   ├─ New method: ~{cpu_new_05:.1f}% per app")
    print(f"   └─ For 3 apps: ~{cpu_new_05*3:.1f}% ✅✅")
    
    # Recommendation
    print("\n🎯 RECOMMENDATION:")
    if cpu_new_05 * 3 < 10:
        print("   ✅ CPU usage looks good! Should work well with the new optimizations.")
    elif cpu_new_05 * 3 < 20:
        print("   ⚠️  Moderate CPU usage. Consider increasing sleep to 1.0s if needed.")
    else:
        print("   ❌ High CPU usage. Your system has many processes. Consider single-threaded monitoring.")
    
    print("\n" + "=" * 60)
    print("Ready to test FadCrypt? Run: python3 FadCrypt_Linux.py")
    print("=" * 60)

if __name__ == "__main__":
    test_process_scanning_methods()

def test_single_vs_multi_thread():
    """Show CPU difference between single-threaded and multi-threaded monitoring"""
    
    print("\n\n🔄 SINGLE-THREAD vs MULTI-THREAD COMPARISON")
    print("=" * 60)
    
    # Quick scan time
    start = time.perf_counter()
    for proc in psutil.process_iter(['name', 'pid']):
        pass
    scan_time = time.perf_counter() - start
    
    print(f"\nSingle process scan time: {scan_time*1000:.2f}ms")
    
    # Multi-threaded (old way): 3 apps = 3 scans
    multi_cpu = (scan_time * 3 * 2) * 100  # 3 apps × 2 checks/sec
    print(f"\n📈 MULTI-THREADED (3 separate threads):")
    print(f"   ├─ 3 apps × {scan_time*1000:.2f}ms = {scan_time*3*1000:.2f}ms per cycle")
    print(f"   ├─ 2 cycles/sec (0.5s sleep)")
    print(f"   └─ Total CPU: ~{multi_cpu:.1f}% 😰")
    
    # Single-threaded (new way): 1 scan for all apps
    single_cpu = (scan_time * 2) * 100  # 1 scan × 2 checks/sec
    print(f"\n🎯 SINGLE-THREADED (unified monitoring):")
    print(f"   ├─ 1 scan × {scan_time*1000:.2f}ms = {scan_time*1000:.2f}ms per cycle")
    print(f"   ├─ 2 cycles/sec (0.5s sleep)")
    print(f"   └─ Total CPU: ~{single_cpu:.1f}% 🎉")
    
    print(f"\n💡 SAVINGS: {multi_cpu - single_cpu:.1f}% CPU reduction!")
    print(f"   Improvement: {multi_cpu / single_cpu:.1f}x more efficient")
    
    print("\n" + "=" * 60)

# Run both tests
if __name__ == "__main__":
    test_process_scanning_methods()
    test_single_vs_multi_thread()
