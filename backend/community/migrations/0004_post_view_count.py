from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0003_post_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='view_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
