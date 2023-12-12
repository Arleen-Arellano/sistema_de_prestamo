from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .models import Prestamo, Libro, Usuario
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, date
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
from django.shortcuts import get_object_or_404


# Create your views here.
def home (request):
    return render(request, 'core/home.html')

@login_required
def products(request):
    return render(request, 'core/products.html')   

def exit (request):
    logout(request)
    return redirect('home')

@login_required
def insertarlibro(request):
    if request.method == 'POST':
        titulo = request.POST['titulo']
        autor = request.POST['autor']
        editorial = request.POST['editorial']
        ano_de_publicacion = request.POST['ano_de_publicacion']
        isbn = request.POST['isbn']
        Libro.objects.create(titulo=titulo, autor=autor, editorial=editorial, ano_de_publicacion=ano_de_publicacion, isbn=isbn)
        return HttpResponseRedirect(reverse('products'))
    else:
        return render(request, 'core/insertarlibro.html')

@login_required
def products(request):
    libros = Libro.objects.filter(prestado=False)  # Solo muestra los libros que no están prestados
    return render(request, 'core/products.html', {'libros': libros})


@login_required
def insertar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        direccion = request.POST.get('direccion')
        correo_electronico = request.POST.get('correo_electronico')
        numero_de_telefono = request.POST.get('numero_de_telefono')
        user_type = request.POST.get('user_type')
        rut = request.POST.get('rut')  # Recoge el RUT del formulario

        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            direccion=direccion,
            correo_electronico=correo_electronico,
            numero_de_telefono=numero_de_telefono,
            user_type=user_type,
            rut=rut  # Agrega el RUT aquí
        )
        usuario.full_clean()  # Valida el usuario antes de guardarlo
        usuario.save()

        return redirect('lista_usuarios')

    return render(request, 'core/insertar_usuario.html')

@login_required
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'core/lista_usuarios.html', {'usuarios': usuarios})
@login_required
def insertar_prestamo(request):
    if request.method == 'POST':
        id_del_libro = request.POST.get('id_del_libro')
        id_del_usuario = request.POST.get('id_del_usuario')
        fecha_de_prestamo_str = request.POST.get('fecha_de_prestamo')


        if fecha_de_prestamo_str:
            fecha_de_prestamo = datetime.strptime(fecha_de_prestamo_str, "%Y-%m-%d").date()
        else:
            return render(request, 'core/insertar_prestamo.html', {'error_message': 'Por favor, ingrese una fecha de préstamo.'})

        libro = Libro.objects.get(id=id_del_libro)
        usuario = Usuario.objects.get(id=id_del_usuario)

        if libro.prestado:
            return HttpResponse('Este libro ya está prestado.')

        Prestamo.objects.create(libro=libro, usuario=usuario, fecha_prestamo=fecha_de_prestamo)
        libro.prestado = True
        libro.save()

        return redirect('lista_prestamos')

    else:
        libros = Libro.objects.filter(prestado=False)  # Solo muestra los libros que no están prestados
        usuarios = Usuario.objects.all()
        return render(request, 'core/insertar_prestamo.html', {'libros': libros, 'usuarios': usuarios})

@login_required
def lista_prestamos(request):
    prestamos = Prestamo.objects.all()
    return render(request, 'core/lista_prestamos.html', {'prestamos': prestamos})

@login_required
def prestar_libro(request, libro_id, usuario_id):
    libro = Libro.objects.get(id=libro_id)
    usuario = Usuario.objects.get(id=usuario_id)

    if libro.prestado:
        return HttpResponse('Este libro ya está prestado.')

    Prestamo.objects.create(libro=libro, usuario=usuario)
    libro.prestado = True
    libro.save()

    return redirect('lista_libros')

@login_required
def devolver_libro(request):
    rut = None
    prestamos = Prestamo.objects.none()  # Inicialmente, mostrar una lista vacía

    if request.method == 'POST':
        rut = request.POST.get('rut')
        try:
            usuario = Usuario.objects.get(rut=rut)
            prestamos = Prestamo.objects.filter(usuario=usuario, fecha_devolucion__isnull=True)
        except Usuario.DoesNotExist:
            return HttpResponse('Usuario no encontrado')
        
        # Proceso de devolución
        prestamo_id = request.POST.get('prestamo')
        try:
            prestamo = Prestamo.objects.get(id=prestamo_id)
            if prestamo.fecha_devolucion is not None:
                return HttpResponse('El préstamo seleccionado ya ha sido devuelto.')

            fecha_devolucion = timezone.now()

            # Calcular la multa si hay atraso
            fecha_devuelta = prestamo.fecha_prestamo + timedelta(days=prestamo.dias_prestamo)
            dias_atraso = max(0, (fecha_devolucion.date() - fecha_devuelta).days)
            multa = dias_atraso * 1000  # Multa de $1000 por día de atraso

            prestamo.fecha_devolucion = fecha_devolucion
            prestamo.multa_pagada = multa == 0
            prestamo.multa = multa
            prestamo.save()

            libro = prestamo.libro
            libro.prestado = False
            libro.save()

            # Actualizar el estado del libro
            return redirect('core/lista_prestamos')

        except Prestamo.DoesNotExist:
            return HttpResponse('El préstamo seleccionado no existe.')

    return render(request, 'core/devolver_libro.html', {'rut': rut, 'prestamos': prestamos})

@login_required
def libros_prestados_por_rut(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        try:
            usuario = Usuario.objects.get(rut=rut)
            prestamos = Prestamo.objects.filter(usuario=usuario, fecha_devolucion__isnull=True)
            return render(request, 'core/devolver_libro.html', {'usuario': usuario, 'prestamos': prestamos})
        except Usuario.DoesNotExist:
            return HttpResponse('Usuario no encontrado')
    return render(request, 'core/buscar_por_rut.html')

@login_required
def buscar_prestamos(request):
    if request.method == 'POST':
        rut = request.POST.get('rut')
        prestamos = Prestamo.objects.filter(usuario__rut=rut)
        return render(request, 'core/buscar_prestamos.html', {'rut': rut, 'prestamos': prestamos})
