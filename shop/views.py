from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.db.models import Avg
from django.contrib.auth.models import User
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Cart, Order,Wishlist, Review, Profile
from django.db.models import Q
from django.template.loader import get_template
from django.http import HttpResponse
# pyrefly: ignore [missing-import]
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from io import BytesIO
from django.contrib import messages

def home(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    products = Product.objects.all()

    if query:
        products = products.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__icontains=query)
        )

    if category:
        products = products.filter(category__icontains=category)
    for product in products:
        product.avg_rating = Review.objects.filter(product=product).aggregate(Avg('rating'))['rating__avg']

    return render(request, "home.html", {
        "products": products,
        "query": query,
        "category": category
    })
    

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, "product_detail.html", {
        "product": product
    })

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('/cart/')

def cart(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    cart_items = Cart.objects.filter(user=request.user)
    total_price = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })
    
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if password != confirm_password:
            return render(request, "register.html", {
                "error": "Passwords do not match"
            })

        otp = random.randint(100000, 999999)

        request.session["register_username"] = username
        request.session["register_email"] = email
        request.session["register_phone"] = phone
        request.session["register_password"] = password
        request.session["register_otp"] = str(otp)

        send_mail(
            "Your Registration OTP",
            f"Your OTP is {otp}",
            "noreply@myshop.com",
            [email],
            fail_silently=False,
        )

        return redirect('/verify-otp/')

    return render(request, "register.html")



def remove_from_cart(request, cart_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    item.delete()

    return redirect('/cart/')


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {
        "form": form
    })


def verify_otp(request):
    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        saved_otp = request.session.get("register_otp")

        if entered_otp == saved_otp:

            user = User.objects.create_user(
                username=request.session.get("register_username"),
                email=request.session.get("register_email"),
                password=request.session.get("register_password")
            )

            Profile.objects.create(
                user=user,
                phone=request.session.get("register_phone")
            )

            login(request, user)

            return redirect('/login/')

        return render(request, "verify_otp.html", {
            "error": "Invalid OTP"
        })

    return render(request, "verify_otp.html")

def user_logout(request):
    logout(request)
    return redirect('/')



def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    reviews = Review.objects.filter(product=product)

    average_rating = reviews.aggregate(
        Avg('rating')
    )['rating__avg']

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('/login/')

        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

        return redirect(f'/product/{product.id}/')

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews,
        "average_rating": average_rating
    })


def increase_quantity(request, cart_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    item = get_object_or_404(Cart, id=cart_id, user=request.user)
    item.quantity += 1
    item.save()

    return redirect('/cart/')


def decrease_quantity(request, cart_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    item = get_object_or_404(Cart, id=cart_id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('/cart/')

def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    orders = Order.objects.filter(user=request.user).order_by('-id')

    return render(request, "my_orders.html", {
        "orders": orders
    })


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    cart_items = Cart.objects.filter(user=request.user)
    total_price = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


def place_order(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        phone = request.POST.get("phone")

        cart_items = Cart.objects.filter(user=request.user)
        total_price = 0

        for item in cart_items:
            total_price += item.product.price * item.quantity

        Order.objects.create(
            user=request.user,
            customer_name=name,
            address=address,
            phone=phone,
            total_price=total_price
        )

        cart_items.delete()

        return redirect('/my-orders/')

    return redirect('/checkout/')


def my_orders(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    orders = Order.objects.filter(user=request.user).order_by('-id')

    return render(request, "my_orders.html", {
        "orders": orders
    })


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect('/')


def my_wishlist(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    wishlist_items = Wishlist.objects.filter(user=request.user)

    return render(request, "my_wishlist.html", {
        "wishlist_items": wishlist_items
    })


def payment(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        pincode = request.POST.get("pincode")

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Please enter a valid 10-digit phone number")
            return redirect('/checkout/')

        if len(address) < 10:
            messages.error(request, "Please enter a valid address")
            return redirect('/checkout/')

        if not city.replace(" ", "").isalpha():
            messages.error(request, "Please enter a valid city name")
            return redirect('/checkout/')

        if not state.replace(" ", "").isalpha():
            messages.error(request, "Please enter a valid state name")
            return redirect('/checkout/')

        if not pincode.isdigit() or len(pincode) != 6:
            messages.error(request, "Please enter a valid 6-digit pincode")
            return redirect('/checkout/')

        if not name.replace(" ", "").isalpha():
           messages.error(request, "Please enter a valid name")
           return redirect('/checkout/')

        request.session["checkout_name"] = name
        request.session["checkout_email"] = email
        request.session["checkout_phone"] = phone
        request.session["checkout_address"] = address
        request.session["checkout_city"] = city
        request.session["checkout_state"] = state
        request.session["checkout_pincode"] = pincode

    cart_items = Cart.objects.filter(user=request.user)
    total_price = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity

    return render(request, "payment.html", {
        "total_price": total_price
    })


def payment_success(request, payment_method):
    if not request.user.is_authenticated:
        return redirect('/login/')

    cart_items = Cart.objects.filter(user=request.user)
    total_price = 0

    for item in cart_items:
        total_price += item.product.price * item.quantity

    if total_price == 0:
      return redirect('/cart/')

    order = Order.objects.create(
        user=request.user,
        customer_name=request.session.get("checkout_name"),
        address=request.session.get("checkout_address"),
        phone=request.session.get("checkout_phone"),
        total_price=total_price,
        payment_method=payment_method
    )

    customer_email = request.session.get("checkout_email")

    if customer_email:
        customer_email = request.session.get("checkout_email")

    if customer_email:
       template = get_template("invoice_pdf.html")
       html = template.render({"order": order})

    pdf_file = BytesIO()
    pisa.CreatePDF(html, dest=pdf_file)

    email = EmailMessage(
        "Your MyShop Invoice PDF",
        "Thank you for your order. Please find your invoice attached.",
        settings.EMAIL_HOST_USER,
        [customer_email],
    )

    email.attach(
        f"invoice_{order.id}.pdf",
        pdf_file.getvalue(),
        "application/pdf"
    )

    email.send()

    cart_items.delete()

    return redirect(f'/invoice/{order.id}/')

def remove_from_wishlist(request, wishlist_id):
    if not request.user.is_authenticated:
        return redirect('/login/')

    item = get_object_or_404(Wishlist, id=wishlist_id, user=request.user)

    item.delete()

    return redirect('/my-wishlist/')


def invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, "invoice.html", {
        "order": order
    })


def profile(request):
    if not request.user.is_authenticated:
        return redirect('/login/')

    total_orders = Order.objects.filter(user=request.user).count()
    total_cart = Cart.objects.filter(user=request.user).count()
    total_wishlist = Wishlist.objects.filter(user=request.user).count()

    return render(request, "profile.html", {
        "total_orders": total_orders,
        "total_cart": total_cart,
        "total_wishlist": total_wishlist
    })
