from django.db import models
from apps.agendamentos.models import Agendamento
from apps.armazens.models import Armazem
from apps.robos.models import Robo  # Assumindo que você tem um modelo Robo

class Inventario(models.Model):
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='itens_inventario',
        verbose_name='Agendamento relacionado'
    )
    robo = models.ForeignKey(
        Robo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventarios_realizados',
        verbose_name='Robô executor'
    )
    codigo_palete = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código Único do Palete'
    )
    codigo_endereco = models.CharField(
        max_length=50,
        verbose_name='Código do Endereço Físico',
        help_text='Localização física no armazém'
    )
    data_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora do Registro'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('verificado', 'Verificado'),
            ('divergente', 'Divergente'),
            ('ajustado', 'Ajustado')
        ],
        default='pendente',
        verbose_name='Status do Item'
    )
    dados_adicionais = models.JSONField(
        default=dict,
        verbose_name='Dados Adicionais',
        blank=True
    )

    class Meta:
        verbose_name = 'Item de Inventário'
        verbose_name_plural = 'Itens de Inventário'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['codigo_palete']),
            models.Index(fields=['codigo_endereco']),
            models.Index(fields=['status']),
            models.Index(fields=['agendamento', 'robo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['codigo_palete', 'agendamento'],
                name='unique_palete_por_agendamento'
            )
        ]

    def __str__(self):
        return f"Inv-{self.id}: {self.codigo_palete} ({self.get_status_display()})"


class Trajetoria(models.Model):
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='trajetorias_inventario',
        verbose_name='Agendamento relacionado'
    )
    robo = models.ForeignKey(
        Robo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trajetorias_percorridas',
        verbose_name='Robô executor'
    )
    codigo_localizacao = models.CharField(
        max_length=100,
        verbose_name='Código de Localização',
        help_text='Formato: cidade:bairro:rua:predio:nivel:apto'
    )
    data_hora_inicio = models.DateTimeField(
        verbose_name='Início da Trajetória'
    )
    data_hora_fim = models.DateTimeField(
        verbose_name='Fim da Trajetória',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('em_andamento', 'Em Andamento'),
            ('concluida', 'Concluída'),
            ('interrompida', 'Interrompida'),
            ('falha', 'Falha')
        ],
        default='em_andamento',
        verbose_name='Status'
    )
    metricas = models.JSONField(
        default=dict,
        verbose_name='Métricas da Trajetória',
        help_text='Dados de desempenho e sensores'
    )

    class Meta:
        verbose_name = 'Trajetória de Inventário'
        verbose_name_plural = 'Trajetórias de Inventário'
        ordering = ['agendamento', '-data_hora_inicio']
        indexes = [
            models.Index(fields=['codigo_localizacao']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Traj-{self.id}: {self.codigo_localizacao} ({self.get_status_display()})"


class EstatisticaInventario(models.Model):
    armazem = models.ForeignKey(
        Armazem,
        on_delete=models.CASCADE,
        related_name='estatisticas_inventario',
        verbose_name='Armazém relacionado'
    )
    periodo_referencia = models.DateField(
        verbose_name='Período de Referência'
    )
    data_calculo = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora do Cálculo'
    )
    total_itens = models.PositiveIntegerField(
        verbose_name='Total de Itens Inventariados'
    )
    itens_por_cidade = models.JSONField(
        verbose_name='Distribuição por Cidade'
    )
    itens_por_bairro = models.JSONField(
        verbose_name='Distribuição por Bairro'
    )
    precisao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Precisão do Inventário (%)'
    )
    tempo_total = models.DurationField(
        verbose_name='Tempo Total Gasto'
    )
    relatorio = models.FileField(
        upload_to='relatorios/inventario/',
        null=True,
        blank=True,
        verbose_name='Relatório Completo'
    )

    class Meta:
        verbose_name = 'Estatística de Inventário'
        verbose_name_plural = 'Estatísticas de Inventário'
        ordering = ['-periodo_referencia']
        unique_together = ['armazem', 'periodo_referencia']

    def __str__(self):
        return f"Estat-{self.armazem.codigo_armazem}: {self.periodo_referencia}"

    def save(self, *args, **kwargs):
        # Cálculo automático da precisão se não for fornecido
        if not self.precisao and 'itens_divergentes' in self.itens_por_cidade:
            total_divergentes = sum(self.itens_por_cidade['itens_divergentes'].values())
            if self.total_itens > 0:
                self.precisao = 100 - (total_divergentes / self.total_itens * 100)
        super().save(*args, **kwargs)