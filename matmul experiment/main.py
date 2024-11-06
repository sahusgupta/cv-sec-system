import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

# Updated model list with more commonly supported models
model_names = [
    "gpt2-medium",
    "facebook/opt-350m",
    "EleutherAI/pythia-160m"  # Replaced MMfreeLM with a more standard model
]

# Remove .cuda() calls and keep models in CPU
models = []
tokenizers = []

print("Loading models...")
for name in model_names:
    print(f"Loading {name}...")
    try:
        model = AutoModelForCausalLM.from_pretrained(name).half()
        tokenizer = AutoTokenizer.from_pretrained(name)
        models.append(model)
        tokenizers.append(tokenizer)
        print(f"Successfully loaded {name}")
    except Exception as e:
        print(f"Error loading {name}: {str(e)}")

# Set pad tokens for tokenizers
for tokenizer in tokenizers:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

def performance(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    input_ids = inputs.input_ids
    attention_mask = inputs.attention_mask
    
    # Track memory usage
    memory_before = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    
    start = time.time()
    with torch.no_grad():
        outs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=128,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1,
            no_repeat_ngram_size=2
        )
    end = time.time()

    memory_after = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
    memory_consumed = (memory_after - memory_before) / (1024**2)  # Convert to MB
    gen_time = end - start
    gen_text = tokenizer.decode(outs[0], skip_special_tokens=True)

    return gen_time, memory_consumed, gen_text

prompt = "Explain how to write an introductory program in python?"  # example prompt
results = {}

# Only process models that were successfully loaded
for name, model, tokenizer in zip(model_names[:len(models)], models, tokenizers):
    print(f"\nProcessing {name}...")
    try:
        time_taken, memory_used, output = performance(model, tokenizer, prompt)
        results[name] = {
            "time_taken": time_taken,
            "memory_used": memory_used,
            "output": output
        }
        print(f"Model: {name}")
        print(f"Time taken: {time_taken:.2f} seconds")
        print(f"Memory used: {memory_used:.2f} MB")
        print(f"Output: {output}\n")
    except Exception as e:
        print(f"Error processing {name}: {str(e)}")

# Print summary of results
print("\nSummary of Results:")
for name, result in results.items():
    print(f"\n{name}:")
    print(f"Time: {result['time_taken']:.2f}s")
    print(f"Memory: {result['memory_used']:.2f}MB")
    print("-" * 50)