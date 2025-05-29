from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.usuarios.models import Usuario
from apps.robos.models import Robo
from apps.armazens.models import Armazem


class Agendamento(models.Model):
    STATUS_CHOICES = [
        ('concluido', 'Concluído'),
        ('aguardando', 'Aguardando'),
        ('em_andamento', 'Em Andamento'),
        ('alerta', 'Alerta'),
        ('problema', 'Problema'),
        ('cancelado', 'Cancelado')
    ]

    TIPO_CHOICES = [
        ('completo', 'Inventário Completo'),
        ('parcial', 'Inventário Parcial'),
        ('emergencial', 'Verificação Emergencial')
    ]

    robo = models.ForeignKey(Robo, on_delete=models.PROTECT, related_name='agendamentos')
    armazem = models.ForeignKey(Armazem, on_delete=models.PROTECT, related_name='agendamentos')
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='agendamentos_criados')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aguardando')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='completo')
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    descricao = models.TextField(blank=True, null=True)
    cidades = models.JSONField(default=list, blank=True)  # Lista de cidades específicas para inventário parcial
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    excluido_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='agendamentos_excluidos')
    excluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-data_inicio']
        constraints = [
            models.CheckConstraint(
                check=models.Q(data_fim__gt=models.F('data_inicio')),
                name='check_data_fim_maior_que_inicio'
            )
        ]

    def __str__(self):
        return f"Agendamento #{self.id} - {self.get_status_display()}"

    def clean(self):
        # Validação para garantir que o robô pertence ao armazém
        if self.robo.armazem != self.armazem:
            raise ValidationError("O robô selecionado não pertence a este armazém")

        # Validação de conflito de agendamento
        conflitos = Agendamento.objects.filter(
            robo=self.robo,
            data_inicio__lt=self.data_fim,
            data_fim__gt=self.data_inicio,
            status__in=['aguardando', 'em_andamento']
        ).exclude(pk=self.pk if self.pk else None)

        if conflitos.exists():
            raise ValidationError("Conflito de agendamento: o robô já está agendado neste período")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class NotificacaoAgendamento(models.Model):
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    tipo = models.CharField(max_length=20, choices=[
        ('info', 'Informação'),
        ('alerta', 'Alerta'),
        ('erro', 'Erro')
    ])
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificação de Agendamento'
        verbose_name_plural = 'Notificações de Agendamento'
        ordering = ['-criada_em']

    def __str__(self):
        return f"Notificação #{self.id} - {self.get_tipo_display()}"