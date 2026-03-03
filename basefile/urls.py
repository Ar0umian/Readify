"""
URL configuration for basefile project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from catalogue import views as catalogue_views
from accounts import views as accounts_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', catalogue_views.index, name='index'),
    path('book/<int:book_id>/', catalogue_views.book_detail, name='book_detail'),
    path('register/', accounts_views.register, name='register'),

    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', accounts_views.profile_view, name='profile'),
    path('edit_profile/', accounts_views.edit_profile, name='edit_profile'),
    path('change_password' , accounts_views.change_password, name='change_password'),
    path('cart/', catalogue_views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:book_id>/', catalogue_views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', catalogue_views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', catalogue_views.checkout, name='checkout'),
    path('invoice/<int:order_id>/', catalogue_views.order_invoice, name='order_invoice'),
    path('delete-account/', accounts_views.delete_user, name='delete_user'),
    path('all-books/', catalogue_views.all_books, name='all_books'),
    path('random-book/', catalogue_views.random_book_redirect, name='random_book'),
    path('delete-order/<int:order_id>/', catalogue_views.delete_order, name='delete_order'),

]