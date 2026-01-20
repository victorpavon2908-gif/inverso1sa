from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Producto


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'saldo',
        'codigo_invitacion',
        'is_staff',
        'is_superuser',
    )

    list_filter = (
        'is_staff',
        'is_superuser',
        'groups',
    )

    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )

    ordering = ('-date_joined',)

    # ⬇️ SOLO tus campos extra (SIN groups)
    fieldsets = UserAdmin.fieldsets + (
        ('Inverso Info', {
            'fields': (
                'saldo',
                'codigo_invitacion',
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Inverso Info', {
            'fields': (
                'saldo',
            )
        }),
    )

    filter_horizontal = ('groups',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'ingreso_diario', 'limite', 'activo', 'creado')
    list_filter = ('activo', 'creado')
    search_fields = ('nombre',)
    readonly_fields = ('creado',)
