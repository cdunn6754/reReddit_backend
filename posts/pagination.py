from rest_framework.pagination import LimitOffsetPagination

class PostPagination(LimitOffsetPagination):
    default_limit = 15
    max_limit = 100
