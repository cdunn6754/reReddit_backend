API_ROOT_URL = 'http://127.0.0.1:8000/'
API_USER_URL = API_ROOT_URL + 'users/'
API_SUB_URL = API_ROOT_URL + 'subreddits/'
API_POST_URL = API_ROOT_URL + 'posts/'
API_COMMENT_URL = API_ROOT_URL + 'comments/'

API_USER_CREATE_URL = API_USER_URL + 'create/'
API_USER_LOGIN_URL = API_USER_URL + 'login/'

API_COMMENT_VOTE_URL = API_COMMENT_URL + 'vote/'



## Functions

# A lot of these functions are based on
# an action (e.g. subscribe, create post) at a particular sub
# url.
API_SUB_BASE_ = lambda args: (API_SUB_URL +
                                       'sub/{}/{}/'.format(args[0],args[1]))
API_SUB_SUBSCRIBE_URL_ = lambda sub: API_SUB_BASE_((sub, "subscribe"))
                                      
