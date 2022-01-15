from django_filters import rest_framework
from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size=50


# You can add this to setting page and all the views will have pagination 
# REST_FRAMEWORK = {
#     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
# }

    # Method    url                     request         response
    # ------------------------------------------------------------
    # POST      /carts/                 {}              cart
    # GET       /carts/:id              {}              cart
    # DELETE    /carts/:id              {}              {}
    # POST      /carts/:id/items        {prodiId, qty}  item
    # PATCH     /carts/:id/items/:id    {qty }          {qty}
    # DELETE    /carts/:id/items/:id    {}              {}