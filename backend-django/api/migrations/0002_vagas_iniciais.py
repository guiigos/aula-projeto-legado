from django.db import migrations

CARROS = [f'A{n:02d}' for n in range(1, 11)]
MOTOS = [f'B{n:02d}' for n in range(1, 6)]


def criar_vagas(apps, schema_editor):
    """Mesmas vagas de exemplo que o init.sql do PostgreSQL inseria."""
    Vaga = apps.get_model('api', 'Vaga')
    for numero in CARROS:
        Vaga.objects.get_or_create(numero=numero, defaults={'tipo': 'CARRO'})
    for numero in MOTOS:
        Vaga.objects.get_or_create(numero=numero, defaults={'tipo': 'MOTO'})


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_vagas, migrations.RunPython.noop),
    ]
