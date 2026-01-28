from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from datetime import date
from .models import Usuario, Transaccion, Producto, Recarga, CuentaBancaria, Inversion, Retiro, CuentaUsuario
from django.contrib.auth.hashers import make_password
from django.db.models import Sum
from.forms import ProductoForm, CuentaBancariaForm
from django.contrib import messages
import random
from django.utils import timezone
from datetime import timedelta
# --------------------
# LOGIN
# --------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'inverso_sa/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request, 'inverso_sa/login.html')


# --------------------
# DASHBOARD
# --------------------
@login_required(login_url='login')
def dashboard(request):
    return redirect('inicio')


# --------------------
# LOGOUT
# --------------------
def logout_view(request):
    logout(request)
    return redirect('login')


# --------------------
# REGISTRO
# --------------------
def registro_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        codigo_ingresado = request.POST.get('codigo_invitacion')

        if password1 != password2:
            return render(request, 'inverso_sa/registro.html', {
                'error': 'Las contraseñas no coinciden'
            })

        if Usuario.objects.filter(username=username).exists():
            return render(request, 'inverso_sa/registro.html', {
                'error': 'El usuario ya existe'
            })

        if Usuario.objects.filter(email=email).exists():
            return render(request, 'inverso_sa/registro.html', {
                'error': 'El correo ya está registrado'
            })

        usuario = Usuario.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            saldo=20,
            password=make_password(password1)
        )

        grupo, _ = Group.objects.get_or_create(name='inversionista')
        usuario.groups.add(grupo)

        # 🔗 GUARDAR QUIÉN LO INVITÓ
        if codigo_ingresado:
            try:
                invitador = Usuario.objects.get(codigo_invitacion=codigo_ingresado)
                usuario.referido_por = invitador
                usuario.save()
            except Usuario.DoesNotExist:
                pass

        return redirect('login')

    return render(request, 'inverso_sa/registro.html')




# --------------------
# OTRAS VISTAS
# --------------------
@login_required
def ingreso(request):
    usuario = request.user

    inversiones_activas = Inversion.objects.filter(
        usuario=usuario,
        activa=True
    )

    inversiones_expiradas = Inversion.objects.filter(
        usuario=usuario,
        activa=False
    )

    context = {
        'saldo': usuario.saldo,
        'inversiones_activas': inversiones_activas,
        'inversiones_expiradas': inversiones_expiradas,
        'total_proyectos': inversiones_activas.count(),  # ✅ AQUÍ
    }

    return render(request, 'inverso_sa/ingreso.html', context)

# --------------------
# MIO
# --------------------
@login_required
def mio_view(request):
    usuario = request.user

    inversiones = Inversion.objects.filter(
        usuario=usuario,
        activa=True
    )

    # 🔁 generar ingresos si ya pasaron 24h
    for inversion in inversiones:
        if inversion.puede_pagar():
            inversion.pagar()

    
    hoy = timezone.now().date()

    ganancias_hoy = Transaccion.objects.filter(
    usuario=usuario,
    tipo='ingreso',
    fecha__date=hoy).aggregate(total=Sum('monto'))['total'] or 0

    context = {
        'usuario': usuario,
        'saldo': usuario.saldo,
        'ganancias_hoy': ganancias_hoy,
        'inversiones': inversiones
    }

    return render(request, 'inverso_sa/mio.html', context)

@login_required
def panel_view(request):

    filtro = request.GET.get("rol")

    usuarios = Usuario.objects.all()

    if filtro == "admin":
        usuarios = usuarios.filter(is_staff=True)
    elif filtro == "user":
        usuarios = usuarios.filter(is_staff=False)

    return render(request, 'inverso_sa/usuarios.html', {
        'usuarios': usuarios,
        'filtro': filtro
    })




def inicio(request):
    productos = Producto.objects.filter(activo=True)

    return render(request, "inverso_sa/inicio.html", {
        "productos": productos
    })


