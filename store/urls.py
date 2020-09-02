from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('category/<slug:category_slug>/', views.home, name="products_category"),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product, name="product_detail"),
    path('cart/add/<int:product_id>/', views.add_cart, name="add_cart"),
    path('cart/decrement/<int:product_id>/', views.remove_cart, name="remove_cart"),
    path('cart/remove/<int:product_id>/', views.trash_cart, name="trash_cart"),
    path('cart/', views.cart_detail, name="cart_detail"),
    path('thankyou/<int:order_id>/', views.thanks_page, name="thanks_page"),
    path('account/signup/', views.signupView, name="signup"),
    path('account/login/', views.loginView, name="login"),
    path('account/logout/', views.logoutView, name="logout"),
    path('order_history/', views.orderHistory, name="order_history"),
    path('order_details/<int:order_id>', views.orderDetail, name="order_details"),
    path('search/', views.search, name="search"),
    path('contact/', views.contact, name="contact"),
    path('contact/thanks/', views.thanks_contact, name="thanks"),
]
