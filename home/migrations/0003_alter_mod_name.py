# Generated by Django 4.2.6 on 2023-12-02 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamepanel', '0002_alter_customer_id_alter_ftp_user_id_alter_game_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mod',
            name='name',
            field=models.CharField(blank=True, choices=[('clanwar', 'Clanwar'), ('zombieplague', 'Zombieplague'), ('surf', 'Surf'), ('deathrun', 'Deathrun'), ('knifearena', 'Knifearena'), ('gungame', 'Gungame'), ('deathmatch', 'Deathmatch'), ('fy_snow', 'Fy_snow'), ('public', 'Public')], max_length=30, null=True),
        ),
    ]
