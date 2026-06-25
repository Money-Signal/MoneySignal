from django.db import models

# Create your models here.
from django.db import models

class ExchangeRate(models.Model):
    currency_code = models.CharField(max_length=10)  # USD, JPY 등
    currency_name = models.CharField(max_length=50)  # 미국 달러 등
    date = models.DateField()                         # 환율 기준일
    deal_bas_r = models.FloatField()                  # 매매기준율

    class Meta:
        unique_together = ('currency_code', 'date')  # 날짜+통화 중복 방지
        ordering = ['date']

    def __str__(self):
        return f"{self.currency_code} {self.date} {self.deal_bas_r}"