from rest_framework.pagination import LimitOffsetPagination
from rest_framework.utils.urls import replace_query_param

class PostListPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100
    
    # def get_next_link(self):
    #     url = super().get_next_link()
    #     return replace_query_param(url, self.limit.qu)
