from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.views import LoginView

from .models import Producto
from .forms import CustomUserCreationForm

from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType

import uuid


# Opciones para la integración Transbank Webpay Plus
TRANSACTION_OPTIONS = {
    "commerce_code": "597055555532",
    "api_key": "XNNF6A0fJ1N8FTvVJH8z8jZ2mI6R0s4e",
    "integration_type": IntegrationType.TEST
}


class CustomLoginView(LoginView):
    template_name = 'ferremas/login.html'


def inicio(request):
    return render(request, 'ferremas/inicio.html')


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'ferremas/lista_productos.html', {'productos': productos})


def login_view(request):
    return render(request, 'ferremas/login.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('inicio')
    else:
        form = CustomUserCreationForm()
    return render(request, 'ferremas/register.html', {'form': form})


def agregar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito[str(producto_id)] = carrito.get(str(producto_id), 0) + 1
    request.session['carrito'] = carrito
    return redirect('productos')


def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos = []
    total = 0

    for id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, pk=id)
        producto.cantidad = cantidad
        producto.subtotal = cantidad * producto.precio
        total += producto.subtotal
        productos.append(producto)

    return render(request, 'ferremas/carrito.html', {'productos': productos, 'total': total})


def eliminar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
    request.session['carrito'] = carrito
    return redirect('ver_carrito')


