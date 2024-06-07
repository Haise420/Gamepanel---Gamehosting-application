# Generated by Django 4.2.6 on 2023-12-19 11:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamepanel', '0007_ftp_user_password_label_alter_ftp_user_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('label', models.CharField(blank=True, max_length=300, null=True)),
                ('version', models.CharField(blank=True, max_length=300, null=True)),
                ('img', models.ImageField(blank=True, upload_to='plugins/')),
                ('game', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gamepanel.game')),
            ],
        ),
    ]
