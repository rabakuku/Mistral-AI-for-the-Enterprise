Now that your engine is live, it’s time to see what that **NVIDIA L4** can really do! 🚀 In this section, we will create a professional benchmarking tool to measure the raw speed of your Sovereign Engine.

### 🧪 What does this script do?

This Python script acts as a "speedometer" for your AI by simulating a real-world user request to your local vLLM server. It specifically calculates **Tokens Per Second (TPS)**, which is the industry-standard metric for measuring LLM performance. By tracking the exact time taken from the start of the request to the final word generated, it provides a transparent look at your hardware's efficiency. This allows you to verify that your GPU is properly optimized and delivering the high-speed experience your users expect.




## 🛠️ Lab: Benchmarking Your Mistral Engine

Follow these steps to set up your testing tools directory and run your first performance test.

### **Step 1: Create Your Tools Directory** 📁

We like to keep our engine clean. Let's create a dedicated folder for our diagnostic scripts.

Bash

```javascript
# 1. Elevate to root and move to the root directory
sudo su 
cd /

# 2. Create and enter the 'tools' folder
mkdir -p tools
cd tools

# 3. Refresh your AI environment to ensure the OpenAI library is available
conda activate vllm-env
conda deactivate
conda activate vllm-env

```

### **Step 2: Create the Benchmarking Script** 📄

We will use `nano` to create the script file.

1. Run `nano benchmark_mistral.py`
2. Paste the code below.
3. Save and Exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

```javascript
import time
from openai import OpenAI

# 1. Initialize the client to point to your local Sovereign Engine
# We use the 'OpenAI' class because vLLM mimics the OpenAI API perfectly.
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"  # vLLM doesn't require a key by default
)

def test_inference(prompt: str):
    print(f"[*] Sending Request: {prompt}")
    start_time = time.time()
    
    # 2. Execute the Chat Completion
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.7
    )
    
    end_time = time.time()
    
    # 3. Calculate Performance Metrics
    duration = end_time - start_time
    output_text = response.choices[0].message.content
    tokens_generated = response.usage.completion_tokens
    tps = tokens_generated / duration

    print("-" * 30)
    print(f"Response: {output_text}")
    print("-" * 30)
    print(f"Duration: {duration:.2f} seconds")
    print(f"Speed:    {tps:.2f} tokens/sec")
    print("-" * 30)

if __name__ == "__main__":
    test_inference("Write a 3-paragraph summary on the importance of local LLMs for data privacy.")

```

### **Step 3: Run the Test** ⚡

Now, let's put the L4 to work! Ensure your vLLM service is running in the background, then execute:

Bash

```javascript
python3 benchmark_mistral.py

```




### **Understanding Your Results** 🎓

- **Under 20 tokens/sec:** Your GPU might be throttled or sharing resources with another process (check `nvidia-smi`).
- **30 - 60 tokens/sec:** This is the "Sweet Spot" for an L4! This is faster than a human can read and perfect for a high-end user experience. 🌟
- **Duration:** This shows "Latency"—how long the user has to wait before the entire message is finished.