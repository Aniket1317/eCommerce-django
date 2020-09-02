from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review, Contact
from django.core.exceptions import ObjectDoesNotExist
import stripe
from django.conf import settings
from django.contrib.auth.models import Group, User
from .forms import SignUpForm, ContactForm, ContactModelForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request, category_slug=None):
	category_page = None
	products = None
	if category_slug!= None:
		category_page = get_object_or_404(Category, slug=category_slug) 
		products = Product.objects.filter(category= category_page, available=True)
	else:
		products = Product.objects.all().filter(available=True)
	return render(request, 'home.html', {'category':category_page, 'products':products})

def product(request, category_slug, product_slug):
	try:
		product = Product.objects.get(category__slug=category_slug, slug=product_slug)
	except Exception as e:
		raise e

	if request.method == 'POST' and request.user.is_authenticated and request.POST['content'].strip() != '':
		Review.objects.create(
				product=product, 
				user=request.user, 
				content=request.POST['content']
			)
	reviews = Review.objects.filter(product=product)
	return render(request, 'product.html', {'product':product, 'reviews':reviews})


def _cart_id_(request):
	cart = request.session.session_key
	if not cart:
		cart = request.session.create()
	return cart

@login_required(redirect_field_name='next',login_url='login')
def add_cart(request, product_id):
	product = Product.objects.get(id= product_id)
	try:
		cart = Cart.objects.get(cart_id=_cart_id_(request))
	except Cart.DoesNotExist:
		cart = Cart.objects.create(cart_id= _cart_id_(request))
		cart.save()
	try:
		cart_item = CartItem.objects.get(product= product, cart=cart)
		if cart_item.quantity < cart_item.product.stock:
			cart_item.quantity += 1
		cart_item.save()
	except CartItem.DoesNotExist:
		cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
		cart_item.save()
	return redirect('cart_detail')

@login_required(redirect_field_name='next',login_url='login')
def remove_cart(request, product_id):
	cart = Cart.objects.get(cart_id=_cart_id_(request))
	product = get_object_or_404(Product, id=product_id)
	cart_item = CartItem.objects.get(cart=cart, product=product)
	if cart_item.quantity > 1:
		cart_item.quantity -=1
		cart_item.save()
	else:
		cart_item.delete()
	return redirect('cart_detail')

@login_required(redirect_field_name='next',login_url='login')
def trash_cart(request, product_id):
	cart = Cart.objects.get(cart_id=_cart_id_(request))
	product = get_object_or_404(Product, id=product_id)
	cart_item = CartItem.objects.get(cart=cart, product=product)
	cart_item.delete()
	return redirect('cart_detail')

@login_required(redirect_field_name='next',login_url='login')
def cart_detail(request, total=0, counter=0, cart_items= None):
	try:
		cart = Cart.objects.get(cart_id= _cart_id_(request))
		cart_items = CartItem.objects.filter(cart=cart, active=True)
		for cart_item in cart_items:
			total += (cart_item.product.price * cart_item.quantity)
			counter += cart_item.quantity
	except ObjectDoesNotExist:
		pass

	stripe.api_key = settings.STRIPE_SECRET_KEY
	stripe_total = int(total * 100)
	description = 'AR-Store - New Order'
	data_key = settings.STRIPE_PUBLISHABLE_KEY
	if request.method == 'POST':
		try:
			token = request.POST['stripeToken']
			email = request.POST['stripeEmail']
			billingName = request.POST['stripeBillingName']
			billingAddress1 = request.POST['stripeBillingAddressLine1']
			billingCity = request.POST['stripeBillingAddressCity']
			billingPostcode = request.POST['stripeBillingAddressZip']
			billingCountry = request.POST['stripeBillingAddressCountryCode']
			shippingName = request.POST['stripeShippingName']
			shippingAddress1 = request.POST['stripeShippingAddressLine1']
			shippingCity = request.POST['stripeShippingAddressCity']
			shippingPostcode = request.POST['stripeShippingAddressZip']
			shippingCountry = request.POST['stripeShippingAddressCountryCode']
			customer = stripe.Customer.create(
					email = email,
					source = token
				)
			charge = stripe.Charge.create(
					amount = stripe_total,
					currency = 'inr',
					description = description,
					customer = customer.id
				)
			# Creating the Order
			try:
				order_details = Order.objects.create(
						token = token,
						total = total, 
						emailAddress = email,
						billingName = billingName,
						billingAddress1 = billingAddress1,
						billingCity = billingCity,
						billingPostcode = billingPostcode,
						billingCountry = billingCountry,
						shippingName = shippingName,
						shippingAddress1 = shippingAddress1,
						shippingCity = shippingCity,
						shippingPostcode = shippingPostcode,
						shippingCountry = shippingCountry
					)
				order_details.save()
				for order_item in cart_items:
					or_item = OrderItem.objects.create(
							product = order_item.product.name,
							quantity = order_item.quantity,
							price = order_item.product.price,
							order = order_details
						)
					or_item.save()

					#reduce stock in db
					products = Product.objects.get(id=order_item.product.id)
					products.stock = int(order_item.product.stock - order_item.quantity)
					products.save()
					order_item.delete()

				return redirect('thanks_page', order_details.id)
			except ObjectDoesNotExist:
				pass

		except stripe.error.CardError as e:
			return False,e

	return render(request, 'cart.html', dict(cart_items= cart_items, total=total, counter=counter, 
				data_key=data_key, stripe_total=stripe_total, description=description) )

@login_required(redirect_field_name='next',login_url='login')
def thanks_page(request, order_id):
	if order_id:
		customer_order = get_object_or_404(Order, id=order_id)  
	return render(request, 'thanks_page.html', {'customer_order':customer_order})

def signupView(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			signup_user = User.objects.get(username=username)
			customer_group = Group.objects.get(name='Customers')
			customer_group.user_set.add(signup_user)
			return redirect('login')
	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form':form})

def loginView(request):
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request,user)
				return redirect('home')
			else:
				return redirect('signup')
	else:
		form = AuthenticationForm()
	return render(request, 'login.html', {'form':form})

def logoutView(request):
	logout(request)
	return redirect('login')

@login_required(redirect_field_name='next',login_url='login')
def orderHistory(request):
	if request.user.is_authenticated:
		email = str(request.user.email)
		order_details = Order.objects.filter(emailAddress=email)
	return render(request, 'orderlist.html', {'order_details':order_details})

@login_required(redirect_field_name='next',login_url='login')
def orderDetail(request, order_id):
	if request.user.is_authenticated:
		email = str(request.user.email)
		order = Order.objects.get(id=order_id, emailAddress=email)
		order_items = OrderItem.objects.filter(order=order)
	return render(request, 'order_details.html', {'order':order,'order_items':order_items})

def search(request):
	products = Product.objects.filter(name__contains=request.GET['name'])
	return render(request, 'home.html', {'products':products})


@login_required(redirect_field_name='next',login_url='login')
def thanks_contact(request):
	return render(request, 'thanks_contact.html')

@login_required(redirect_field_name='next',login_url='login')
def contact(request):
	form = ContactModelForm(request.POST or None)
	if form.is_valid():
		# obj = MyBlog.objects.create(**form.cleaned_data)
		obj = form.save(commit=False)
		obj.user = request.user
		obj.save()
		form = ContactModelForm()
		return redirect('thanks')
	return render(request, 'contact.html', {'form':form})

