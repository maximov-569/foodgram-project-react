# Generated by Django 4.2.4 on 2023-09-07 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0003_ingredienttorecipe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredienttorecipe',
            name='recipe',
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, related_name='recipe', to='foodgram.ingredienttorecipe'),
        ),
    ]
