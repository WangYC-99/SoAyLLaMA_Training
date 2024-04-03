import jsonlines
import json
from inference import *

def v1_answer_gen(round):
    answer_list = []
    with open('./combinations.txt', 'r') as f:
        content = f.read()
        combination_list = content.split('\n')
        f.close()
    with jsonlines.open('/data/wangyuanchun/AMinerS/v1aminer/00{}.jsonl'.format(round), 'r') as f:
        for i, line in enumerate(f):
            query = line["Query"]
            route = combination_list[i]
            result_dict = {}
            process = code_gen(prompt = query, route = route, use_stream=False)

            try:
                result = code_execution(process)
            except:
                result = 'exe error'

            result_dict = {'route' : 'none', 'result' : result}
            print('query: {}; result: {}'.format(query, result))
            answer_list.append(result_dict)
        f.close()
    
    with jsonlines.open('./results/soayBenchv1/00{}.jsonl'.format(round), 'w') as f:
        for each in answer_list:
            f.write(each)

def v1_score():
    em_list = []
    acc_list = []
    wrong_case_list = []
    result_type_list = ['AC: all correct', 'PnB: answer correct but parse not the best', 'PaE: parse error leads to answer wrong', 'PrE: process error(parse correct but answer wrong and not exe error)', 'EE: exe error']
    detail_list = [0, 0, 0, 0, 0]

    # for round in range(0, 44):
    for round in range(1):
        answer_list = []
        expect_list = []
        combination_list = []
        em = 0
        acc = 0
        with open('./results/soayBenchv1/00{}.jsonl'.format(round), 'r') as f:
            for line in f:
                answer_list.append(json.loads(line))
            f.close()

        # with open('/data/wangyuanchun/AMinerS/v1aminer/00{}.jsonl'.format(round), 'r') as f:
        #     expect_list = json.load(f)
        #     f.close()
        with jsonlines.open('/data/wangyuanchun/AMinerS/v1aminer/00{}.jsonl'.format(round), 'r') as f:
            expect_list = []
            for line in f:
                expect_list.append(line)
            f.close()

        with open('./combinations.txt', 'r') as f:
            content = f.read()
            combination_list = content.split('\n')
            f.close()

        for i in range(min(len(answer_list), len(expect_list))):
            if answer_list[i]['result'] == expect_list[i]['Answer']:
                acc += 1
                    
                if answer_list[i]['route'] == combination_list[i]:
                    em += 1
                    detail_list[0] += 1
                elif answer_list[i]['route'] != combination_list[i]:
                    detail_list[1] += 1
            else:
                if answer_list[i]['result'] == "exe error":
                    detail_list[4] += 1
                    with jsonlines.open('./results/soayBenchv1/EE.jsonl', 'a') as f:
                        f.write({'query_id' : i})
                        f.close()
                elif answer_list[i]['route'] == combination_list[i]:
                    detail_list[3] += 1
                    with jsonlines.open('./results/soayBenchv1/WA.jsonl', 'a') as f:
                        f.write({'query_id' : i, 'answer': answer_list[i]['result']})
                        f.close()
                    # print('i:{}, answer:{}; reference:{}'.format(i, answer_list[i]['route'], combination_list[i]))
                elif answer_list[i]['route'] != combination_list[i]:
                    with jsonlines.open('./results/soayBenchv1/WA.jsonl', 'a') as f:
                        f.write({'query_id' : i, 'answer': answer_list[i]['result']})
                        f.close()
                    detail_list[2] += 1
        em_list.append(em / min(len(answer_list), len(expect_list)) * 100)
        acc_list.append(acc / min(len(answer_list), len(combination_list)) * 100)

    avg_em = sum(em_list) / len(em_list)
    avg_acc = sum(acc_list) / len(acc_list)
    print('avg_em: {}; avg_acc: {}'.format(avg_em, avg_acc))
    print('details: \n{}\t{}\t{}\t{}\t{}'.format(100 * detail_list[0] / sum(detail_list), 100 * detail_list[1] / sum(detail_list), 100 * detail_list[2] / sum(detail_list), 100 * detail_list[3] / sum(detail_list), 100 * detail_list[4] / sum(detail_list)))
    # print('details: \nAC: {}; PnB: {}; PaE: {}; PrE: {}; EE: {}'.format(detail_list[0] / sum(detail_list), detail_list[1] / sum(detail_list), detail_list[2] / sum(detail_list), detail_list[3] / sum(detail_list), detail_list[4] / sum(detail_list)))
            
if __name__ == '__main__':
    v1_answer_gen(round = 0)
    v1_score()