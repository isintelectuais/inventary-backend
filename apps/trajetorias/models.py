from django.db import models
from agendamentos.models import Agendamento


class Trajetoria(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='trajetorias')
    codigo_localizacao = models.CharField(max_length=100)  # Formato: cidade:bairro:rua:predio:nivel:apto
    data_hora = models.DateTimeField(auto_now_add=True)
    dados_sensores = models.JSONField(default=dict)  # Dados coletados durante a trajetória

    class Meta:
        verbose_name = 'Trajetória'
        verbose_name_plural = 'Trajetórias'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['codigo_localizacao']),
        ]

    def __str__(self):
        return f"Trajetória {self.id} - {self.codigo_localizacao}"


class PontoInteresse(models.Model):
    trajetoria = models.ForeignKey(Trajetoria, on_delete=models.CASCADE, related_name='pontos_interesse')
    codigo = models.CharField(max_length=50)  # Código RFID ou QR Code
    tipo = models.CharField(max_length=20, choices=[
        ('inicio', 'Ponto de Início'),
        ('fim', 'Ponto de Fim'),
        ('checkpoint', 'Checkpoint'),
        ('obstaculo', 'Obstáculo Detectado')
    ])
    dados = models.JSONField(default=dict)  # Dados adicionais
    data_hora = models.DateTimeField()

    class Meta:
        verbose_name = 'Ponto de Interesse'
        verbose_name_plural = 'Pontos de Interesse'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.codigo}"