import time
import requests

start_time = time.time()
response = requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "messages": [{"role": "user", "content": "Write a 200-word essay on AI ethics."}]
})
end_time = time.time()

print(f"Total Response Time: {end_time - start_time:.2f} seconds")
print(f"Tokens Generated: {response.json()['usage']['completion_tokens']}")
