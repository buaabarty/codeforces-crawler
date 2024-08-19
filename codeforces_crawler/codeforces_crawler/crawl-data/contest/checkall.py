import subprocess
import sys
import json
import csv
import ast
import os
from judge import *

def compare_output(output1, output2):
    # 去除行末空格
    output1_lines = [line.rstrip() for line in output1.split('\n')]
    output2_lines = [line.rstrip() for line in output2.split('\n')]

    # 比较行数是否相同
    if len(output1_lines) != len(output2_lines):
        return False

    # 逐行比较
    for line1, line2 in zip(output1_lines, output2_lines):
        if line1 != line2:
            return False

    return True

cnt = 0
tot = 0
ans = {}
with open(sys.argv[1], 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        tot += 1
        code = ast.literal_eval(row['code'])[0]
        ret = judgeByDetails(72254, 1000, 131072, 14, None, code)
        # print('\n\n\n\n', ret)
        if ret['statusCode'] == 6:
            case_id = 0
            for item in ret['extra']:
                if item['statusCode'] == 6:
                    case_id = item['case']
                    break
            for item in ret['extra']:
                if 'stdout&stderr' in item:
                    del item['stdout&stderr']
            if 'diffOutput' in ret:
                # print('hey!!!!')
                del ret['diffOutput']
            cnt += 1
            if cnt >= 120:
                break
            ans[cnt] = {
                'code': code,
                'case_id': case_id,
                'judge_result': ret,
            }
            print(ret)
            print(tot, cnt)
            # break
            # print(ans)
        else:
            print(ret)
            print(code)
            print('fuck')

json.dump(ans, open(sys.argv[1] + '.res.json', 'w'))