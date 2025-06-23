from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.views import LoginView

from .models import Producto
from .forms import CustomUserCreationForm

from .models import Producto
from .forms import StockUpdateForm

import uuid
import mercadopago
from django.conf import settings

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from django.shortcuts import render, redirect


import requests
from .decorators import group_required

API_KEY = '70b1ae962c7551b79305d5a6'





class CustomLoginView(LoginView):
    template_name = 'ferremas/login.html'


def inicio(request):
    user = request.user
    es_bodeguero = user.groups.filter(name="Bodeguero").exists() if user.is_authenticated else False
    es_contador = user.groups.filter(name="Contador").exists() if user.is_authenticated else False
    return render(request, 'ferremas/inicio.html', {
        'es_bodeguero': es_bodeguero,
        'es_contador': es_contador,
    })

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

@login_required
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

    # Aquí defines la tasa de cambio (puedes actualizarla o sacar de API)
    tasa_cambio = 938  # Ejemplo: 800 CLP = 1 USD
    total_usd = round(total / tasa_cambio, 2) if total else 0

    return render(request, 'ferremas/carrito.html', {'productos': productos, 'total': total, 'total_usd': total_usd})


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



def tasa_cambio(request):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
    response = requests.get(url)
    data = response.json()

    # Obtener CLP por ejemplo
    tasa_clp = data['conversion_rates'].get('CLP', None)

    return JsonResponse({
        'base': 'USD',
        'CLP': tasa_clp
    })




def es_bodeguero(user):
    return user.groups.filter(name='Bodeguero').exists()
@group_required("Bodeguero")
@user_passes_test(es_bodeguero)
def gestionar_stock(request):
    productos = Producto.objects.all()
    if request.method == 'POST':
        for producto in productos:
            nuevo_stock = request.POST.get(f'stock_{producto.id}')
            if nuevo_stock is not None:
                producto.stock = int(nuevo_stock)
                producto.save()
        return redirect('gestionar_stock')
    
    return render(request, 'ferremas/gestionar_stock.html', {'productos': productos})


def es_contador(user):
    return user.groups.filter(name='Contador').exists()

@group_required("Contador")
def transacciones_contador(request):
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # Obtener las últimas 10 transacciones (puedes ajustar el límite)
    result = sdk.payment().search({"limit": 10, "sort": "date_created", "criteria": "desc"})

    pagos = result["response"]["results"]

    return render(request, 'ferremas/transacciones_contador.html', {'pagos': pagos})