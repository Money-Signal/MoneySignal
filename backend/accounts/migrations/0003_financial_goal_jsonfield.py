from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_financial_info'),
    ]

    operations = [
        # VARCHAR → JSON 타입 변환 전에 기존 문자열 값을 유효한 JSON 배열로 변환
        # "HOME" → ["HOME"], NULL/'' → NULL
        migrations.RunSQL(
            sql="""
                UPDATE accounts_user
                SET financial_goal = CASE
                    WHEN financial_goal IS NULL OR financial_goal = '' THEN NULL
                    ELSE JSON_ARRAY(financial_goal)
                END;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='user',
            name='financial_goal',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
