# Generated by Django 5.0.3 on 2024-03-18 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merger', '0004_alter_order_download_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdffile',
            name='file',
            field=models.FileField(upload_to='pdf_uploads'),
        ),
    ]
