from orders.models import Order

def order_context(request):

    context = {
        'recent_orders': Order.objects.filter(user=request.user)[:3],
        'order_list': Order.objects.filter(user=request.user)
    }
    return context