# Generated by Django 4.2.4 on 2023-09-14 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0011_alter_recipe_options_alter_recipe_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredienttorecipe',
            old_name='ingredients',
            new_name='ingredient',
        ),
    ]
