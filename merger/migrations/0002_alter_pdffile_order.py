# Generated by Django 5.0.3 on 2024-03-09 13:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdffile',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_files', to='merger.order'),
        ),
    ]