import requests
import time
import uuid

def postJudgeByDetails(nanti_id, time_limit, memory_limit, total_case, file_name, code, show_detail='0'):
    identifier = str(uuid.uuid4())
    ret = requests.post('http://ingress.jsktesting.com/suani/judge/submit', timeout=5, data={
        'identifier': identifier,
        'code': code,
        'language': 'c++',
        'timeLimit': time_limit,
        'uid': 1,
        'problemId': nanti_id,
        'judgeType': 'default',
        'testAll': True,
        'memoryLimit': memory_limit,
        'statusId': 100000,
        'testAll': '1',
        'case': total_case,
        'diffLevel': 1,
        'fileName': file_name,
        'showDetail': show_detail,
    })
    return identifier, ret.status_code == 200

def postJudge(nanti, code):
    identifier = str(uuid.uuid4())
    ret = requests.post('http://ingress.jsktesting.com/suani/judge/submit', timeout=5, data={
        'identifier': identifier,
        'code': code,
        'language': 'c++',
        'timeLimit': nanti[6],
        'uid': 1,
        'problemId': nanti[0],
        'judgeType': 'default',
        'testAll': True,
        'memoryLimit': nanti[7],
        'statusId': 100000,
        'testAll': '1',
        'case': nanti[23],
        'diffLevel': 1,
        'fileName': nanti[28],
        'showDetail': '0',
    })
    return identifier, ret.status_code == 200

def getJudgeStatus(identifier):
    response = requests.get('http://ingress.jsktesting.com/suani/judge/' + identifier, timeout=5)
    response_data = response.json()
    if response_data['status'] != 'finished':
        return {
            'status': response_data['status'],
        }
    if 'detail' not in response_data:
        return {
            'status': 'running',
        }
    details = response_data['detail']
    case_cnt = 0
    pass_cnt = 0
    for item in details:
        case_cnt += 1
        pass_cnt += item['statusCode'] == 4
    # print(response_data)
    return {
        'status': response_data['status'],
        'statusCode': response_data['statusCode'],
        'total': case_cnt,
        'passed': pass_cnt,
        'compileLog': response_data['message'],
        'compileJson': response_data.get('compileJson', ''),
        'compileErrorLog' : response_data.get('message', ''),
        'time': response_data['time'],
        'memory': response_data['memory'],
        'extra': response_data['detail'],
        'diffOutput': response_data['diffOutput'],
    }

def judge(nanti, code):
    identifier, _ = postJudge(nanti, code)
    ret = getJudgeStatus(identifier)
    cnt = 0
    while ret['status'] != 'finished':
        print(ret['status'], flush=True)
        time.sleep(1)
        ret = getJudgeStatus(identifier)
        cnt += 1
        if cnt > 60:
            return None
    return ret

def judgeByDetails(nanti_id, time_limit, memory_limit, total_case, file_name, code, show_detail=False):
    show_detail_flag = '1' if show_detail else '0'
    identifier, _ = postJudgeByDetails(nanti_id, time_limit, memory_limit, total_case, file_name, code, show_detail_flag)
    print(identifier, flush=True)
    ret = getJudgeStatus(identifier)
    cnt = 0
    while ret['status'] != 'finished':
        print(ret['status'], flush=True)
        time.sleep(1)
        ret = getJudgeStatus(identifier)
        cnt += 1
        if cnt > 60:
            return None
    return ret

def format_extra(ret, case_cnt):
    extra = {}
    times = []
    statuses = []
    memory = []
    for item in ret['extra']:
        times.append(item['runTime'])
        statuses.append(item['statusCode'])
        memory.append(item['memory'])
    extra = {'testcase': {'total': case_cnt, 'passed': ret['passed']},
             'time': times, 'statuses': statuses, 'memory': memory}
    if 'debug_info' in ret:
        extra['debug_info'] = ret['debug_info']
    return extra
