from flask import Flask, request, jsonify

import logging
from flask_cors import CORS
import json
import re
from vllm import LLM, SamplingParams
from aminer_env import *
import time

# llm_name = 'AMinerS_v5_codellama-13b-instruct_bs4-4'
llm_name = 'soayllama_v2-1_7b'
llm = LLM(model="/data/wangyuanchun/AMinerS/output/{}/checkpoint-1000".format(llm_name), tensor_parallel_size=1)

app = Flask(__name__)
CORS(app)
logging.basicConfig(filename='flasklog/AMinerSAPP.log', level=logging.INFO)

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
    aminer_api = aminer()
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

    # bg_text = "Background:\n\nHere are some tool functions you can use. Each function returns a dict or a list of dict.\n------\nsearchPerson(name, organization, interest):\n    person_list = [{'person_id': str, 'name': str, 'num_citation': int, 'interests':list of str, 'num_pubs': int, 'organization': str}, {...}]\n    return person_list\n---\nsearchPublication(publication_info)\n    publication_list = [{'pub_id': str, 'title': str, 'year': time}, {...}]\n    return publication_list\n---\ngetCoauthors(person_id):\n    coauthors_list = [{'person_id': str, 'name': str, 'relation': ['advisor' or 'advisee' or 'coauthor']}, {...}]\n    return coauthors_list\n---\ngetPersonInterest(person_id):\n    return interest_list\n---\ngetPersonPubs(person_id):\n    publication_list = [{'authors_name_list':list of str, 'pub_id':str, 'title':str, 'num_citation':int, 'year':str}]\n    return publication_list\n---\ngetPersonBasicInfo(person_id):\n    person_basic_info = {'person_id': str, 'name': str, 'gender': str, 'organization':str , 'position': str, 'bio': str, 'education_experience': str, 'email': str}\n    return person_basic_info\n---\ngetPublication(pub_id)\n    publication_info = {'abstract' : str, 'author_list': [{'person_id': str, 'name': str, 'organization': str}, {...}], 'num_citation': int, 'year' : int, 'pdf_link': str, 'venue' : str}\n    return publication_info\n------\nYou are given a query. Parse the query into a combination of the given query and write python codes in order to solve it. \nNote that the result must be one of these combination candidates:\nsearhPerson\nsearchPublication\nsearchPerson -> getCoauthors\nsearchPerson -> getPublication\nsearchPerson -> getPersonBasicInfo\nsearchPublication -> getPublication\nsearchPerson -> getCoauthors -> searchPerson\nsearchPerson -> getCoauthors -> getCoauthors\nsearchPerson -> getCoauthors -> getPersonInterest\nsearchPerson -> getPersonPubs -> getPublication\nsearchPublication -> getPublication -> getPersonInterest\nsearchPublication -> getPublication -> getCoauthors\nsearchPublication -> getPublication -> getPersonPubs\nsearchPublication -> getPublication -> getPersonBasicInfo\nsearchPublication -> getPublication -> searchPerson\n\n-----\nQuery:\n"
    new_prompts = []

    for prompt in prompts:
        new_prompt = "[INST]" + prompt + "\n-----\n[/INST]"
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

@app.route('/api/soayllama/getcode', methods = ['POST'])
def getcode():
    try:
        data = request.get_json()
        # query = request.args.get('query')
        query = data['query']
        print('query: {}\n'.format(query))
        output_list, exe_time = code_gen_llm(prompts=[query], llm=llm)
        route = route_extractor(output_list[0])
        code = code_extractor(output_list[0])
        # result = code_executor(code)

        print('route:{}\ncode:{}\nexe_time:{}'.format(route, code, exe_time))
        return jsonify({'message': 'success', 'route' : route, 'code' : code}) 
    except:
        return jsonify({'message': 'failed'}), 400

@app.route('/api/soayllama/purequery', methods = ['GET'])
def routecode():
    try:
        query = request.args.get('query')
        print('query: {}\n'.format(query))
        bg_text = "Background:\n\nHere are some tool functions you can use. Each function returns a dict or a list of dict.\n------\nsearchPerson(name, organization, interest):\n    person_list = [{'person_id': str, 'name': str, 'num_citation': int, 'interests':list of str, 'num_pubs': int, 'organization': str}, {...}]\n    return person_list\n---\nsearchPublication(publication_info)\n    publication_list = [{'pub_id': str, 'title': str, 'year': time}, {...}]\n    return publication_list\n---\ngetCoauthors(person_id):\n    coauthors_list = [{'person_id': str, 'name': str, 'relation': ['advisor' or 'advisee' or 'coauthor']}, {...}]\n    return coauthors_list\n---\ngetPersonInterest(person_id):\n    return interest_list\n---\ngetPersonPubs(person_id):\n    publication_list = [{'authors_name_list':list of str, 'pub_id':str, 'title':str, 'num_citation':int, 'year':str}]\n    return publication_list\n---\ngetPersonBasicInfo(person_id):\n    person_basic_info = {'person_id': str, 'name': str, 'gender': str, 'organization':str , 'position': str, 'bio': str, 'education_experience': str, 'email': str}\n    return person_basic_info\n---\ngetPublication(pub_id)\n    publication_info = {'abstract' : str, 'author_list': [{'person_id': str, 'name': str, 'organization': str}, {...}], 'num_citation': int, 'year' : int, 'pdf_link': str, 'venue' : str}\n    return publication_info\n------\nYou are given a query. Parse the query into a combination of the given query and write python codes in order to solve it. \nNote that the result must be one of these combination candidates:\nsearhPerson\nsearchPublication\nsearchPerson -> getCoauthors\nsearchPerson -> getPublication\nsearchPerson -> getPersonBasicInfo\nsearchPublication -> getPublication\nsearchPerson -> getCoauthors -> searchPerson\nsearchPerson -> getCoauthors -> getCoauthors\nsearchPerson -> getCoauthors -> getPersonInterest\nsearchPerson -> getPersonPubs -> getPublication\nsearchPublication -> getPublication -> getPersonInterest\nsearchPublication -> getPublication -> getCoauthors\nsearchPublication -> getPublication -> getPersonPubs\nsearchPublication -> getPublication -> getPersonBasicInfo\nsearchPublication -> getPublication -> searchPerson\n\n-----\nQuery:\n"
        output_list, exe_time = code_gen_llm(prompts=[bg_text + query], llm=llm)
        route = route_extractor(output_list[0])
        code = code_extractor(output_list[0])
        # result = code_executor(code)

        print('route:{}\ncode:{}\nexe_time:{}'.format(route, code, exe_time))
        return jsonify({'message': 'success', 'route' : route, 'code' : code})
    except:
        return jsonify({'message': 'failed'}), 400

if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 19000)