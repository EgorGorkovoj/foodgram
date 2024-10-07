from requests import Response
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'limit'
    page_query_param = 'page'
    max_page_size = 100


# class SubscribeRecipePagination(PageNumberPagination):
#     page_size = 2
#     page_size_query_param = 'recipes_limit'

#     def get_paginated_response(self, data):
#         return Response({
#             'links': {
#                 'next': self.get_next_link(),
#                 'previous': self.get_previous_link()
#             },
#             'count': self.page.paginator.count,
#             'results': data
#         })
