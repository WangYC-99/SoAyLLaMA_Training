from vllm import LLM, SamplingParams
import jsonlines
import re
from aminer_env import *
import os
import time

# prompts = [
#     "Could you name a few researchers at OpenAI?",
#     "How many papers has Yann Lecun published?",
#     "How many citations does Neel Sundaresan from Microsoft have?",
#     "List some collaborators of Jing Zhang at Renmin University of China.",
#     "What's the seminal work of Jifan Yu from Tsinghua University?",
#     "Could you suggest some papers about knowledge graph?",
#     "Which research institution is Andrew Ng currently affiliated with?"
# ]

# prompts = [
#     "Could you name a few researchers at OpenAI?"
# ]
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

    # with jsonlines.open('./results/codellama13b/{}.jsonl'.format(epoch), 'w') as f:
    #     for each in outputs:
    #         generated_text = each.outputs[0].text
    #         f.write({'generated_text' : generated_text})
    #     f.close()

def interaction():
    # llm_name = 'AMinerS_v5_codellama-13b-instruct_bs4-4'
    llm_name = 'soayllama_v2_7b'

    llm = LLM(model="/data/wangyuanchun/AMinerS/output/{}/checkpoint-1500".format(llm_name), tensor_parallel_size=1)
    
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

# def acc_score(epoch):

#     answer_list = []
#     with jsonlines.open('/data/wangyuanchun/AMinerS/soayBench_v1-2-1/{}.jsonl'.format(epoch), 'r') as f:
#         for line in f:
#             prompts.append(line['Query_en'])
#             answer_list.append(line['Answer'])

#     code_list = []
#     with jsonlines.open('./results/codellama13b/{}.jsonl'.format(epoch), 'r') as f:
#         for line in f:
#             code_list.append(match_after_newline(line['generated_text']))
#         f.close()

#     acc = 0

#     result_list = []

#     for i, code in enumerate(code_list):
#         result = code_execution(code)
#         answer = answer_list[i]
#         print('query_id: {}, result: {}, answer: {}'.format(i, result, answer))
#         if result == answer:
#             acc += 1
#         result_list.append({'result' : result, 'answer' : answer, 'is_correct' : result == answer, 'code' : code})
#     acc = acc / len(code_list)

#     print(acc)
#     return acc, result_list

def main():
    llm_name = 'soayllama_v2_7b'

    llm = LLM(model="/data/wangyuanchun/AMinerS/output/{}/checkpoint-1500".format(llm_name), tensor_parallel_size=1)
    # llm = 'debug'

    for epoch_iterator in range(18):

        query_dict_list = []
        with jsonlines.open('/data/wangyuanchun/AMinerS/soayBench_v1-2-1/{}.jsonl'.format(epoch_iterator), 'r') as f:
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
    main()