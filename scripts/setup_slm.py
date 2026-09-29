#!/usr/bin/env python3
"""
O2C AI - Ultralight Small Language Model (SLM) Setup & Verification Utility
Designed for resource-constrained systems (2 CPU Cores, No GPU, 5 GB RAM, 5 GB disk).
Supports pulling, inspecting, and benchmarking ultralight SLMs (qwen2.5:1.5b, qwen2.5:0.5b, llama3.2:1b).
"""

import sys
import os
import time
import argparse
import shutil
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.llm_provider import (
    LLMProvider,
    LLMProviderConfig,
    SLM_PRESETS,
    DEFAULT_SLM_MODEL
)


def get_system_resources() -> dict:
    """Inspect local CPU cores, RAM, and disk space"""
    import os
    info = {"cpu_cores": os.cpu_count() or 1, "ram_total_gb": None, "disk_free_gb": None}
    
    # Disk space
    try:
        total, used, free = shutil.disk_usage(BASE_DIR)
        info["disk_free_gb"] = round(free / (1024**3), 2)
        info["disk_total_gb"] = round(total / (1024**3), 2)
    except Exception:
        pass

    # RAM
    try:
        if sys.platform == "win32":
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            info["ram_total_gb"] = round(stat.ullTotalPhys / (1024**3), 2)
            info["ram_avail_gb"] = round(stat.ullAvailPhys / (1024**3), 2)
        elif sys.platform == "linux":
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if "MemTotal" in line:
                        info["ram_total_gb"] = round(int(line.split()[1]) / (1024**2), 2)
                    elif "MemAvailable" in line:
                        info["ram_avail_gb"] = round(int(line.split()[1]) / (1024**2), 2)
    except Exception:
        pass

    return info


def check_ollama_daemon(provider: LLMProvider) -> dict:
    """Probe Ollama daemon and return diagnostic summary"""
    status = provider.check_ollama()
    models = provider.list_installed_ollama_models()
    return {
        "status": status,
        "models": models
    }


def pull_model(provider: LLMProvider, model_name: str) -> bool:
    """Pull model with progress reporting"""
    print(f"\n[*] Initiating pull for SLM model: '{model_name}'...")
    preset = SLM_PRESETS.get(model_name, {})
    if preset:
        print(f"    Expected download size: ~{preset.get('download_size_mb', 'N/A')} MB")
        print(f"    Estimated RAM usage:   ~{preset.get('ram_footprint_mb', 'N/A')} MB")
        print(f"    Description:           {preset.get('description', '')}")

    print(f"[*] Contacting Ollama daemon at {provider.config.ollama_host}...")
    start_time = time.time()
    res = provider.pull_ollama_model(model_name)
    elapsed = round(time.time() - start_time, 1)

    if res.get("success"):
        print(f"[+] Model '{model_name}' pulled successfully in {elapsed}s!")
        return True
    else:
        print(f"[-] Pull failed: {res.get('message')}")
        print("\n[!] Manual fallback command:")
        print(f"    ollama pull {model_name}\n")
        return False


def run_benchmark(provider: LLMProvider) -> None:
    """Benchmark local SLM CPU inference speed and latency"""
    print(f"\n[*] Running CPU inference benchmark on '{provider.config.ollama_model}'...")
    print("    Prompt: 'Analyze this shipment delay: order 800000000000001 delayed 14 hrs. Suggest action.'")
    res = provider.benchmark_ollama_cpu()

    if res.get("success"):
        print(f"[+] Benchmark completed successfully!")
        print(f"    Latency:          {res.get('latency_sec')} s")
        print(f"    Approx Tokens:    {res.get('approx_tokens')}")
        print(f"    Throughput:       {res.get('tokens_per_sec')} tokens/sec (CPU)")
        print(f"    Sample Output:    \"{res.get('output_sample')}\"")
    else:
        print(f"[-] Benchmark failed: {res.get('error')}")


