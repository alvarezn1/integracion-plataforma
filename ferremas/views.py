from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto


def inicio(request):
    return render(request, 'ferremas/inicio.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'ferremas/lista_productos.html',{'productos': productos})


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
# Create your views here.
