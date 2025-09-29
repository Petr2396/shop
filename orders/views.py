from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.decorators.http import require_POST 
from catalog.models import Product
from .cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from payments.views import create_payment
from .models import PromoCode


# Корзина
def cart_detail(request):
    cart = Cart(request)
    return render(request, "orders/cart_detail.html", {
        "cart": cart,
        "total_price": cart.get_total_price()
    })


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)

    messages.success(request, f'Товар "{product.name}" добавлен в корзину ✅')
    return redirect(request.META.get("HTTP_REFERER", reverse("catalog:product_list")))


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect("orders:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart.update(product, quantity)
    
    # Возвращаем обновленные данные корзины в JSON
    return JsonResponse({
        'success': True,
        'item_total': cart.get_item_total_price(product),
        'total_price': cart.get_total_price(),
        'quantity': quantity
    })


# orders/views.py
@login_required
def order_create(request):
    cart = Cart(request)
    if request.method == "POST":
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.customer = request.user
            
            # Добавляем информацию о промокоде
            if hasattr(cart, 'promo_code') and cart.promo_code:
                order.promo_code = cart.promo_code.get('code')
                order.discount = cart.promo_code.get('discount', 0)
                order.total_with_discount = cart.get_total_with_discount()
            
            order.save()
            
            for item in cart:
                order.items.create(
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            
            cart.clear()
            # 🔥 сразу редиректим на оплату
            return create_payment(request, order)
    else:
        form = OrderCreateForm()
    
    return render(request, "orders/create.html", {
        "cart": cart, 
        "form": form,
        "total_with_discount": cart.get_total_with_discount(),
        "discount": cart.get_discount()
    })


def order_success(request):
    return render(request, "orders/order_success.html")


# Личный кабинет заказов
@login_required
def my_orders(request):
    # Актуальные заказы (новый, в сборке, отправлен)
    active_orders = (
        Order.objects.filter(customer=request.user)
        .exclude(status__in=["delivered", "canceled"])
        .order_by("-created")  # новые сверху
    )

    # Архивные (доставленные и отмененные)
    archived_orders = (
        Order.objects.filter(customer=request.user, status__in=["delivered", "canceled"])
        .order_by("-created")
    )

    return render(
        request,
        "orders/my_orders.html",
        {"active_orders": active_orders, "archived_orders": archived_orders},
    )


@login_required
def cancel_order(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, customer=request.user)

        if order.status in ["new", "processing"]:
            order.status = "canceled"
            order.save()

    return redirect("orders:my_orders")



def apply_promo_code(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        cart = Cart(request)
        
        success, result = cart.apply_promo_code(code)
        
        if success:
            return JsonResponse({
                'success': True,
                'discount': result.discount,
                'original_total': cart.get_total_price(),  # Добавляем
                'new_total': cart.get_total_with_discount(),
                'message': f'Промокод применен! Скидка {result.discount}%'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def remove_promo_code(request):
    cart = Cart(request)
    cart.remove_promo_code()
    return JsonResponse({
        'success': True,
        'new_total': cart.get_total_price(),
        'message': 'Промокод удален'
    })





