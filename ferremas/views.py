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
import mercadopago
from django.conf import settings

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from django.shortcuts import render, redirect







class CustomLoginView(LoginView):
    template_name = 'ferremas/login.html'


def inicio(request):
    return render(request, 'ferremas/inicio.html')


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'ferremas/lista_productos.html', {'productos': productos})


def login_view(request):
    print(settings.MERCADO_PAGO_ACCESS_TOKEN)
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

def gracias(request):
    return render(request, 'ferremas/gracias.html')

def error(request):
    return render(request, 'ferremas/error.html')

def pendiente(request):
    return render(request, 'ferremas/pendiente.html')


def pago_view(request):
    return render(request, 'ferremas/pago.html')

def crear_preferencia(request):
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    carrito = request.session.get('carrito', {})
    items_mp = []

    for prod_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, pk=prod_id)
        items_mp.append({
            "title": f"{producto.nombre} (ID: {producto.id})",  # título único
            "quantity": cantidad,
            "unit_price": float(producto.precio),
            "currency_id": "CLP"
        })

    if not items_mp:
        return JsonResponse({"error": "El carrito está vacío"}, status=400)

    preference_data = {
        "items": items_mp,
        "back_urls": {
            "success": "https://2b4f-201-241-4-239.ngrok-free.app/gracias/",
            "failure": "https://2b4f-201-241-4-239.ngrok-free.app/error/",
            "pending": "https://2b4f-201-241-4-239.ngrok-free.app/pendiente/"
        },
        "auto_return": "approved",
        "payer": {
            "email": "test_user_1492597836@testuser.com"
        }
    }

   

    preference_response = sdk.preference().create(preference_data)
    preference = preference_response.get("response", {})

    if 'id' not in preference:
        return JsonResponse({"error": "No se encontró 'id' en la respuesta de preferencia"}, status=500)

    return JsonResponse({"id": preference["id"]})
