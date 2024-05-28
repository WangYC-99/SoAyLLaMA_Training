from vllm import LLM, SamplingParams
import jsonlines
import re
from aminer_env import *
import os
import time

def route_extractor(string):
    match = re.search(r'Route:\n(.*?)\n-----\n', string, re.DOTALL)
    if match:
        return match.group(1)
    return 'route parsing error'

def code_extractor(string):
    match = re.search(r'Code:\n(.*)', string, re.DOTALL)
    if match:
        return match.group(1)
    return 'code exrtaction error'

def code_executor(process):
    aminer_api = aminer_soay()
    global searchPerson 
    global searchPublication
    global getCoauthors 
    global getPersonInterest
    global getPersonPubs
    global getPersonBasicInfo
    global getPublication
    searchPerson = aminer_api.searchPersonComp
    searchPublication = aminer_api.searchPublication
    getCoauthors = aminer_api.getCoauthors
    getPersonInterest = aminer_api.getPersonInterest
    getPersonPubs = aminer_api.getPersonPubs
    getPersonBasicInfo = aminer_api.getPersonBasicInfo
    getPublication = aminer_api.getPublication
    # print('generated process: \n', process)   
    try: 
    #     # final_result = ''
        exec(process, globals())
        result = final_result
    except:
        result = 'exe error'
    # print('code_gen result: {}'.format(result))
    return result

def code_gen_llm(prompts, llm):

    bg_text = "Background:\n\nHere are some tool functions you can use. Each function returns a dict or a list of dict.\n------\nsearchPerson(name, organization, interest):\n    person_list = [{'person_id': str, 'name': str, 'num_citation': int, 'interests':list of str, 'num_pubs': int, 'organization': str}, {...}]\n    return person_list\n---\nsearchPublication(publication_info)\n    publication_list = [{'pub_id': str, 'title': str, 'year': time}, {...}]\n    return publication_list\n---\ngetCoauthors(person_id):\n    coauthors_list = [{'person_id': str, 'name': str, 'relation': ['advisor' or 'advisee' or 'coauthor']}, {...}]\n    return coauthors_list\n---\ngetPersonInterest(person_id):\n    return interest_list\n---\ngetPersonPubs(person_id):\n    publication_list = [{'authors_name_list':list of str, 'pub_id':str, 'title':str, 'num_citation':int, 'year':str}]\n    return publication_list\n---\ngetPersonBasicInfo(person_id):\n    person_basic_info = {'person_id': str, 'name': str, 'gender': str, 'organization':str , 'position': str, 'bio': str, 'education_experience': str, 'email': str}\n    return person_basic_info\n---\ngetPublication(pub_id)\n    publication_info = {'abstract' : str, 'author_list': [{'person_id': str, 'name': str, 'organization': str}, {...}], 'num_citation': int, 'year' : int, 'pdf_link': str, 'venue' : str}\n    return publication_info\n------\nYou are given a query. Parse the query into a combination of the given query and write python codes in order to solve it. \nNote that the result must be one of these combination candidates:\nsearhPerson\nsearchPublication\nsearchPerson -> getCoauthors\nsearchPerson -> getPublication\nsearchPerson -> getPersonBasicInfo\nsearchPublication -> getPublication\nsearchPerson -> getCoauthors -> searchPerson\nsearchPerson -> getCoauthors -> getCoauthors\nsearchPerson -> getCoauthors -> getPersonInterest\nsearchPerson -> getPersonPubs -> getPublication\nsearchPublication -> getPublication -> getPersonInterest\nsearchPublication -> getPublication -> getCoauthors\nsearchPublication -> getPublication -> getPersonPubs\nsearchPublication -> getPublication -> getPersonBasicInfo\nsearchPublication -> getPublication -> searchPerson\n\n-----\nQuery:\n"

    new_prompts = []

    for prompt in prompts:
        new_prompt = "[INST]" + bg_text + prompt + "\n-----\n[/INST]"
        new_prompts.append(new_prompt)

    sampling_params = SamplingParams(temperature=0, top_p=0.95, max_tokens=512)

    bg_time = time.time()
    outputs = llm.generate(new_prompts, sampling_params)
    generated_txt_list = []
    for each in outputs:
        generated_txt_list.append(each.outputs[0].text)
    end_time = time.time()
    
    # generated_txt_list = ['debug']

    return generated_txt_list, end_time - bg_time

def interaction(inference_config_dict):   

    llm_name = inference_config_dict['llm_name']
    save_path = inference_config_dict['save_path']
    checkpoint_iteration = inference_config_dict['checkpoint_iteration']
    test_dataset_path = inference_config_dict['test_dataset_path']
    llm_name = 'soayllama_v2_7b'

    llm = LLM(model="{}/{}/checkpoint-{}".format(save_path, llm_name, checkpoint_iteration), tensor_parallel_size=1)

    
    while(True):
        prompt = input('Please input your question here (e for exit, r for rewrite):\n')
        if prompt == 'e':
            break
        elif prompt == 'r':
            continue
        else:
            output_list, exe_time = code_gen_llm(prompts=[prompt], llm=llm)
            route = route_extractor(output_list[0])
            code = code_extractor(output_list[0])
            result = code_executor(code)

            print('route:{}\ncode:{}\nresult:{}\nexe_time:{}'.format(route, code, result, exe_time))
    
    print('thanks for using.')


def main(inference_config_dict):

    llm_name = inference_config_dict['llm_name']
    save_path = inference_config_dict['save_path']
    checkpoint_iteration = inference_config_dict['checkpoint_iteration']
    test_dataset_path = inference_config_dict['test_dataset_path']

    llm = LLM(model="{}/{}/checkpoint-{}".format(save_path, llm_name, checkpoint_iteration), tensor_parallel_size=1)
    # llm = 'debug'

    for epoch_iterator in range(18):

        query_dict_list = []
        with jsonlines.open('{}/{}.jsonl'.format(test_dataset_path, epoch_iterator), 'r') as f:
            for line in f:
                query_dict_list.append(line)

        for query_iterator in range(44):

            query_list = [query_dict_list[query_iterator]['Query_en']]
            output_list, exe_time = code_gen_llm(query_list, llm)

            route = route_extractor(output_list[0])
            code = code_extractor(output_list[0])
            result = code_executor(code)

            dir_path = './results/{}'.format(llm_name)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            with jsonlines.open('{}/{}.jsonl'.format(dir_path, epoch_iterator), 'a') as f:
                f.write({'Query_en' : query_dict_list[query_iterator]['Query_en'], 'Answer' : query_dict_list[query_iterator]['Answer'], 'route' : route, 'code' : code, 'result' : result, 'exe_time' : exe_time})
                f.close()

if __name__ == '__main__':
    with open('config/inference_config.json', 'r') as f:
        inference_config_dict = json.load(f)
        f.close()

    if inference_config_dict['inference_mode'] == 'interaction':
        interaction(inference_config_dict)
    else:
        main(inference_config_dict)