def agregar_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Redirige a la lista de productos
    else:
        form = ProductoForm()
    return render(request, 'inverso_sa/agregar_producto.html', {'form': form})

from decimal import Decimal, InvalidOperation

@login_required
def recargar_view(request):

    montos_rapidos = [400, 600, 800, 1000, 1500, 3000, 5000]

    cuentas = CuentaBancaria.objects.filter(activa=True)

    if not cuentas.exists():
        messages.error(request, "No hay cuentas bancarias disponibles")
        return redirect("inicio")

    cuenta = random.choice(list(cuentas))

    if request.method == "POST":
        try:
            monto = Decimal(request.POST.get("monto"))
        except (InvalidOperation, TypeError):
            messages.error(request, "Monto inválido")
            return redirect("recargar")

        referencia = request.POST.get("referencia")
        voucher = request.FILES.get("voucher")

        # ✅ VALIDACIÓN MÍNIMA
        if monto < 400:
            messages.error(request, "⚠ El monto mínimo de recarga es C$400")
            return redirect("recargar")

        # ❌ referencia repetida
        if Recarga.objects.filter(referencia=referencia).exists():
            messages.error(request, "Número de referencia repetido")
            return redirect("recargar")

        # ❌ voucher obligatorio
        if not voucher:
            messages.error(request, "Debe adjuntar el comprobante")
            return redirect("recargar")

        Recarga.objects.create(
            usuario=request.user,
            cuenta=cuenta,
            monto=monto,
            referencia=referencia,
            voucher=voucher
        )

        messages.success(request, "✅ Recarga enviada correctamente")
        return redirect("mis_recargas")

    return render(request, "inverso_sa/recargar.html", {
        "cuenta": cuenta,
        "montos_rapidos": montos_rapidos
    })


@login_required
def mis_recargas_view(request):
    recargas = Recarga.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'inverso_sa/mis_recargas.html', {'recargas': recargas})

@login_required
def cuentas_bancarias(request):
    cuentas = CuentaBancaria.objects.all().order_by('-fecha_creacion')
    return render(request, 'inverso_sa/cuentas_bancarias.html', {
        'cuentas': cuentas
    })


@login_required
def crear_cuenta_bancaria(request):
    if request.method == 'POST':
        form = CuentaBancariaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Cuenta bancaria agregada correctamente')
            return redirect('cuentas_bancarias')
    else:
        form = CuentaBancariaForm()

    return render(request, 'inverso_sa/cuenta_form.html', {
        'form': form,
        'titulo': 'Agregar Cuenta Bancaria'
    })


@login_required
def editar_cuenta_bancaria(request, id):
    cuenta = get_object_or_404(CuentaBancaria, id=id)

    if request.method == 'POST':
        form = CuentaBancariaForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            messages.success(request, '✏ Cuenta bancaria actualizada')
            return redirect('cuentas_bancarias')
    else:
        form = CuentaBancariaForm(instance=cuenta)

    return render(request, 'inverso_sa/cuenta_form.html', {
        'form': form,
        'titulo': 'Editar Cuenta Bancaria'
    })


@login_required
def eliminar_cuenta_bancaria(request, id):
    cuenta = get_object_or_404(CuentaBancaria, id=id)

    cuenta.activa = False
    cuenta.save()

    messages.warning(
        request,
        "⛔ Cuenta bancaria desactivada (no se puede eliminar porque tiene movimientos)"
    )

    return redirect('cuentas_bancarias')


