from rest_framework.pagination import PageNumberPagination


class CustomWithLimitPagination(PageNumberPagination):
    """Custom pagination with limited objects on page
    through 'limit' query parameter."""
    page_size_query_param = 'limit'
