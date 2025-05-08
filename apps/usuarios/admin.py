from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    list_display = ("email", "nome", "matricula", "departamento", "cargo", "tipo", "is_staff", "is_active")
    list_filter = ("tipo", "is_staff", "is_active")
    search_fields = ("email", "nome", "matricula")
    ordering = ("email",)
    fieldsets = (
        ("Informações Pessoais", {"fields": ("email", "nome", "matricula", "departamento", "cargo", "tipo")}),
        ("Permissões", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Datas Importantes", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            "Criar Novo Usuário",
            {
                "classes": ("wide",),
                "fields": ("email", "nome", "matricula", "departamento", "cargo", "tipo", "password1", "password2"),
            },
        ),
    )

admin.site.register(Usuario, UsuarioAdmin)
