from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='financial_goal',
            field=models.CharField(
                blank=True,
                choices=[
                    ('HOME',       '내집마련'),
                    ('WEDDING',    '결혼자금'),
                    ('RETIREMENT', '노후준비'),
                    ('TRAVEL',     '여행/여가'),
                    ('EDUCATION',  '자녀교육'),
                    ('EMERGENCY',  '비상금 마련'),
                    ('ETC',        '기타'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.RemoveField(
            model_name='user',
            name='target_amount',
        ),
        migrations.AddField(
            model_name='user',
            name='occupation',
            field=models.CharField(
                blank=True,
                choices=[
                    ('EMPLOYEE',    '직장인'),
                    ('SELF_EMPLOY', '자영업자'),
                    ('STUDENT',     '학생'),
                    ('HOUSEWIFE',   '주부'),
                    ('FREELANCER',  '프리랜서'),
                    ('ETC',         '기타'),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
