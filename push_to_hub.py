from transformers import AutoModelForCausalLM, AutoTokenizer
import json

with open('config/inference_config.json', 'w') as f:
    config_dict = json.read(f)
    f.close()

checkpoint = "{}/{}/checkpoint-{}".format(config_dict['save_path'], config_dict['llm_name'], config_dict['checkpoint_iteration'])

model = AutoModelForCausalLM.from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# Do whatever with the model, train it, fine-tune it...

model.save_pretrained("/data/wangyuanchun/AMinerS/soayllama_v2_7b")
tokenizer.save_pretrained("/data/wangyuanchun/AMinerS/soayllama_v2_7b")