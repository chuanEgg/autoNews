from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch


model = "yentinglin/Taiwan-LLM-7B-v2.0.1-chat"

quantization_config = BitsAndBytesConfig(llm_int8_enable_fp32_cpu_offload=True)
tokenizer = AutoTokenizer.from_pretrained(model, use_auth_token=True)
model_8bit = AutoModelForCausalLM.from_pretrained(
    model, device_map="auto", 
    load_in_8bit=True, 
    quantization_config=quantization_config, 
    offload_folder="offload", 
    torch_dtype=torch.float16, 
    offload_state_dict = True,
    use_auth_token=True,
)

max_tokens = 100
input_ids = tokenizer("NTU 在哪?", return_tensors="pt").input_ids.to('cuda')
outputs = model_8bit.generate(input_ids, max_new_tokens=max_tokens)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))