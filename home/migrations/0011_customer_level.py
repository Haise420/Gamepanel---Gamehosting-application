# Generated by Django 4.2.6 on 2023-12-21 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gamepanel', '0010_customer_balance_customer_img_customer_xp'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='level',
            field=models.CharField(choices=[('1', '1 Level'), ('2', '2 Level'), ('3', '3 Level'), ('4', '4 Level'), ('5', '5 Level')], default='1', max_length=2),
        ),
    ]
