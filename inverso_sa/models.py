# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    codigo_invitacion = models.CharField(max_length=20, unique=True, blank=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.codigo_invitacion:
            import random
            self.codigo_invitacion = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)


# inverso_sa/models.py (continúa)
class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('retiro', 'Retiro'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.monto}"
    
class Producto(models.Model):
    DURACION_CHOICES = [
        ('1mes', '1 Mes'),
        ('2meses', '2 Meses'),
        ('6meses', '6 Meses'),
        ('12meses', '1 Año'),
    ]

    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    ingreso_diario = models.DecimalField(max_digits=10, decimal_places=2)
    limite = models.PositiveIntegerField(default=0)
    duracion = models.CharField(max_length=10, choices=DURACION_CHOICES, default='1mes')  # NUEVO CAMPO
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    


class CuentaBancaria(models.Model):
    banco = models.CharField(max_length=100)
    destinatario = models.CharField(max_length=150)
    numero_cuenta = models.CharField(max_length=50)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.banco} - {self.numero_cuenta}"



class Recarga(models.Model):
    ESTADO_CHOICES = [
        ('revision', 'En revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaBancaria, on_delete=models.PROTECT)

    monto = models.DecimalField(max_digits=12, decimal_places=2)
    referencia = models.CharField(max_length=50, unique=True)
    voucher = models.ImageField(upload_to='recargas/')

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='revision'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.monto} - {self.estado}"
    ESTADO_CHOICES = [
        ('revision', 'En revisión'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    banco = models.CharField(max_length=100)
    destinatario = models.CharField(max_length=150)
    numero_cuenta = models.CharField(max_length=50)

    monto = models.DecimalField(max_digits=12, decimal_places=2)
    referencia = models.CharField(max_length=50, unique=True)
    voucher = models.ImageField(upload_to='recargas/')

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default='revision'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.monto} - {self.estado}"
    

