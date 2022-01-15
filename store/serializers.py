from decimal import Decimal
from django.db import models
from django.db import transaction
from django.db.models import fields
from store.models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection
from rest_framework import serializers


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title' ]

 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


#Serializer for getting critcal information about the products
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']

 
class CartItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields=['id','title','unit_price']

   



class CartItemSerializer(serializers.ModelSerializer):
    product=CartItemProductSerializer() 
    
    #SerializerMethodField bo awaya valuy naw returni functionek
    # bkaina naw aw variablay ka ta3rifman krdwa, bas abe aw functionay
    # ka valuy le waragry awha nawy bney (get_nawyvariablaka) bo away 
    # retunakay bbe ba value bo variablaka
    
    total_price=serializers.SerializerMethodField()
    
    def get_total_price(self,cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price
    
    class Meta:
        model = CartItem
        fields=['id','product','quantity','total_price']

   

class CartSerializer(serializers.ModelSerializer):
    id=serializers.UUIDField(read_only=True) # we don't want to send id for saving
    items=CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self,cart):
       return  sum([item.quantity * item.product.unit_price for item in cart.items.all() ])
    class Meta:
        model = Cart
        fields=['id','items','total_price']

   
class AddCartItemSerializer(serializers.ModelSerializer):
    
    
    product_id= serializers.IntegerField()
     
    class Meta:
        model=CartItem
        fields=['id', 'product_id','quantity']
        
    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given id')
        return value
        
    
    def save(self,**kwarg):
        cart_id=self.context['cart_id']
        product_id=self.validated_data['product_id']
        quantity=self.validated_data['quantity']
        
        try:
            # Updating an existing item
            cart_item=CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            # Creating new item
            CartItem.objects.create(cart_id=cart_id,**self.validated_data)
        
        return self.instance
    
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    
      class Meta:
        model=CartItem
        fields=['quantity']
     
     
class CustomerSerializer(serializers.ModelSerializer):
    
    user_id= serializers.IntegerField()
    
    class Meta():
        model = Customer
        fields = ['id','user_id','phone','birth_date','membership']
        

class OrderItemSerializer(serializers.ModelSerializer):
        
        product = SimpleProductSerializer()
        
        class Meta():
            model = OrderItem
            fields = ['id','product','unit_price','quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta():
        model = Order
        fields = ['id','customer','items','placed_at','payment_status']
        
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields= ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id=serializers.UUIDField()
    
    def validate_cart_id(self,cart_id):
        if not Cart.objects.filter(pk=cart_id).exists(): #wrong cart id 
            raise serializers.ValidationError('No cart with the given id was found')
        if CartItem.objects.filter(cart_id=cart_id).count()==0:
            raise serializers.ValidationError("You can't add an empty card")
        return cart_id
    
    
     
    def save(self, **kwargs):
        with transaction.atomic(): # excuting the code bellow all or non 
                    
            cart_id=self.validated_data['cart_id']
            
            customer=Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            
            cart_items=CartItem.objects\
                                .select_related('product') \
                                .filter(cart_id=cart_id)
            
            order_items= [
                OrderItem(
                     order=order,
                     product=item.product,
                     unit_price=item.product.unit_price,
                     quantity=item.quantity
                ) for item in cart_items
            ]
            
            OrderItem.objects.bulk_create(order_items)
            
            Cart.objects.filter(pk=cart_id).delete() # deleting item in cart
            
            return order
        


