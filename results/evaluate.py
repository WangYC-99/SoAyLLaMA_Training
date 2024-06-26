import json
from json.encoder import py_encode_basestring_ascii
import re
import math
import jsonlines

acc_list = []
wrong_case_list = []
result_type_list = ['AC: all correct', 'PnB: answer correct but parse not the best', 'PaE: parse error leads to answer wrong', 'PrE: process error(parse correct but answer wrong and not exe error)', 'EE: exe error']
detail_list = [[0] * 5 for _ in range(18)]
target = 'v5_codellama-13b'
# begin_num = 1
# end_num = 9
# begin_num = 9
# end_num = 31
# begin_num = 31
# end_num = 45
begin_num = 1
end_num = 45

for round in range(18):
    answer_list = []
    answer_list = []
    combination_list = []
    acc = 0
    with jsonlines.open('./{}/{}.jsonl'.format(target, round), 'r') as f:
        tag = begin_num
        for line in f:
            if tag == end_num: 
                break
            answer_list.append(line)
            tag += 1
        f.close()

    with open('./combinations.txt', 'r') as f:
        content = f.read()
        combination_list = content.split('\n')
        f.close()

    for i in range(min(len(answer_list), len(answer_list))):
        if answer_list[i]['result'] == answer_list[i]['Answer']:
            acc += 1
            if answer_list[i]['route'] == combination_list[i]:
                detail_list[round][0] += 1
            elif answer_list[i]['route'] != combination_list[i]:
                detail_list[round][1] += 1
        else:
            if answer_list[i]['result'] == "exe error":
                detail_list[round][4] += 1
            elif answer_list[i]['route'] == combination_list[i]:
                detail_list[round][3] += 1
                # print('i:{}, answer:{}; reference:{}'.format(i, answer_list[i]['route'], combination_list[i]))
            elif answer_list[i]['route'] != combination_list[i]:
                # print('answer:{}\n expected:{}'.format(answer_list[i]['route'], combination_list[i]))
                detail_list[round][2] += 1
    acc_list.append(acc / min(len(answer_list), len(answer_list)) * 100)

def calculate_variance(o_data):
    data = [d for d in o_data if d != 0]
    n = len(data)
    if n == 0:
        return 0.00
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    variance = math.sqrt(variance)
    return variance

avg_acc = sum(acc_list) / len(acc_list)
# avg_acc = sum(p_acc_list) / len(p_acc_list)
percentage_list = [[0] * 5 for _ in range(18)]

for j in range(18):
    each = detail_list[j]
    new_list = [0, 0, 0, 0, 0]
    for i in range(5):
        percentage_list[j][i] = 100 * each[i] / sum(each)

# print(percentage_list)
pnb = [percentage_list[i][1] for i in range(18)]
sw = [percentage_list[i][2] for i in range(18)]
pw = [percentage_list[i][3] for i in range(18)]
ee = [percentage_list[i][4] for i in range(18)]
em = [percentage_list[i][0] for i in range(18)]

pnb_mean = sum(pnb) / len(pnb)
sw_mean = sum(sw) / len(sw)
pw_mean = sum(pw) / len(pw)
ee_mean = sum(ee) / len(ee)
em_mean = sum(em) / len(em)

pnb = [percentage_list[i][1] for i in range(17)]
sw = [percentage_list[i][2] for i in range(17)]
pw = [percentage_list[i][3] for i in range(17)]
ee = [percentage_list[i][4] for i in range(17)]
em = [percentage_list[i][0] for i in range(17)]

pnb_v = calculate_variance(pnb)
sw_v = calculate_variance(sw)
pw_v = calculate_variance(pw)
ee_v = calculate_variance(ee)
em_v = calculate_variance(em)

print('{:.2f}±{:.2f} & {:.2f}±{:.2f} & {:.2f}±{:.2f} & {:.2f}±{:.2f} & {:.2f}±{:.2f} & {:.2f}'.format(pnb_mean, pnb_v, sw_mean, sw_v, pw_mean, pw_v, ee_mean, ee_v, em_mean, em_v, avg_acc))