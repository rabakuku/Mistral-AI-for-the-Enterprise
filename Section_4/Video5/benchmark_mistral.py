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
