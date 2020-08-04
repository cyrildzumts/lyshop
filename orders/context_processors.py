from orders.models import Order

def order_context(request):
    if request.user.is_authenticated :
        qs = Order.objects.filter(user=request.user).order_by('-created_at')
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:3]
    else :
        qs = Order.objects.none()
        recent_orders = qs
    context = {
        'recent_orders': recent_orders,
        'order_list': qs
    }
    return context