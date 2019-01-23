import json

dumps = json.dumps


def loads(data, *a, **kwargs):
    print('*'*30)
    print(data)
    # print(type(data))
    # if isinstance(data, str):
    #     return json.loads(data, *a, **kwargs)
    #
    # try:
    #     data = data.encode('gbk')
    #     return json.loads(data, encoding='gbk', *a, **kwargs)
    # except UnicodeDecodeError:
    #     data = data.decode('utf-8')
    # print(type(data))
    t = json.loads(data, *a, **kwargs)
    # print(t)
    # if isinstance(t, dict) and 'id' in t and t['id'] == 9:
    #     print('before decode.')
    #     data = data.decode('gb18030')#.encode('utf-8')
    #     # data = data.encode('gb18030', 'ignore').decode('utf-8', 'ignore')
    #     print('after decode. ', data)
    #     return json.loads(data, encoding='gb18030', *a, **kwargs)

    return t