from django.db import models
from agendamentos.models import Agendamento
from armazens.models import Armazem

class Inventario(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='itens_inventario')
    codigo_palete = models.CharField(max_length=50, verbose_name='Código do Palete')
    codigo_endereco = models.CharField(max_length=50, verbose_name='Código do Endereço')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora do Registro')

    class Meta:
        verbose_name = 'Item de Inventário'
        verbose_name_plural = 'Itens de Inventário'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['codigo_palete']),
            models.Index(fields=['codigo_endereco']),
        ]

    def __str__(self):
        return f"Inventário {self.id} - {self.codigo_palete}"

class Trajetoria(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='trajetorias')
    codigo_localizacao = models.CharField(
        max_length=100,
        verbose_name='Código de Localização',
        help_text='Formato: cidade:bairro:rua:predio:nivel:apto'
    )
    data_hora_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Trajetória'
        verbose_name_plural = 'Trajetórias'
        ordering = ['agendamento', '-data_hora_registro']

    def __str__(self):
        return f"Trajetória {self.id} - {self.codigo_localizacao}"

class EstatisticaInventario(models.Model):
    armazem = models.ForeignKey(Armazem, on_delete=models.CASCADE, related_name='estatisticas')
    data_calculo = models.DateTimeField(auto_now_add=True)
    total_itens = models.PositiveIntegerField()
    itens_por_cidade = models.JSONField(verbose_name='Itens por Cidade')
    itens_por_bairro = models.JSONField(verbose_name='Itens por Bairro')

    class Meta:
        verbose_name = 'Estatística de Inventário'
        verbose_name_plural = 'Estatísticas de Inventário'
        ordering = ['-data_calculo']

    def __str__(self):
        return f"Estatísticas {self.armazem.nome} - {self.data_calculo.date()}"