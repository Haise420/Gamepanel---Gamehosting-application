# Generated by Django 4.2.6 on 2024-01-13 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamepanel', '0021_alter_customer_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='label',
            field=models.CharField(blank=True, choices=[('Uplata', 'Uplata'), ('Pitanje', 'Pitanje'), ('Pomoc', 'Pomoc'), ('Hitna pomoc!', 'Hitna pomoc!')], max_length=20, null=True),
        ),
    ]
