from django.shortcuts import render
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Count, Max, Min, Avg, Sum, Func, Value, ExpressionWrapper, DecimalField
from store.models import Product, Customer, Collection, Order, OrderItem, Cart, CartItem
from django.contrib.contenttypes.models import ContentType
from tags.models import TaggedItem

def say_hello(request):
    customer_query_set = Customer.objects.filter(email__icontains='.com')
    collection_query_set = Collection.objects.filter(featured_product__isnull=True)
    product_query_set = Product.objects.filter(inventory=F('unit_price'))
    order_query_set = Order.objects.filter(customer__id=1)
    order_item_query_set = OrderItem.objects.filter(product__collection__id=3)

    ordered_products = OrderItem.objects.values('product__id', 'product__title').distinct().order_by('product__title')
    # ordered_products = Product.objects.filter(
    #     id__in=OrderItem.objects.values('product__id').distinct()
    # ).order_by('title')
    last_five_prod = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[:5]
    total_orders = Order.objects.aggregate(total_count=Count('id'))
    total_units_sold = OrderItem.objects.filter(product__id=1).aggregate(total_units_sold=Sum('quantity'))
    total_orders_by_customer1 = Order.objects.filter(customer__id=1).aggregate(total_count=Count('id'))
    result = Product.objects.filter(collection__id=3).aggregate(max_price=Max('unit_price'), min_price=Min('unit_price'), avg_price=Avg('unit_price'))
    concat = Customer.objects.annotate(
        full_name=Func(F('first_name'), Value(" "), F('last_name'), function='CONCAT')
    )
    last_order = Customer.objects.annotate(
        last_order=Max('order__id')
    )

    collection_product_count = Collection.objects.annotate(
        products_count=Count('product')
    )

    customers_with_more_than_5 = Customer.objects.annotate(
        orders_count=Count('order')
    ).filter(orders_count__gt=5)

    customers_total_amount = Customer.objects.annotate(
        total_amount=Sum('order__orderitem__product__unit_price')
    )

    top_5_best_selling = Product.objects.annotate(
        total_sum=Sum(ExpressionWrapper((F'orderitem__quantity') * F('orderitem__unit_price'), output_field=DecimalField())
    )).order_by('total_sum')[:5]

    tag_query_set = TaggedItem.objects.get_tags_for(Product,1)

    # insert/update object
    # collection = Collection()
    # collection.title = 'Video Games'
    # collection.featured_product = Product(pk=1)
    # collection.save()
    # or use Collection.objects.create() for insert
    # Collection.objects.update for update without read first
    with transaction.atomic():
        order = Order()
        order.customer_id = 1

    return render(request, 'hello.html', {'name': 'Smith', 'products': list(tag_query_set)})
