from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, matricula=None, tipo="Usuario", **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, matricula=matricula or None, tipo=tipo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("tipo", "Master")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email=email, password=password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPOS_USUARIO = [
        ("Master", "Master"),
        ("Admin", "Admin"),
        ("Usuario", "Usuario"),
    ]

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255, default="Usuário Padrão")

    matricula = models.CharField(max_length=20, blank=True, null=True, unique=True)

    departamento = models.CharField(max_length=50, blank=True)
    cargo = models.CharField(max_length=50, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPOS_USUARIO, default="Usuario")

    # Campos obrigatórios para integração com Django Admin e autenticação
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["tipo"]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["matricula"],
                name="unique_matricula",
                condition=~models.Q(matricula=None) & ~models.Q(matricula="")
            )
        ]

    def __str__(self):
        return self.email


    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "matricula": self.matricula if self.matricula else "",  # None vira ""
            "departamento": self.departamento,
            "cargo": self.cargo,
            "tipo": self.tipo
        }