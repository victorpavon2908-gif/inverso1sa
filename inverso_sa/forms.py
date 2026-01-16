
from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'ingreso_diario', 'limite', 'duracion', 'imagen', 'activo']

from django import forms
from .models import CuentaBancaria

class CuentaBancariaForm(forms.ModelForm):
    class Meta:
        model = CuentaBancaria
        fields = ['banco', 'destinatario', 'numero_cuenta', 'activa']
