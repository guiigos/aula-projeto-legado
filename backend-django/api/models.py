from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=11)
    email = models.EmailField()

    class Meta():
        db_table = 'clientes'

    def __str__(self):
        return self.nome

class Veiculo(models.Model):
    placa = models.CharField(max_length=7, unique=True)
    marca = models.CharField(max_length=15)
    modelo = models.CharField(max_length=50)
    cor = models.CharField(max_length=20)

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='veiculos'
    )

    class Meta:
        db_table = 'veiculos'

    def __str__(self):
        return self.placa
    

class Vaga(models.Model):
    class Tipo(models.TextChoices):
        CARRO = 'CARRO', 'Carro'
        MOTO = 'MOTO', 'Moto'

    class Status(models.TextChoices):
        LIVRE = 'LIVRE', 'Livre'
        OCUPADA = 'OCUPADA', 'Ocupada'

    numero = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(
        max_length=5,
        choices=Tipo.choices
    )
    status = models.CharField(
        max_length=7,
        choices=Status.choices,
        default=Status.LIVRE
    )

    class Meta:
        db_table = 'vagas'

    def __str__(self):
        return self.numero

class Permanencia(models.Model):
    class Status(models.TextChoices):
        ABERTO = 'ABERTO', 'Aberto'
        FINALIZADO = 'FINALIZADO', 'Finalizado'

    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.PROTECT,
        related_name='permanencias'
    )

    vaga = models.ForeignKey(
        Vaga,
        on_delete=models.PROTECT,
        related_name='permanencias'
    )

    data_hora_entrada = models.DateTimeField()
    data_hora_saida = models.DateTimeField(
        null=True,
        blank=True
    )

    valor_total = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    null=True,
    blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ABERTO
    )

    class Meta:
        db_table = 'permanencias'

    def __str__(self):
        return f'{self.veiculo.placa} - {self.Status}'

#banco