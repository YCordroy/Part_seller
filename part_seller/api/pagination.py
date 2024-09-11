from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class TenOnPagePaginator(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'result': data,
        })


class FiveOnPagePaginator(PageNumberPagination):
    page_size = 5

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'result': data,
        })
