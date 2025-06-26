from rest_framework.pagination import PageNumberPagination

class UserScrollPagination(PageNumberPagination):
    page_size = 10       #Number of users to return per scroll
    page_size_query_param = 'page_size'
    max_page_size = 50