@login_required
def solicitudes_recarga(request):
    """
    Vista para listar todas las solicitudes de recarga en revisión.
    Permite aprobar o rechazar cada recarga mediante POST desde el template.
    """
    recargas = Recarga.objects.filter(estado='revision').order_by('-fecha')

    if request.method == 'POST':
        recarga_id = request.POST.get('recarga_id')
        accion = request.POST.get('accion')  # 'aprobar' o 'rechazar'

        recarga = get_object_or_404(Recarga, id=recarga_id)

        if recarga.estado != 'revision':
            messages.warning(request, '⚠ Esta recarga ya fue procesada.')
            return redirect('solicitudes_recarga')

        if accion == 'aprobar':
            recarga.estado = 'aprobada'
            # Sumar el monto al saldo del usuario
            recarga.usuario.saldo += recarga.monto
            recarga.usuario.save()
            recarga.save()
            messages.success(request, f'✅ Recarga de {recarga.usuario.username} aprobada correctamente.')
        elif accion == 'rechazar':
            recarga.estado = 'rechazada'
            recarga.save()
            messages.warning(request, f'❌ Recarga de {recarga.usuario.username} rechazada.')
        else:
            messages.error(request, 'Acción no válida.')

        return redirect('solicitudes_recarga')

    context = {
        'recargas': recargas,
    }
    return render(request, 'inverso_sa/solicitudes_recarga.html', context)

@login_required
def aprobar_rechazar_recarga(request, id):
    recarga = get_object_or_404(Recarga, id=id)

    if request.method == "POST":
        accion = request.POST.get("accion")

        if recarga.estado != 'revision':
            messages.warning(request, "Esta recarga ya fue procesada")
            return redirect('solicitudes_recarga')

        if accion == "aprobar":
            recarga.estado = 'aprobada'

            usuario = recarga.usuario
            usuario.saldo += recarga.monto
            usuario.save()
            recarga.save()

            # ✅ COMISIÓN SOLO PRIMERA RECARGA
            if (
                usuario.referido_por
                and not usuario.recarga_comision_pagada
            ):
                invitador = usuario.referido_por
                comision = recarga.monto * Decimal("0.04")

                invitador.saldo += comision
                invitador.save()

                usuario.recarga_comision_pagada = True
                usuario.save()

                messages.success(
                    request,
                    f"🎉 Comisión de C$ {comision:.2f} pagada al invitador"
                )

            messages.success(request, "✅ Recarga aprobada correctamente")

        elif accion == "rechazar":
            recarga.estado = 'rechazada'
            recarga.save()
            messages.warning(request, "❌ Recarga rechazada")

    return redirect('solicitudes_recarga')




@login_required
def invertir_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    usuario = request.user

    # ❌ saldo insuficiente
    if usuario.saldo < producto.precio:
        messages.error(request, "❌ Saldo insuficiente")
        return redirect('recargar')

    # ❌ límite alcanzado
    inversiones_actuales = Inversion.objects.filter(
        producto=producto,
        activa=True
    ).count()

    if inversiones_actuales >= producto.limite:
        messages.error(request, "⚠ Producto agotado")
        return redirect('inicio')

    # ✅ descontar saldo
    usuario.saldo -= producto.precio
    usuario.save()

    # ✅ crear inversión
    Inversion.objects.create(
        usuario=usuario,
        producto=producto
    )

    messages.success(request, "✅ Inversión realizada correctamente")
    return redirect('ingreso')


@login_required
def ver_productos(request):
    productos = Producto.objects.all().order_by('-creado')
    return render(request, 'inverso_sa/ver_productos.html', {
        'productos': productos
    })

@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        form = ProductoForm(
            request.POST,
            request.FILES,     # 🔥 ESTO ES LA CLAVE
            instance=producto
        )

        if form.is_valid():
            form.save()
            return redirect('ver_productos')

    else:
        form = ProductoForm(instance=producto)

    return render(request, 'inverso_sa/editar_producto.html', {
        'form': form,
        'producto': producto
    })


@login_required
def toggle_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.activo = not producto.activo
    producto.save()

    if producto.activo:
        messages.success(request, "✅ Producto activado")
    else:
        messages.warning(request, "⛔ Producto desactivado")

    return redirect('ver_productos')

