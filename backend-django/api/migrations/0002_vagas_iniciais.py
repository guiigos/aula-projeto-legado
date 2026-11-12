from django.db import migrations


def criar_vagas(apps, schema_editor):
    Vaga = apps.get_model('api', 'Vaga')
    banco = schema_editor.connection.alias
    for numero in range(1, 11):
        Vaga.objects.using(banco).get_or_create(
            numero=f'A{numero:02}', defaults={'tipo': 'CARRO', 'status': 'LIVRE'}
        )
    for numero in range(1, 6):
        Vaga.objects.using(banco).get_or_create(
            numero=f'B{numero:02}', defaults={'tipo': 'MOTO', 'status': 'LIVRE'}
        )


class Migration(migrations.Migration):
    dependencies = [('api', '0001_initial')]
    operations = [migrations.RunPython(criar_vagas, migrations.RunPython.noop)]
