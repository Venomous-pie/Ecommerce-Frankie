from orders.models import Cart
from users.models import Wishlist

def navbar_counts(request):
    wishlist_count = 0
    cart_count = 0

    if request.user.is_authenticated:
        print("NAVBAR CONTEXT PROCESSOR CALLED")
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        wishlist_count = wishlist.products.count()

        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()

    print(f"wishlist_count={wishlist_count}, cart_count={cart_count}")
    return {
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }
