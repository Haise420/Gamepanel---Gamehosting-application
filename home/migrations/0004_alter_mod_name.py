# Generated by Django 4.2.6 on 2023-12-02 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamepanel', '0003_alter_mod_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mod',
            name='name',
            field=models.CharField(blank=True, choices=[('clanwar', 'clanwar'), ('zombieplague', 'zombieplague'), ('surf', 'surf'), ('deathrun', 'deathrun'), ('knifearena', 'knifearena'), ('gungame', 'gungame'), ('deathmatch', 'deathmatch'), ('fy_snow', 'fy_snow'), ('public', 'public')], max_length=30, null=True),
        ),
    ]
