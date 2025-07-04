

from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, ManufacturerViewSet,
    CartViewSet, CartItemViewSet
)
router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('manufacturers', ManufacturerViewSet)
router.register('carts', CartViewSet)
router.register('cart-items', CartItemViewSet)

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('about_me/', views.about_me, name='about_me'),
    path('about_project/', views.about_project, name='about_project'),
    path('spec/', views.spec, name='spec'),
    path('spec/<int:id>/', views.spec_id, name='spec_id'),

    path('catalog/', views.product_list, name='product_list'), 
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'), 
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  
    path('cart/', views.cart_view, name='cart_view'),  
    path('checkout/', views.checkout_view, name='checkout'),
    path('api/', include(router.urls)),
]