@login_required
def agregar_cuenta_usuario(request):

    if request.method == "POST":
        banco = request.POST.get("banco")
        titular = request.POST.get("titular")
        numero_cuenta = request.POST.get("numero_cuenta")

        if not banco or not titular or not numero_cuenta:
            messages.error(request, "Todos los campos son obligatorios")
            return redirect("agregar_cuenta_usuario")

        if CuentaUsuario.objects.filter(
            usuario=request.user,
            numero_cuenta=numero_cuenta
        ).exists():
            messages.warning(request, "Esta cuenta ya fue registrada")
            return redirect("agregar_cuenta_usuario")

        CuentaUsuario.objects.create(
            usuario=request.user,
            banco=banco,
            titular=titular,
            numero_cuenta=numero_cuenta
        )

        messages.success(request, "Cuenta bancaria agregada correctamente")
        return redirect("inicio")

    return render(request, "inverso_sa/agregar_cuenta_usuario.html")


from decimal import Decimal

@login_required
def retirar_view(request):

    cuentas = CuentaUsuario.objects.filter(usuario=request.user)

    if not cuentas.exists():
        messages.warning(request, "Primero debes agregar una cuenta bancaria")
        return redirect("agregar_cuenta_usuario")

    if request.method == "POST":
        try:
            monto = Decimal(request.POST.get("monto"))
        except:
            messages.error(request, "Monto inválido")
            return redirect("retirar")

        cuenta_id = request.POST.get("cuenta")

        if monto <= 300:
            messages.error(request, "El monto debe ser mayor a 300")
            return redirect("retirar")

        if monto > request.user.saldo:
            messages.error(request, "Saldo insuficiente")
            return redirect("retirar")

        cuenta = get_object_or_404(
            CuentaUsuario,
            id=cuenta_id,
            usuario=request.user
        )

        # 🔻 DESCONTAR SALDO (YA ES DECIMAL)
        request.user.saldo -= monto
        request.user.save()

        # 📝 CREAR RETIRO
        Retiro.objects.create(
            usuario=request.user,
            cuenta=cuenta,
            monto=monto,
            estado='pendiente'
        )

        messages.success(request, "✅ Retiro enviado correctamente")
        return redirect("mio")

    return render(request, "inverso_sa/retirar.html", {
        "cuentas": cuentas,
        "saldo": request.user.saldo
    })



@login_required
def solicitudes_retiro(request):
    retiros = Retiro.objects.filter(estado="pendiente").order_by("-fecha")
    return render(request, 'inverso_sa/solicitudes_retiro.html', {
        'retiros': retiros
    })


@login_required
def procesar_retiro(request, id):
    retiro = get_object_or_404(Retiro, id=id)

    if request.method == "POST":
        accion = request.POST.get("accion")

        if retiro.estado != "pendiente":
            messages.warning(request, "Este retiro ya fue procesado")
            return redirect("solicitudes_retiro")

        if accion == "aprobar":
            retiro.estado = "aprobado"
            retiro.save()
            messages.success(request, "✅ Retiro aprobado correctamente")

        elif accion == "rechazar":
            retiro.estado = "rechazado"

            retiro.usuario.saldo += retiro.monto
            retiro.usuario.save()
            retiro.save()

            messages.warning(request, "❌ Retiro rechazado y dinero devuelto")

    return redirect("solicitudes_retiro")


@login_required
def equipo_view(request):
    usuario = request.user

    # 🔗 NIVELES DE EQUIPO
    nivel_1 = Usuario.objects.filter(referido_por=usuario)
    nivel_2 = Usuario.objects.filter(referido_por__in=nivel_1)
    nivel_3 = Usuario.objects.filter(referido_por__in=nivel_2)

    # 🔢 CONTADORES
    n1_total = nivel_1.count()
    n2_total = nivel_2.count()
    n3_total = nivel_3.count()

    # 🔗 LINK DE INVITACIÓN
    link = f"https://inverso1sa-5.onrender.com/registro/?ref={usuario.codigo_invitacion}"

    context = {
        "codigo": usuario.codigo_invitacion,
        "link": link,
        "n1_total": n1_total,
        "n2_total": n2_total,
        "n3_total": n3_total,
    }

    return render(request, "inverso_sa/equipo.html", context)

