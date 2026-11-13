from django.db import models


class Cliente(models.Model):
    nome     = models.CharField(max_length=100)
    cpf      = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email    = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'clientes'


class Veiculo(models.Model):
    placa   = models.CharField(max_length=10, unique=True)
    marca   = models.CharField(max_length=50)
    modelo  = models.CharField(max_length=50)
    cor     = models.CharField(max_length=30)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'veiculos'


class Vaga(models.Model):
    TIPOS = [('CARRO', 'Carro'), ('MOTO', 'Moto')]
    STATUS = [('LIVRE', 'Livre'), ('OCUPADA', 'Ocupada')]

    numero = models.CharField(max_length=10, unique=True)
    tipo   = models.CharField(max_length=5, choices=TIPOS)
    status = models.CharField(max_length=7, choices=STATUS, default='LIVRE')

    class Meta:
        db_table = 'vagas'


class Permanencia(models.Model):
    STATUS = [('ABERTO', 'Aberto'), ('FINALIZADO', 'Finalizado')]

    veiculo           = models.ForeignKey(Veiculo, on_delete=models.PROTECT)
    vaga              = models.ForeignKey(Vaga, on_delete=models.PROTECT)
    data_hora_entrada = models.DateTimeField()
    data_hora_saida   = models.DateTimeField(null=True, blank=True)
    valor_total       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status            = models.CharField(max_length=10, choices=STATUS, default='ABERTO', db_index=True)

    class Meta:
        db_table = 'permanencias'