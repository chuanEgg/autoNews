from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

from accelerate import infer_auto_device_map, init_empty_weights
from transformers import AutoConfig, AutoModelForCausalLM

model = "yentinglin/Taiwan-LLaMa-v1.0"

quantization_config = BitsAndBytesConfig(llm_int8_enable_fp32_cpu_offload=True)
tokenizer = AutoTokenizer.from_pretrained(model)
model_8bit = AutoModelForCausalLM.from_pretrained(model, device_map="auto", load_in_8bit=True, quantization_config=quantization_config, offload_folder="offload", torch_dtype=torch.float16, offload_state_dict = True)

# Get memory usage
model_8bit.get_memory_footprint()

max_tokens = 100
input_ids = tokenizer("NTU 在哪?", return_tensors="pt").input_ids.to('cuda')
outputs = model_8bit.generate(input_ids, max_new_tokens=max_tokens)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))