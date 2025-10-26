from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load a small model (this will download it if not already present)
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained(model_name)

# Test the model
messages = [
    {"role": "user", "content": "Who are you?"},
]

print("Tokenizing input...")
inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
)

print("Generating response...")
with torch.no_grad():
    outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7, do_sample=True)

print("Decoding response...")
response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True)
print("Response:", response)