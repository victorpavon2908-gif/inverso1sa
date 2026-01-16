from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('ingreso/', views.ingreso, name='ingreso'),
    path('equipo/', views.equipo_view, name='equipo'),
    path('inicio/', views.inicio, name='inicio'),
    path('mio/', views.mio_view, name='mio'),
    path('panel/', views.panel_view, name='panel'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('recargar/', views.recargar_view, name='recargar'),
    path('mis-recargas/', views.mis_recargas_view, name='mis_recargas'),


    path('cuentas/', views.cuentas_bancarias, name='cuentas_bancarias'),
    path('cuentas/crear/', views.crear_cuenta_bancaria, name='crear_cuenta_bancaria'),
    path('cuentas/editar/<int:id>/', views.editar_cuenta_bancaria, name='editar_cuenta_bancaria'),
    path('cuentas/eliminar/<int:id>/', views.eliminar_cuenta_bancaria, name='eliminar_cuenta_bancaria'),

    path('recargas/solicitudes/', views.solicitudes_recarga, name='solicitudes_recarga'),
    path('recargas/accion/<int:id>/', views.aprobar_rechazar_recarga, name='aprobar_rechazar_recarga'),

]

