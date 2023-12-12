"""
URL configuration for login project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from django.contrib.auth.views import LoginView
from .views import home, products, exit, insertarlibro, insertar_usuario, lista_usuarios, insertar_prestamo,lista_prestamos, devolver_libro, prestar_libro,libros_prestados_por_rut,buscar_prestamos
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('logout/', exit, name='exit'),
    path('insertarlibro/', views.insertarlibro, name='insertarlibro'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('insertarusuario/', insertar_usuario, name='insertar_usuario'),
    path('listausuarios/', lista_usuarios, name='lista_usuarios'),
    path('insertarprestamo/', insertar_prestamo, name='insertar_prestamo'),
    path('listaprestamos/', lista_prestamos, name='lista_prestamos'),
    path('prestar_libro/<int:libro_id>/<int:usuario_id>/', views.prestar_libro, name='prestar_libro'),
    path('libros_prestados_por_rut/', libros_prestados_por_rut, name='libros_prestados_por_rut'),
    path('buscar_prestamos/', buscar_prestamos, name='buscar_prestamos'),
    path('devolver_libro/', devolver_libro, name='devolver_libro'),
]
