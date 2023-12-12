from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
# Create your models here.
class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    editorial = models.CharField(max_length=200)
    ano_de_publicacion = models.IntegerField()
    prestado = models.BooleanField(default=False)
    isbn = models.CharField(max_length=200)

class Usuario(models.Model):
    USER_TYPE_CHOICES = (
        ('ALUMNO', 'Alumno'),
        ('DOCENTE', 'Docente'),
    )
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    correo_electronico = models.EmailField()
    numero_de_telefono = models.CharField(max_length=200)
    user_type = models.CharField(max_length=7, choices=USER_TYPE_CHOICES, default='ALUMNO')
    rut = models.CharField(max_length=20)  

    def clean(self):
        # Valida el formato del RUT
        rut_pattern = r'^\d{1,2}\.\d{3}\.\d{3}[-][0-9kK]{1}$'
        if not re.match(rut_pattern, self.rut):
            raise ValidationError('RUT debe tener el formato XX.XXX.XXX-Y')

class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_prestamo = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    multa_pagada = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.fecha_prestamo:
            self.fecha_prestamo = timezone.now()
        if self.usuario.user_type == 'DOCENTE':
            self.fecha_devolucion = self.fecha_prestamo + timedelta(days=20)
        else:  # ALUMNO
            self.fecha_devolucion = self.fecha_prestamo + timedelta(days=7)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Préstamo {self.id}: {self.libro.titulo} a {self.usuario.nombre}'