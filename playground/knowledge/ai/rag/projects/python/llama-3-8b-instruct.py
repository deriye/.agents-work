import requests

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
headers = {"Authorization": "Bearer <token>"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()
	
system = ""
user = "Afsoomali ma taqaana?"

input = f"""
<|begin_of_text|>

<|start_header_id|>user<|end_header_id|>\n\n{user}<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>\n\n
"""

output = query({
	"inputs": input,
})



print(output[0]['generated_text'])