# Generated by Django 4.2.13 on 2024-06-27 09:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('variables', '0003_targetyear_yearlyinputvalue'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='yearlyinputvalue',
            unique_together={('variable', 'year')},
        ),
        migrations.RemoveField(
            model_name='yearlyinputvalue',
            name='target_year',
        ),
    ]
