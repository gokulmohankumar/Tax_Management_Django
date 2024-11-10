# Generated by Django 5.1.2 on 2024-11-06 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apptax', '0002_alter_deductions_entry_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deductions',
            name='entry_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='deductions', to='apptax.basictaxdetail'),
        ),
        migrations.AlterField(
            model_name='incomedetails',
            name='entry_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='income_details', to='apptax.basictaxdetail'),
        ),
        migrations.AlterField(
            model_name='taxcalculation',
            name='entry_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='tax_calculation', to='apptax.basictaxdetail'),
        ),
    ]
