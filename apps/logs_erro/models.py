from django.db import models
from apps.robos.models import Robo
from apps.usuarios.models import Usuario

class LogErro(models.Model):
    robo = models.ForeignKey(
        Robo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_erro'
    )
    mensagem = models.TextField()
    origem = models.CharField(max_length=100)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log de Erro"
        verbose_name_plural = "Logs de Erro"
        ordering = ['-data_hora']

    def __str__(self):
        return f"Erro {self.id} - {self.origem} - {self.data_hora}"