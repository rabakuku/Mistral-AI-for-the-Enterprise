import torch
import sys
import os

def validate_enclave():
    print("="*50)
    print("🛡️  SOVEREIGN AI ENGINE: GPU VALIDATION")
    print("="*50)

    # 1. Check Python Version
    print(f"🐍 Python Version: {sys.version.split()[0]}")

    # 2. Check Driver Communication
    print(f"📡 Driver Link: ", end="")
    driver_check = os.popen("nvidia-smi --query-gpu=driver_version --format=csv,noheader").read().strip()
    if driver_check:
        print(f"✅ ACTIVE (Driver: {driver_check})")
    else:
        print("❌ FAILED (No NVIDIA driver detected)")

    # 3. Check PyTorch & CUDA
    cuda_available = torch.cuda.is_available()
    print(f"🔥 CUDA Available: {'✅ YES' if cuda_available else '❌ NO'}")

    if cuda_available:
        # 4. Identify the GPU Model
        gpu_name = torch.cuda.get_device_name(0)
        print(f"🎯 Target GPU: {gpu_name}")

        # 5. Memory Statistics (The L4 has 24GB)
        total_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"📊 Total VRAM: {total_mem:.2f} GB")

        # 6. Simple Computation Test
        # We send a small 'tensor' to the GPU to see if it can actually do math.
        try:
            x = torch.tensor([1.0, 2.0]).to("cuda")
            print("⚡ Computation Test: ✅ SUCCESS (GPU is processing math!)")
        except Exception as e:
            print(f"⚡ Computation Test: ❌ FAILED ({str(e)})")
    
    print("="*50)

if __name__ == "__main__":
    validate_enclave()
