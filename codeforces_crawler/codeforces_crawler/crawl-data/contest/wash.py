import json
import sys

d = json.load(open(sys.argv[1], 'r'))

for item in d:
    if 'diffOutput' in d[item]['judge_result']:
        del d[item]['judge_result']['diffOutput']
    for its in d[item]['judge_result']['extra']:
        if 'stdout&stderr' in its:
            del its['stdout&stderr']

json.dump(d, open(sys.argv[2], 'w'))
