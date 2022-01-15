import collections
from django.db.models import query
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import api_view,action, permission_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.utils import serializer_helpers
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin,DestroyModelMixin, UpdateModelMixin
from core import models
from store.filters import ProductFilter
from store.pagination import DefaultPagination
from store.permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission
from .models import Collection, Customer, Order, Product,Cart,CartItem
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializer, UpdateCartItemSerializer, UpdateOrderSerializer


class ProductViewSet(ModelViewSet):
    queryset= Product.objects.all()
    serializer_class=  ProductSerializer  
    
    #generic filtering for filtering with more than one field by using django filtering framework
  
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class=ProductFilter
    search_fields=['title','description']
    ordering_fields=['unit_price','last_update'] # you can filter even with fields you didin't wrote here
    pagination_class=DefaultPagination
    permission_classes =[IsAdminOrReadOnly]
    
    # def get_queryset(self):  # old way of filtering by filtering one fild only 
    #     queryset= Product.objects.all()
    #     collection_id=self.request.query_params.get('collection_id') # getting colllection id 
    #     if collection_id is not None: # to make sure we have a collection id 
    #         queryset=queryset.filter(collection_id=collection_id)
        
    #     return  queryset
    

    def get_serializer_context(self):
        return {'request': self.request}
    def delete(self,request,pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
   

# The above code is for cretaing both product list and product detail in less code in one class

# class ProductList(ListCreateAPIView):
    
#     queryset = Product.objects.select_related('collection').all()
#     serializer_class=  ProductSerializer 
#     def get_serializer_context(self):
#         return {'request': self.request}

    
    # # the code above is a simpler version of the below code
    # # def get_query_set(self):
    # #     return Product.objects.select_related('collection').all()
    # # def get_serializer_class(self):
    # #     return ProductSerializer     
    # # def get_serializer_context(self):
    # #     return {'request': self.request}  
    
    # # the code above is a simpler version the code below by help of generic views 
    
    # # def get(self,request):
    # #     queryset = Product.objects.select_related('collection').all()
    # #     serializer = ProductSerializer(
    # #         queryset, many=True, context={'request': request})
    # #     return Response(serializer.data)
    # # def post(self,request):
    # #     serializer = ProductSerializer(data=request.data)
    # #     serializer.is_valid(raise_exception=True)
    # #     serializer.save()
    # #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    #   /  

 

# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

    
#     def delete(self,request,pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionViewSet(ModelViewSet):  # we can write (ReadOnlyModelViewSet) so that we just read the data without creating or updating,deleting it it 
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class=  CollectionSerializer    

 
    def delete(self,request,pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.orderitems.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it is associated with a product item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# The above code is for cretaing both collection list and collection detail in less code in one class


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class=  CollectionSerializer 

#     products_count=serializers.IntegerField(read_only=True)    
#     # we don't want to specify the count property while we create a new collection so we use the code above to do so.
    
#     #  if request.method == 'GET':
#     #     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     #     serializer = CollectionSerializer(queryset, many=True)
#     #     return Response(serializer.data)
#     # elif request.method == 'POST':
#     #     serializer = CollectionSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    
    
    
    

# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('products')).all()
#     serializer_class=  CollectionSerializer 

 
#     def delete(self,request,pk):
#         collection = get_object_or_404(Collection, pk=pk)
#         if collection.orderitems.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it is associated with a product item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class CartViewSet(CreateModelMixin,DestroyModelMixin,RetrieveModelMixin, GenericViewSet):
    
    queryset= Cart.objects.prefetch_related('items__product').all()
    serializer_class=CartSerializer
    
    
class CartItemViewSet(ModelViewSet):
    
    http_method_names=['get','post','patch','delete']

    
    def get_serializer_class(self):
        if self.request.method=='POST':
            return AddCartItemSerializer
        elif self.request.method=='PATCH':
            return UpdateCartItemSerializer        
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    def  get_queryset(self):
        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')
                
    
    
class CustomerViewSet(ModelViewSet):
    queryset= Customer.objects.all()
    serializer_class =CustomerSerializer   
    permission_classes = [IsAdminUser]
    
    
    def get_permissions(self): # setting permition for different action in get put or delete 
        
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True,permission_classes=ViewCustomerHistoryPermission)
    def history(self,request,pk):
        return Response('ok')
    
    
    @action(detail=False,methods=['GET','PUT'],permission_classes=IsAuthenticated)
    def me(self,request):
        customer =  Customer.objects.get(user_id=request.user.id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    
class OrderViewSet(ModelViewSet):
    
    http_method_names=['get','patch','delete','head','options']    
    
    def get_permissions(self):
        if self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=request.data,
            context={'user_id':self.request.user.id })
        
        serializer.is_valid(raise_exception=True)
        order=serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    
    
    # Getting the orders of the authenticated customer
    def get_queryset(self):
        user = self.request.user

        
        if user.is_staff:
            return Order.objects.all()
        customer_id=Customer.objects.only('id').get(user_id=user.id) # we can't get customer id in request so we retrive it in customer model
        return Order.objects.filter(customer_id=customer_id)
    
    