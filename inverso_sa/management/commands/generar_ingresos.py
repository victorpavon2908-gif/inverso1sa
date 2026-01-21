from django.core.management.base import BaseCommand
from django.utils import timezone
from inverso_sa.models import Inversion, Transaccion

class Command(BaseCommand):
    help = 'Genera ingresos diarios a inversionistas'

    def handle(self, *args, **kwargs):
        inversiones = Inversion.objects.filter(activa=True)

        for inversion in inversiones:
            usuario = inversion.usuario
            producto = inversion.producto

            # crear ingreso
            Transaccion.objects.create(
                usuario=usuario,
                monto=producto.ingreso_diario,
                tipo='ingreso'
            )

            # sumar saldo
            usuario.saldo += producto.ingreso_diario
            usuario.save()

        self.stdout.write("✅ Ingresos diarios generados")
