# Generated by Django 4.2.7 on 2023-12-06 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_experience'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='core.profile'),
        ),
    ]
