# Generated by Django 4.2.6 on 2023-10-29 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wavelength', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='file',
            field=models.FileField(upload_to='uploads/'),
        ),
    ]
