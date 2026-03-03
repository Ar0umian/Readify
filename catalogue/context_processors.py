# books/context_processors.py
from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        # جلب السلة وحساب مجموع كميات الكتب بداخلها
        cart, created = Cart.objects.get_or_create(user=request.user)
        count = sum(item.quantity for item in cart.items.all())
        return {'cart_count': count}
    return {'cart_count': 0}

