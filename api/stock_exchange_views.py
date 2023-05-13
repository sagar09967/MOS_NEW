from rest_framework import request
from rest_framework.response import Response
# from stocksymbol import StockSymbol
from rest_framework.decorators import api_view
# from .stock_exchange_models import Index
# from yahoo_fin import stock_info as si
# import json
# api_key = '0aeab093-8852-4021-940e-f063fb69d08b'
# ss = StockSymbol(api_key)


# get symbol list based on market
# symbol_list_us = ss.get_symbol_list(market="IN")  # "us" or "america" will also work
#
# # get symbol list based on index
# symbol_list_spx = ss.get_symbol_list(index="NIFTY")
#
# # show a list of available market
# market_list = ss.market_list
#
# # show a list of available index
# index_list = ss.index_list
#
# default_obj = None
from api.stock_exchange_models import StockExchange, StockSymbol


@api_view(['GET'])
def get_list_of_exchanges(request):
    exchanges = list(StockExchange.objects.filter(is_active=True).values())
    return Response({"status": True, "data": exchanges})

@api_view(['GET'])
def get_symbol_list_by_exchange(request):
    stock_exchange = request.query_params.get("stock_exchange")
    symbols = list(StockSymbol.objects.filter(stock_exchange=stock_exchange).values())
    return Response({"status": True, "data": symbols})

# @api_view(['GET'])
# def get_list_of_indexes(request):
#     indexes = list(Index.objects.filter(is_active=True).values())
#     return Response({"status": True, "data": indexes})
#
#
# @api_view(['GET'])
# def get_symbol_list_by_index(request):
#     #companies = si.tickers_other(request.query_params.get("index"))
#     index = request.query_params.get("index")
#     tickers = ss.get_symbol_list(index=index)
#     return Response({"status": True, "data": tickers})
