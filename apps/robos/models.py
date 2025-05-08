from django.db import models
from armazens.models import Armazem
from usuarios.models import Usuario


class Robo(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('em_missao', 'Em Missão'),
        ('manutencao', 'Em Manutenção'),
        ('erro', 'Erro')
    ]

    identificador = models.CharField(max_length=50, unique=True)
    armazem = models.ForeignKey(Armazem, on_delete=models.PROTECT, related_name='robos')
    modelo = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inativo')
    habilitado = models.BooleanField(default=True)
    sensores = models.JSONField(default=dict)  # Dados dinâmicos dos sensores
    ultima_comunicacao = models.DateTimeField(auto_now=True)
    configuracao = models.JSONField(default=dict)  # Configurações do robô (WiFi, token, etc.)

    class Meta:
        verbose_name = 'Robô'
        verbose_name_plural = 'Robôs'
        ordering = ['identificador']

    def __str__(self):
        return f"{self.identificador} ({self.armazem.nome})"


class ComandoRobo(models.Model):
    TIPOS_COMANDO = [
        ('desligar', 'Desligar'),
        ('reiniciar', 'Reiniciar'),
        ('pausar', 'Pausar Missão'),
        ('retomar', 'Retomar Missão'),
        ('emergencia', 'Parada de Emergência')
    ]

    robo = models.ForeignKey(Robo, on_delete=models.CASCADE, related_name='comandos')
    tipo = models.CharField(max_length=20, choices=TIPOS_COMANDO)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    executado = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_execucao = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Comando para Robô'
        verbose_name_plural = 'Comandos para Robôs'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Comando {self.get_tipo_display()} para {self.robo.identificador}"