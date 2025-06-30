from django.db import models

class ApiToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    expiracao = models.DateTimeField()

class ApiLogs(models.Model):
    endpoint = models.CharField(max_length=200)
    metodo = models.CharField(max_length=10)
    status_http = models.IntegerField()
    sucesso = models.BooleanField()
    payload_enviado = models.JSONField()
    payload_resposta = models.JSONField()
    mensagem = models.TextField()
    data_hora = models.DateTimeField(auto_now_add=True)

class ApiChecklist(models.Model):
    referencia_externa = models.CharField(max_length=100)
    entidade = models.CharField(max_length=50)
    encontrado_localmente = models.BooleanField()
    divergencia = models.TextField(null=True, blank=True)
    data_hora = models.DateTimeField(auto_now_add=True)
