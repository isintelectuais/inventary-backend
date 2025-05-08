from django.db import models
from robos.models import Robo
from agendamentos.models import Agendamento

class ImagemCapturada(models.Model):
    robo = models.ForeignKey(Robo, on_delete=models.CASCADE, related_name='imagens')
    url_imagem = models.TextField(verbose_name='URL da Imagem')
    codigo_lido = models.CharField(max_length=50, verbose_name='Código Identificado')
    data_hora = models.DateTimeField(auto_now_add=True, verbose_name='Data/Hora da Captura')

    class Meta:
        verbose_name = 'Imagem Capturada'
        verbose_name_plural = 'Imagens Capturadas'
        ordering = ['-data_hora']

    def __str__(self):
        return f"Imagem {self.id} - Robô {self.robo.identificador}"

class LogProcessamentoImagem(models.Model):
    imagem = models.ForeignKey(ImagemCapturada, on_delete=models.CASCADE, related_name='logs_processamento')
    status = models.CharField(max_length=20, choices=[
        ('sucesso', 'Sucesso'),
        ('falha', 'Falha'),
        ('sem_codigo', 'Sem Código Detectado')
    ])
    detalhes = models.TextField(blank=True, null=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de Processamento'
        verbose_name_plural = 'Logs de Processamento'
        ordering = ['-data_hora']

    def __str__(self):
        return f"Log {self.id} - {self.status}"