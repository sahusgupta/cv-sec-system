import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

model_names = ["gpt2-medium", "facebook/opt-350m", "ridger/MMfreeLM-370M"]

models = [AutoModelForCausalLM.from_pretrained(name).half().cuda() for name in model_names]
tokenizers = [AutoTokenizer.from_pretrained(name) for name in model_names]

for tokenizer in tokenizers:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

def performance(model, tokenizer, prompt):
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    input_ids = inputs.input_ids.cuda()
    attention_mask = inputs.attention_mask.cuda()
    torch.cuda.reset_peak_memory_stats()
    start = time.time()
    with torch.no_grad():
        outs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=128,
            pad_token_id = tokenizer.eos_token_id,
            repetition_penalty=1.1,
            no_repeat_ngram_size=2
        )
    end = time.time()

    peak_memory = torch.cuda.max_memory_allocated()
    gen_time = end - start
    memory_consumed = peak_memory / (1024**2)
    gen_text = tokenizer.decode(outs[0], skip_special_tokens=True)

    return gen_time, memory_consumed, gen_text

prompt = "What are the benefits of renewable energy?" #example prompt
results = {}
for name, model, tokenizer in zip(model_names, models, tokenizers):
	time_taken, memory_used, output = performance(model, tokenizer,prompt)
	results[name] = {
	    "time_taken": time_taken,
	    "memory_used": memory_used,
	    "output": output
	}
	print(f"Model: {name}\nTime taken: {time_taken} seconds\nMemory used: {memory_used} MB\nOutput: {output}\n")