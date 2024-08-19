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
with open(sys.argv[1], 'r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        tot += 1
        code = ast.literal_eval(row['code'])[0]
        retry_cnt = 0
        while True:
            retry_cnt += 1
            with open('solution.cpp', 'w') as code_file:
                code_file.write(code)

            # 编译代码
            compile_command = '/usr/local/bin/g++-13 -o solution solution.cpp'
            subprocess.run(compile_command, shell=True, check=True)

            # 生成随机数据
            n = 500
            min_weight = 100000
            max_weight = 100000
            generate_command = f'python3 295.py {n} {min_weight} {max_weight} > input.txt'
            subprocess.run(generate_command, shell=True, check=True)

            # 运行代码，获取输出结果
            run_command = './solution < input.txt > output.txt'
            subprocess.run(run_command, shell=True, check=True)

            # 读取代码输出结果
            with open('output.txt', 'r') as output_file:
                code_output = output_file.read().strip()

            # 运行标准程序，获取输出结果
            standard_command = './295 < input.txt > standard_output.txt'
            subprocess.run(standard_command, shell=True, check=True)
        
            # 读取标准输出结果
            with open('standard_output.txt', 'r') as standard_output_file:
                standard_output = standard_output_file.read().strip()

            # 比较两个输出结果
            if compare_output(code_output, standard_output):
                print(f"Test case {tot}: Passed")
            else:
                print('done~')
                sys.exit(0)