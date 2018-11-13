API_ROOT_URL = 'http://127.0.0.1:8000/'
API_USER_URL = API_ROOT_URL + 'users/'
API_SUB_URL = API_ROOT_URL + 'subreddits/'

API_USER_CREATE_URL = API_USER_URL + 'create/'
API_USER_LOGIN_URL = API_USER_URL + 'login/'

API_SUB_SUBSCRIBE_URL_ = lambda sub: (API_SUB_URL +
                                      'sub/{}/subscribe/'.format(sub))
