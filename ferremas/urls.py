from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, register
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('lista_productos/', views.lista_productos, name='productos'),
    path('agregar_carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar_carrito/<int:producto_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='inicio'), name='logout'),
    path('register/', register, name='register'),
    path('crear-preferencia/', views.crear_preferencia, name='crear_preferencia'),
    path('gracias/', views.gracias, name='gracias'),
    path('error/', views.error, name='error'),
    path('pendiente/', views.pendiente, name='pendiente'),
    path('tasa-cambio/', views.tasa_cambio, name='tasa_cambio'),
    path('bodega/stock/', views.gestionar_stock, name='gestionar_stock'),
    path('contador/transacciones/', views.transacciones_contador, name='transacciones_contador'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    
    

]