@login_required
def toggle_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.is_active = not usuario.is_active
    usuario.save()

    return redirect("panel_usuarios")

@login_required
def modificar_saldo(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == "POST":
        accion = request.POST.get("accion")
        monto = Decimal(request.POST.get("monto"))

        if monto <= 0:
            messages.error(request, "Monto inválido")
            return redirect("panel_usuarios")

        if accion == "sumar":
            usuario.saldo += monto
        elif accion == "restar":
            if usuario.saldo < monto:
                messages.error(request, "Saldo insuficiente")
                return redirect("panel_usuarios")
            usuario.saldo -= monto

        usuario.save()
        messages.success(request, "Saldo actualizado correctamente")

    return redirect("panel_usuarios")


def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == "POST":
        usuario.first_name = request.POST.get("first_name")
        usuario.last_name = request.POST.get("last_name")
        usuario.email = request.POST.get("email")
        usuario.username = request.POST.get("username")

        usuario.saldo = Decimal(request.POST.get("saldo"))

        usuario.save()

        messages.success(request, "Usuario actualizado correctamente")
        return redirect("panel_usuarios")

    return render(request, "inverso_sa/editar_usuario.html", {
        "usuario": usuario
    })


@login_required
def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.user.id == usuario.id:
        messages.error(request, "❌ No puedes eliminar tu propio usuario")
        return redirect("panel_usuarios")

    if request.method == "POST":
        usuario.delete()
        messages.success(request, "🗑 Usuario eliminado correctamente")
        return redirect("panel_usuarios")

    return render(request, "inverso_sa/confirmar_eliminar.html", {
        "usuario": usuario
    })


@login_required
def desactivar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    # evitar auto-eliminarse
    if usuario == request.user:
        return redirect('panel_usuarios')

    usuario.is_active = False
    usuario.save()

    return redirect('panel_usuarios')

@login_required
def activar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    usuario.is_active = True
    usuario.save()

    return redirect('panel_usuarios')


@login_required
def ingresos_egresos(request):

    hoy = timezone.now().date()
    filtro = request.GET.get('filtro', 'dia')
    cuenta_id = request.GET.get('cuenta')

    transacciones = Transaccion.objects.all().order_by('-fecha')

    # 🕒 FILTROS DE TIEMPO
    if filtro == 'dia':
        transacciones = transacciones.filter(fecha__date=hoy)

    elif filtro == 'semana':
        transacciones = transacciones.filter(
            fecha__date__gte=hoy - timedelta(days=7)
        )

    elif filtro == 'mes':
        transacciones = transacciones.filter(
            fecha__year=hoy.year,
            fecha__month=hoy.month
        )

    # 🏦 FILTRO POR CUENTA
    if cuenta_id:
        transacciones = transacciones.filter(cuenta_id=cuenta_id)

    total_ingresos = transacciones.filter(tipo='ingreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    total_egresos = transacciones.filter(tipo='egreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    balance = total_ingresos - total_egresos

    cuentas = CuentaBancaria.objects.filter(activa=True)

    return render(request, 'inverso_sa/ingresos_egresos.html', {
        'transacciones': transacciones,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'balance': balance,
        'cuentas': cuentas,
        'filtro': filtro,
        'cuenta_id': cuenta_id
    })


@login_required
def acerca_de(request):
    return render(request, "inverso_sa/acerca_de.html")


@login_required
def asistencia(request):
    return render(request, "inverso_sa/asistencia.html")


def custom_404_view(request, exception):
    if request.user.is_authenticated:
        return redirect('inicio')   # tu home logueado
    else:
        return redirect('login')    # tu login
