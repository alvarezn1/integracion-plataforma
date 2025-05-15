from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('lista_productos/',views.lista_productos,name='productos'),
    path('agregar_carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar_carrito/<int:producto_id>/', views.eliminar_carrito, name='eliminar_carrito'),

    
]
