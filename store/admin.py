from django.contrib import admin
from . import models
from django.db.models import Count
from django.utils.html import format_html,urlencode
from django.urls import reverse
# Register your models here.
 
@admin.register(models.Collection)
class CollectionAdmin (admin.ModelAdmin): 
    list_display= ['title','products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url =(
            reverse('admin:store_product_changelist') 
            + '?'
            + urlencode({
                'collection__id':str(collection.id)
            }))
        return format_html('<a href="{}">{}</a>',url, collection.products_count)
        
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )


 
@admin.register(models.Product)
class ProductAdmin (admin.ModelAdmin):
    list_display=['title','unit_price','inventory_status'
                  ,'collection_title']
    list_editable=['unit_price']
    list_per_page=10
    list_filter=['collection','last_update']
    search_fields = ['title']


    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory <10:
            return 'LOW'
        return 'OK'
    def collection_title(self,product):
        return product.collection.title

@admin.register(models.Customer)
class CustomerAdmin (admin.ModelAdmin):
    list_display=['first_name','last_name','membership']
    list_editable=['membership']
    list_per_page=10
    list_select_related=['user'] #if we didn't egerload customer with user by this, a separate query will send to database for each customer 
    ordering=['user__first_name','user__last_name']
    search_fields=['first_name__istartswith','last_name__istartswith'] # i is for insensitive
 
 
class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']