def main():
    parser = argparse.ArgumentParser(description="O2C AI - Ultralight SLM Setup & Verification")
    parser.add_argument("--check-only", action="store_true", help="Inspect system resources and Ollama status without pulling models")
    parser.add_argument("--model", type=str, default=DEFAULT_SLM_MODEL, help=f"SLM model to set up (default: {DEFAULT_SLM_MODEL})")
    parser.add_argument("--host", type=str, default="http://127.0.0.1:11434", help="Ollama host URL")
    parser.add_argument("--benchmark", action="store_true", help="Run token throughput benchmark after check/pull")
    parser.add_argument("--list-presets", action="store_true", help="List all available ultralight SLM presets and exit")
    args = parser.parse_args()

    print("=" * 70)
    print("⚡ O2C AI - Ultralight SLM Environment & Setup Manager")
    print("   Engineered for 2 CPU Cores / 5 GB RAM / 5 GB Disk")
    print("=" * 70)

    if args.list_presets:
        print("\nAvailable Ultralight SLM Profiles:")
        print(f"{'Model Tag':<16} | {'Size':<10} | {'RAM Footprint':<14} | {'CPU Speed':<12} | {'Description'}")
        print("-" * 80)
        for tag, p in SLM_PRESETS.items():
            rec_tag = " (REC)" if p.get("recommended") else ""
            print(f"{tag + rec_tag:<16} | {str(p.get('download_size_mb')) + ' MB':<10} | {str(p.get('ram_footprint_mb')) + ' MB':<14} | {p.get('tokens_per_sec_cpu'):<12} | {p.get('description')}")
        return

    # 1. System Resources Check
    sys_info = get_system_resources()
    print("\n[1] Local System Hardware Profile:")
    print(f"    - CPU Cores:      {sys_info.get('cpu_cores')}")
    print(f"    - Total RAM:      {sys_info.get('ram_total_gb', 'Unknown')} GB (Available: {sys_info.get('ram_avail_gb', 'Unknown')} GB)")
    print(f"    - Free Disk:      {sys_info.get('disk_free_gb', 'Unknown')} GB")

    config = LLMProviderConfig(ollama_host=args.host, ollama_model=args.model)
    provider = LLMProvider(config=config)

    # 2. Ollama Daemon Check
    print(f"\n[2] Probing Local Ollama Daemon at {args.host}...")
    daemon_info = check_ollama_daemon(provider)
    status = daemon_info["status"]
    
    if status.get("available"):
        print(f"[+] Ollama daemon is ONLINE (Ping latency: {status.get('latency_ms', 0):.1f} ms)")
        installed = daemon_info["models"]
        if installed:
            print(f"[+] Installed Models ({len(installed)} found):")
            for m in installed:
                print(f"    - {m['name']} ({m['size_mb']} MB)")
        else:
            print("[-] No models installed yet in Ollama.")

        has_target = status.get("has_target_model")
        if has_target:
            print(f"[+] Target SLM '{args.model}' is ALREADY installed and ready for inference!")
        else:
            print(f"[!] Target SLM '{args.model}' is NOT yet installed.")
            if not args.check_only:
                success = pull_model(provider, args.model)
                if success:
                    has_target = True

        if args.benchmark and has_target:
            run_benchmark(provider)
            
    else:
        print(f"[-] Ollama daemon is OFFLINE or unreachable at {args.host}.")
        print(f"    Status: {status.get('status')} - {status.get('message')}")
        print("\n[!] How to run Ollama:")
        print("    1. Download & install Ollama from: https://ollama.com")
        print("    2. Start the daemon (usually automatic, or run `ollama serve`)")
        print(f"    3. Pull the ultralight SLM: `ollama pull {args.model}`")
        print("\n[+] Note: O2C AI will automatically use Tier 3 Deterministic Model")
        print("    if Ollama is offline, guaranteeing 100% uptime without crashes.")

    print("\n" + "=" * 70)
    print("Setup inspection complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
