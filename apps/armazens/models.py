from django.db import models
from django.core.exceptions import ValidationError


class Armazem(models.Model):
    codigo_armazem = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=100)

    qtd_niveis = models.CharField(max_length=10)
    qtd_cidades = models.IntegerField()
    qtd_bairros_por_cidade = models.IntegerField()
    qtd_ruas_por_bairro = models.IntegerField()
    qtd_predios_por_rua = models.IntegerField()

    codigo_barra = models.CharField(max_length=50, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Armazéns"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.codigo_armazem})"

    def clean(self):
        # Validação para evitar códigos de armazém duplicados
        if Armazem.objects.filter(codigo_armazem=self.codigo_armazem).exclude(id=self.id).exists():
            raise ValidationError({'codigo_armazem': 'Este código de armazém já está em uso.'})

        # Validação para campos numéricos
        if any([
            self.qtd_cidades < 0,
            self.qtd_bairros_por_cidade < 0,
            self.qtd_ruas_por_bairro < 0,
            self.qtd_predios_por_rua < 0
        ]):
            raise ValidationError("Quantidades não podem ser negativas.")

    def save(self, *args, **kwargs):
        # Gera código de barras automaticamente
        if not self.codigo_barra:
            self.codigo_barra = (
                f"{self.codigo_armazem}-{self.qtd_niveis}-"
                f"{self.qtd_cidades}-{self.qtd_bairros_por_cidade}-"
                f"{self.qtd_ruas_por_bairro}-{self.qtd_predios_por_rua}"
            )

        self.full_clean()
        super().save(*args, **kwargs)