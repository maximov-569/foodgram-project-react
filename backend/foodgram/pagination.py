from rest_framework.pagination import PageNumberPagination


class CustomWithLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
