from .chrome_interface import ChromeInterface


class Request(object):
    def __init__(self,
                 url,
                 method='GET',
                 headers=None,
                 body='',
                 cookies=None,
                 footers=None,
                 user_agent=None,
                 proxy=None,
                 is_completed=None,
                 timeout=None,
                 ):
        pass


class Chrome(object):
    '''
    1. 运行 chromium，可以指定各种参数？
    2. 完成请求
    '''
    def __init__(self):
        pass

    def do(self, request):
        pass
