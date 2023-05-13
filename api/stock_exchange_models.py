import os

from django.db import models, transaction
from .validators import AllowedExtensionsValidator, ExcelFileValidator
import pandas as pd


class Index(models.Model):
    index = models.CharField(max_length=10)
    is_active = models.BooleanField()

    def __str__(self):
        return self.index

    class Meta:
        verbose_name_plural = 'indexes'


class StockExchange(models.Model):
    stock_exchange = models.CharField(max_length=50)
    abbr = models.CharField(max_length=10)
    symbols_file = models.FileField(upload_to='stock_exchange_symbol_lists', null=True, blank=True,
                                    validators=[AllowedExtensionsValidator(['.xlsx', '.csv', '.xltx', '.xls']),
                                                ExcelFileValidator(['stock', 'symbol'])])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.stock_exchange}_{self.abbr}'

    @transaction.atomic
    def save(self, *args, **kwargs):
        super(StockExchange, self).save()
        self.refresh_from_db()
        df = pd.read_excel(self.symbols_file.path)
        for index, row in df.iterrows():
            stock_symbol = StockSymbol(stock=row['stock'], symbol=row['symbol'], stock_exchange=self)
            stock_symbol.save()


class StockSymbol(models.Model):
    stock = models.CharField(max_length=200)
    symbol = models.CharField(max_length=50)
    stock_exchange = models.ForeignKey(StockExchange, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.stock}_{self.symbol}_{self.stock_exchange}'
