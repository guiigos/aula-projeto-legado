from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'clientes'


class Veiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    cor = models.CharField(max_length=30)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'veiculos'


class Vaga(models.Model):
    class Tipo(models.TextChoices):
        CARRO = 'CARRO', 'Carro'
        MOTO = 'MOTO', 'Moto'

    class Status(models.TextChoices):
        LIVRE = 'LIVRE', 'Livre'
        OCUPADA = 'OCUPADA', 'Ocupada'

    numero = models.CharField(max_length=10, unique=True)
    tipo = models.CharField(max_length=5, choices=Tipo.choices)
    status = models.CharField(max_length=7, choices=Status.choices, default=Status.LIVRE)

    class Meta:
        db_table = 'vagas'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(tipo__in=['CARRO', 'MOTO']),
                name='vaga_tipo_valido',
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=['LIVRE', 'OCUPADA']),
                name='vaga_status_valido',
            ),
        ]


class Permanencia(models.Model):
    class Status(models.TextChoices):
        ABERTO = 'ABERTO', 'Aberto'
        FINALIZADO = 'FINALIZADO', 'Finalizado'

    # O histórico impede a exclusão do veículo e da vaga associados.
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT)
    vaga = models.ForeignKey(Vaga, on_delete=models.PROTECT)
    data_hora_entrada = models.DateTimeField(default=timezone.now)
    data_hora_saida = models.DateTimeField(blank=True, null=True)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ABERTO, db_index=True
    )

    class Meta:
        db_table = 'permanencias'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['ABERTO', 'FINALIZADO']),
                name='permanencia_status_valido',
            ),
        ]
