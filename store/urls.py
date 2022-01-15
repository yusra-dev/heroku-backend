from django.urls import path
from rest_framework import routers
from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
 # with default router we can see store as an Api root "try /store/ in browser" and we can get the data in json file "try /products.json"
# URLConf
router.register(r'products',views.ProductViewSet,basename="product")# we set base name for those views that we overrided the query set in it and we have more than one page through out this view(product-list)(product-detail)
router.register(r'collections',views.CollectionViewSet)
router.register(r'carts',views.CartViewSet)
router.register(r'customers',views.CustomerViewSet)
router.register(r'orders',views.OrderViewSet,basename="orders")


carts_router=routers.NestedDefaultRouter(router,'carts',lookup='cart')
carts_router.register('items',views.CartItemViewSet,basename='cart-items')
 
urlpatterns=router.urls+carts_router.urls

# using router instead of default implementation for urlpatterns
# urlpatterns = [
#     path('products/', views.ProductList.as_view()),
#     path('products/<int:pk>', views.ProductDetail.as_view()), 
#     path('collections/', views.CollectionList.as_view()),
#     path('collections/<int:pk>/', views.CollectionDetail.as_view(), name='collection-detail'),
# ]
