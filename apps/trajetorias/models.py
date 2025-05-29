from django.db import models
from apps.agendamentos.models import Agendamento

class Trajetoria(models.Model):
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='trajetorias_principal',
        related_query_name='trajetoria_principal',
        verbose_name='Agendamento relacionado'
    )
    codigo_localizacao = models.CharField(
        max_length=100,
        verbose_name='Código de Localização',
        help_text='Formato: cidade:bairro:rua:predio:nivel:apto'
    )
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data e Hora'
    )
    dados_sensores = models.JSONField(
        default=dict,
        verbose_name='Dados dos Sensores',
        help_text='Dados coletados durante a trajetória'
    )

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
    trajetoria = models.ForeignKey(
        Trajetoria,
        on_delete=models.CASCADE,
        related_name='pontos_interesse',
        verbose_name='Trajetória associada'
    )
    codigo = models.CharField(
        max_length=50,
        verbose_name='Código',
        help_text='Código RFID ou QR Code'
    )
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('inicio', 'Ponto de Início'),
            ('fim', 'Ponto de Fim'),
            ('checkpoint', 'Checkpoint'),
            ('obstaculo', 'Obstáculo Detectado')
        ],
        verbose_name='Tipo de Ponto'
    )
    dados = models.JSONField(
        default=dict,
        verbose_name='Dados Adicionais'
    )
    data_hora = models.DateTimeField(
        verbose_name='Data e Hora'
    )

    class Meta:
        verbose_name = 'Ponto de Interesse'
        verbose_name_plural = 'Pontos de Interesse'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.codigo}"