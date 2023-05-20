import yfinance as yf
import pandas as pd
import numpy
from rest_framework.views import APIView
from datetime import datetime
import datetime as dt
from rest_framework.response import Response
from django.http import HttpResponse, FileResponse
import csv


class StockAPI(APIView):
    """
    This API For Stock Buying and selling
    """

    def get(self, request, format=None):
        Money_in_Bank = request.GET.get("Bucket")
        lot_size = request.GET.get("lot_size")
        tickers = request.GET.get("share_name")
        from_date = request.GET.get("from_date")
        Buy_percentage = request.GET.get("Buy_percentage")
        Sale_percentage = request.GET.get("Sale_percentage")
        max_look_back_period = request.GET.get("max_look_back_period")
        Lot_size = int(lot_size)
        list_of_values = tickers.split(",")
        tickers = sorted(tickers)
        tickers = list(list_of_values)
        tickers = sorted(tickers)
        Money_in_Bank = int(Money_in_Bank)
        Buy_percentage = float(Buy_percentage)
        Sale_percentage = float(Sale_percentage)

        end = dt.datetime.today()
        data_10 = False
        position_1 = 0
        position_2 = 0
        position_3 = 0
        position_4 = 0
        position_5 = 0
        position_6 = 0
        position_7 = 0
        position_8 = 0
        print(tickers)
        # print("money_in_bank:",Money_in_Bank,type(Money_in_Bank))
        # print("lot_size:",Lot_size,type(Lot_size))

        # max_look_back_period_1 = 30
        # # from_date = "2023-01-01"
        look_values = []
        # max_look_back_period = 30
        ticker_obj = yf.Ticker(tickers[0])
        if data_10 == False:
            trans_1 = pd.DataFrame(
                columns=['Date', 'Stock', 'Price', 'Quantity', 'P_Value', 'S_date', 'Sale_Price', 'S_Value', 'Profit'])
            trans_2 = pd.DataFrame(
                columns=['Date', 'Stock', 'Perches/Sell', 'Quantity', 'Price', 'Value', 'Opening', 'Closing'])
            data_10 = True

        # for ticker in tickers
        stock_data_1 = yf.download(tickers, start=from_date, end=end)
        # look_bake_period = df1['LBP']
        New_List = []

        master_df = pd.DataFrame(
            columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price', 'third_purchase_price',
                     'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price', 'seventh_purchase_price',
                     'eighth_purchase_price',
                     'New_purchase_date', 'Second_purchase_date', 'third_purchase_date', 'fourth_purchase_date',
                     'fifth_purchase_date', 'sixth_purchase_date', 'seventh_purchase_date', 'eighth_purchase_date',
                     'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B', 'fifth_P_Value_B',
                     'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                     'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity', 'fifth_T_Quantity',
                     'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                     'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6', 'position_7',
                     'position_8'])

        dfs = {}
        # current_ticker = tickers[i]
        for ticker in tickers:
            data = yf.download(ticker, from_date, end, interval='1d')
            data.reset_index(inplace=True)
            data['Date'] = pd.to_datetime(data['Date'])
            data['Date'] = data['Date'].dt.strftime('%d/%m/%Y')
            data.set_index("Date", inplace=True)
            data.drop("Adj Close", axis=1, inplace=True)
            data.columns = ["Open", "High", "Low", "Close", "volume"]
            # data.insert(5, "Trade", "")
            # data["Trade"] = ""
            data['LBP'] = data['High'].rolling(30).max()
            LBP = data['LBP']
            data['LBP'] = data['High'].rolling(30).max()
            data['Low_LBP'] = 0.9 * data['LBP']
            data['ticker'] = ticker
            # df = data.dropna()
            df1 = pd.DataFrame(data)
            df2 = df1.round(1)
            dfs[ticker] = df2
            # with pd.ExcelWriter('output.xlsx') as writer:
            #     for ticker, df in dfs.items():
            #         df.to_excel(writer, sheet_name=ticker)

        for ticker in dfs:
            print(f"{ticker}:\n{dfs[ticker]}\n")
            df_concat = pd.concat([dfs[ticker]], axis=0, keys=[ticker], names=['Date'])
            df_concat = df_concat.reset_index(level=0, drop=True)
            print('df_concat:', df_concat)

        df_concat = pd.concat(dfs, axis=0, keys=tickers, names=['Date'])
        # reset index
        df_concat = df_concat.reset_index(level=0, drop=True)

        # print concatenated data frame
        print(df_concat)

        dfs = {}

        for f in range(len(stock_data_1)):  ##loop for iterating over dates first
            ticker_data = {}
            for i in range(len(tickers)):  ##loop for iterating over companies for each date
                current_ticker = tickers[i]
                current_date = 0

                # stock_data = df_concat(tickers[i], start=start, end=end)
                # stock_data = df_concat.loc[df_concat.index[f], tickers[i]]
                stock_data = df_concat[df_concat['ticker'] == current_ticker]

                # data = data.dropna(subset=['LBP'])
                try:
                    date_str = stock_data.index[f]  # Assuming the date is in string format
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')  # Corrected format
                    current_date = date_obj.strftime('%d-%m-%y')
                except Exception:
                    pass
                # current_date = stock_data.index[f].strftime('%d-%m-%y')
                # current_data = df_concat.index[(df_concat['ticker'] == current_ticker)].strftime('%d-%m-%y')
                # print(data.shape)
                # print(data.columns)
                # print(data.head())
                print('current_date:', current_date)
                # if current_date == '16-02-22':
                #     print("breakpoint")
                #     pass

                non_empty_master_df = master_df.dropna()

                prev_record_df = master_df[
                    (master_df['ticker'] == current_ticker) & ((master_df['new_purchase_price'] != 0) | (
                            master_df['Second_purchase_price'] != 0) | (
                                                                       master_df['third_purchase_price'] != 0) | (
                                                                       master_df['fourth_purchase_price'] != 0) | (
                                                                       master_df['fifth_purchase_price'] != 0) | (
                                                                       master_df['sixth_purchase_price'] != 0) | (
                                                                       master_df['seventh_purchase_price'] != 0) | (
                                                                       master_df['eighth_purchase_price'] != 0) | (
                                                                       master_df['New_purchase_date'] != '') | (
                                                                       master_df['Second_purchase_date'] != '') | (
                                                                       master_df['third_purchase_date'] != '') | (
                                                                       master_df['fourth_purchase_date'] != '') | (
                                                                       master_df['fifth_purchase_date'] != '') | (
                                                                       master_df['sixth_purchase_date'] != '') | (
                                                                       master_df['seventh_purchase_date'] != '') | (
                                                                       master_df['eighth_purchase_date'] != '') | (
                                                                       master_df['New_P_Value_B'] != 0) | (
                                                                       master_df['Second_P_Value_B'] != 0) | (
                                                                       master_df['third_P_Value_B'] != 0) | (
                                                                       master_df['fourth_P_Value_B'] != 0) | (
                                                                       master_df['fifth_P_Value_B'] != 0) | (
                                                                       master_df['sixth_P_Value_B'] != 0) | (
                                                                       master_df['seventh_P_Value_B'] != 0) | (
                                                                       master_df['eighth_P_Value_B'] != 0) | (
                                                                       master_df['T_Quantity'] != 0) | (
                                                                       master_df['Second_T_Quantity'] != 0) | (
                                                                       master_df['third_T_Quantity'] != 0) | (
                                                                       master_df['fourth_T_Quantity'] != 0) | (
                                                                       master_df['fifth_T_Quantity'] != 0) | (
                                                                       master_df['sixth_T_Quantity'] != 0) | (
                                                                       master_df['seventh_T_Quantity'] != 0) | (
                                                                       master_df['eighth_T_Quantity'] != 0))]

                prev_record = prev_record_df.iloc[-1] if len(prev_record_df) > 0 else None

                prev_record_index = master_df.index[
                    (master_df['ticker'] == current_ticker) & ((master_df['new_purchase_price'] != 0) | (
                            master_df['Second_purchase_price'] != 0) | (
                                                                       master_df['third_purchase_price'] != 0) | (
                                                                       master_df['fourth_purchase_price'] != 0) | (
                                                                       master_df['fifth_purchase_price'] != 0) | (
                                                                       master_df['sixth_purchase_price'] != 0) | (
                                                                       master_df['seventh_purchase_price'] != 0) | (
                                                                       master_df['eighth_purchase_price'] != 0) | (
                                                                       master_df['New_purchase_date'] != 0) | (
                                                                       master_df['Second_purchase_date'] != 0) | (
                                                                       master_df['third_purchase_date'] != 0) | (
                                                                       master_df['fourth_purchase_date'] != 0) | (
                                                                       master_df['fifth_purchase_date'] != '') | (
                                                                       master_df['sixth_purchase_date'] != '') | (
                                                                       master_df['seventh_purchase_date'] != '') | (
                                                                       master_df['eighth_purchase_date'] != '') | (
                                                                       master_df['New_P_Value_B'] != 0) | (
                                                                       master_df['Second_P_Value_B'] != 0) | (
                                                                       master_df['third_P_Value_B'] != 0) | (
                                                                       master_df['fourth_P_Value_B'] != 0) | (
                                                                       master_df['fifth_P_Value_B'] != 0) | (
                                                                       master_df['sixth_P_Value_B'] != 0) | (
                                                                       master_df['seventh_P_Value_B'] != 0) | (
                                                                       master_df['eighth_P_Value_B'] != 0) | (
                                                                       master_df['T_Quantity'] != 0) | (
                                                                       master_df['Second_T_Quantity'] != 0) | (
                                                                       master_df['third_T_Quantity'] != 0) | (
                                                                       master_df['fourth_T_Quantity'] != 0) | (
                                                                       master_df['fifth_T_Quantity'] != 0) | (
                                                                       master_df['sixth_T_Quantity'] != 0) | (
                                                                       master_df['seventh_T_Quantity'] != 0) | (
                                                                       master_df['eighth_T_Quantity'] != 0))] if len(
                    prev_record_df) > 0 else None

                New_purchase_price = prev_record['new_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['new_purchase_price']) else 0
                Second_purchase_price_5 = prev_record[
                    'Second_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['Second_purchase_price']) else 0
                third_purchase_price_5 = prev_record[
                    'third_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['third_purchase_price']) else 0
                fourth_purchase_price_5 = prev_record[
                    'fourth_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['fourth_purchase_price']) else 0
                fifth_purchase_price_5 = prev_record[
                    'fifth_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['fifth_purchase_price']) else 0
                sixth_purchase_price_5 = prev_record[
                    'sixth_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['sixth_purchase_price']) else 0
                seventh_purchase_price_5 = prev_record[
                    'seventh_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['seventh_purchase_price']) else 0
                eighth_purchase_price_5 = prev_record[
                    'eighth_purchase_price'] if prev_record is not None and not numpy.isnan(
                    prev_record['eighth_purchase_price']) else 0

                New_purchase_date_s = prev_record['New_purchase_date'] if prev_record is not None and (
                    prev_record['New_purchase_date']) else 0
                Second_purchase_date_s = prev_record['Second_purchase_date'] if prev_record is not None and (
                    prev_record['Second_purchase_date']) else 0
                third_purchase_date_s = prev_record['third_purchase_date'] if prev_record is not None and (
                    prev_record['third_purchase_date']) else 0
                fourth_purchase_date_s = prev_record['fourth_purchase_date'] if prev_record is not None and (
                    prev_record['fourth_purchase_date']) else 0
                fifth_purchase_date_s = prev_record['fifth_purchase_date'] if prev_record is not None and (
                    prev_record['fifth_purchase_date']) else 0
                sixth_purchase_date_s = prev_record['sixth_purchase_date'] if prev_record is not None and (
                    prev_record['sixth_purchase_date']) else 0
                seventh_purchase_date_s = prev_record['seventh_purchase_date'] if prev_record is not None and (
                    prev_record['seventh_purchase_date']) else 0
                eighth_purchase_date_s = prev_record['eighth_purchase_date'] if prev_record is not None and (
                    prev_record['eighth_purchase_date']) else 0

                New_P_Value_B_s = prev_record['New_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['New_P_Value_B']) else 0
                Second_P_Value_B_s = prev_record['Second_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['Second_P_Value_B']) else 0
                third_P_Value_B_s = prev_record['third_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['third_P_Value_B']) else 0
                fourth_P_Value_B_s = prev_record['fourth_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['fourth_P_Value_B']) else 0
                fifth_P_Value_B_s = prev_record['fifth_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['fifth_P_Value_B']) else 0
                sixth_P_Value_B_s = prev_record['sixth_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['sixth_P_Value_B']) else 0
                seventh_P_Value_B_s = prev_record['seventh_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['seventh_P_Value_B']) else 0
                eighth_P_Value_B_s = prev_record['eighth_P_Value_B'] if prev_record is not None and not numpy.isnan(
                    prev_record['eighth_P_Value_B']) else 0

                position_1 = prev_record['position_1'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_1']) else 0
                position_2 = prev_record['position_2'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_2']) else 0
                position_3 = prev_record['position_3'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_3']) else 0
                position_4 = prev_record['position_4'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_4']) else 0
                position_5 = prev_record['position_5'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_5']) else 0
                position_6 = prev_record['position_6'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_6']) else 0
                position_7 = prev_record['position_7'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_7']) else 0
                position_8 = prev_record['position_8'] if prev_record is not None and not numpy.isnan(
                    prev_record['position_8']) else 0

                T_Quantity_s = prev_record['T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['T_Quantity']) else 0
                Second_T_Quantity_s = prev_record['Second_T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['Second_T_Quantity']) else 0
                third_T_Quantity_s = prev_record['third_T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['third_T_Quantity']) else 0
                fourth_T_Quantity_s = prev_record['fourth_T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['fourth_T_Quantity']) else 0
                fifth_T_Quantity_s = prev_record['fifth_T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['fifth_T_Quantity']) else 0
                sixth_T_Quantity_s = prev_record['sixth_T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['sixth_T_Quantity']) else 0
                seventh_T_Quantity_s = prev_record['seventh_T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['seventh_T_Quantity']) else 0
                eighth_T_Quantity_s = prev_record['eighth_T_Quantity'] if prev_record is not None and not numpy.isnan(
                    prev_record['eighth_T_Quantity']) else 0

                New_purchase_date = 0
                new_purchase_price = 0
                Second_purchase_date = 0
                Second_purchase_price = 0
                new_purchase_price_1 = 0
                New_Sale_price = 0
                New_Sale_date = 0
                New_Sale_price_1 = 0
                Second_Sale_price = 0
                Second_Sale_date = 0
                Second_Sale_price_1 = 0
                Second_purchase_price_1 = 0
                Second_T_Quantity = 0
                P_Value = 0
                New_P_Value = 0
                # stock_data = yf.download(tickers[i], start=start, end=end)
                Total_Quantity = 0
                Final_Profit = 0
                F_S_Value = 0
                T_Quantity = 0
                New_P_Value_S = 0
                New_P_Value_B = 0
                Second_P_Value_S = 0
                Second_P_Value_B = 0
                current_price_FB = 0
                current_Price_FS = 0
                current_date = 0
                third_purchase_price = 0
                third_S_Total_Quantity = 0
                third_T_Quantity = 0
                third_P_Value_B = 0
                third_purchase_date = 0
                fourth_purchase_date = 0
                fourth_purchase_price = 0
                seventhh_Final_Profit = 0
                eighth_Final_Profit = 0

                # for tickers[i], values in ticker_data.items():stock_data = yf.download(current_ticker, start=start, end=end)
                # current_date = stock_data.index[f].strftime('%d-%m-%y')
                # current_date = date_obj.strftime('%d-%m-%y')
                try:
                    date_str = stock_data.index[f]  # Assuming the date is in string format
                    date_obj = datetime.strptime(date_str, '%d/%m/%Y')  # Corrected format
                    current_date = date_obj.strftime('%d-%m-%y')
                    current_price_FB = stock_data['Low'][f]
                    current_Price_FS = stock_data['High'][f]
                    current_LBP = stock_data['Low_LBP'][f]
                except Exception:
                    continue
                # print('current_price_FB:',current_price_FB)
                # print('current_Price_FS:',current_Price_FS)
                # print('current_LBP:',current_LBP)
                # print('current_ticker:',current_ticker)

                # current_price_FB = stock_data['Low'][f]
                # current_Price_FS = stock_data['High'][f]
                # current_LBP = data['Low_LBP'][f]
                # print(f)

                # FIRST_SALE LOOP
                # print("going to loop")
                # print('current_price_FB:',current_price_FB,type(current_price_FB))
                # print('max_look_back_period:',max_look_back_period,type(max_look_back_period))
                # print('position_1:',position_1,type(position_1))
                # print('LBP:',LBP,type(LBP))
                # print('f:',f,type(f))
                if position_1 == 1 and current_Price_FS > Sale_percentage * New_purchase_price:
                    print("Firsrt_sell_stock")
                    print('New_purchase_price:', New_purchase_price, type(New_purchase_price))
                    # Sell the stock and update the amount of money available for trading
                    position_1 = 0
                    Sell = ("Sell")
                    New_Sale_price_1 = 1.1 * New_purchase_price
                    New_Sale_price = New_Sale_price_1
                    # New_Sale_price = New_Sale_price_1.round(1)
                    # New_Sale_price = round(New_Sale_price, 1)
                    # New_Sale_price = int(New_Sale_price)
                    print('New_Sale_price:', New_Sale_price, type(New_Sale_price))

                    S_price = New_Sale_price
                    New_Sale_date = current_date
                    print('New_Sale_date:', New_Sale_date, type(New_Sale_date))
                    profit = S_price - New_purchase_price
                    Total_Quantity = Lot_size / S_price
                    T_Quantity = T_Quantity_s
                    New_P_Value_S = S_price * T_Quantity
                    Final_Profit = T_Quantity * profit
                    Final_Profit = round(Final_Profit, 1)
                    F_S_Value = S_price * T_Quantity
                    F_S_Value = round(F_S_Value, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank += New_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [New_purchase_date_s], 'Stock': [tickers[i]], 'Price': [New_purchase_price],
                         'Quantity': [T_Quantity], 'P_Value': [New_P_Value_B_s], 'S_date': [New_Sale_date],
                         'Sale_Price': [S_price], 'S_Value': [F_S_Value], 'Profit': [Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [New_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [T_Quantity_s],
                         'Price': [S_price], 'Value': [New_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, new_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s, third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s,
                          sixth_P_Value_B_s, seventh_P_Value_B_s, eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s,
                          third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s,
                          seventh_T_Quantity_s, eighth_T_Quantity_s, position_1, position_2, position_3, position_4,
                          position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # print("money_in_bank:",Money_in_Bank,type(Money_in_Bank))
                print("Buy_percentage:", Buy_percentage, type(Lot_size))

                # FIRST_BUY_LOOP
                # Check if the current low price is below the maximum look back period and a previous purchase does not exist
                if Money_in_Bank < Lot_size:
                    print("money_in_bank:", Money_in_Bank, type(Money_in_Bank))
                    print("lot_size:", Lot_size, type(Lot_size))
                    print("available money end")
                    pass

                elif position_1 == 0 and current_price_FB < Buy_percentage * LBP[f - int(max_look_back_period):f].max():
                    print("New_Buy")
                    # Buy the stock and record the purchase details
                    New_purchase_date = current_date
                    print('New_purchase_date:', New_purchase_date, type(New_purchase_date))
                    new_purchase_price_1 = current_LBP
                    new_purchase_price = new_purchase_price_1.round(1)
                    new_purchase_price = round(new_purchase_price, 1)

                    position_1 = 1
                    print('Lot_size:', Lot_size, type(Lot_size))
                    print('new_purchase_price:', new_purchase_price, type(new_purchase_price))
                    Total_Quantity = Lot_size / new_purchase_price
                    T_Quantity = int(Total_Quantity)
                    New_P_Value_B = new_purchase_price * T_Quantity
                    New_P_Value_B = round(New_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= New_P_Value_B
                    Perches = ("Buy")

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [New_purchase_date], 'Stock': [tickers[i]], 'Price': [new_purchase_price],
                         'Quantity': [T_Quantity], 'P_Value': [New_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [New_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [T_Quantity], 'Price': [new_purchase_price], 'Value': [New_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, new_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5, New_purchase_date,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B,
                          Second_P_Value_B_s, third_P_Value_B_s,
                          fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s, seventh_P_Value_B_s,
                          eighth_P_Value_B_s, T_Quantity, Second_T_Quantity_s, third_T_Quantity_s,
                          fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s, seventh_T_Quantity_s,
                          eighth_T_Quantity_s, position_1, position_2, position_3, position_4, position_5, position_6,
                          position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # SECOND_SELL_LOOP
                if position_2 == 1 and current_Price_FS > Sale_percentage * Second_purchase_price_5:
                    print("Second_sell_stock")
                    # Sell the stock and update the amount of money available for trading
                    Sell = ("Sell")
                    position_2 = 0
                    Second_Sale_price_1 = 1.1 * Second_purchase_price_5
                    Second_Sale_price = round(Second_Sale_price_1, 1)
                    Second_Sale_price = round(Second_Sale_price, 1)

                    S_price = Second_Sale_price
                    Second_Sale_date = current_date
                    Second_profit = Second_Sale_price - Second_purchase_price_5
                    S_Total_Quantity = Lot_size / Second_Sale_price
                    Second_T_Quantity = int(Second_T_Quantity_s)
                    Second_P_Value_S = Second_Sale_price * Second_T_Quantity
                    Second_Final_Profit = Second_T_Quantity * Second_profit
                    Second_Final_Profit = round(Second_Final_Profit, 1)
                    Second_S_Value = Second_Sale_price * Second_T_Quantity
                    Second_S_Value = round(Second_S_Value, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank = Money_in_Bank + Second_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [Second_purchase_date_s], 'Stock': [tickers[i]],
                         'Price': [Second_purchase_price_5],
                         'Quantity': [Second_T_Quantity], 'P_Value': [Second_P_Value_B_s],
                         'S_date': [Second_Sale_date],
                         'Sale_Price': [Second_Sale_price], 'S_Value': [Second_S_Value],
                         'Profit': [Second_Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [Second_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [Second_T_Quantity], 'Price': [Second_Sale_price],
                         'Value': [Second_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s,
                          New_P_Value_B_s, Second_P_Value_B, third_P_Value_B_s,
                          fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s, seventh_P_Value_B_s,
                          eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s, third_T_Quantity_s,
                          fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s, seventh_T_Quantity_s,
                          eighth_T_Quantity_s, position_1, position_2, position_3, position_4, position_5, position_6,
                          position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # SECOND_BUY_LOOP

                if current_date == New_purchase_date:
                    pass
                elif Money_in_Bank < Lot_size:
                    print("available money end")
                    pass
                elif position_2 == 1:
                    pass
                elif position_1 == 1 and current_price_FB < Buy_percentage * New_purchase_price:
                    print("second_Buy")
                    # Buy more of the stock and update the purchase details
                    Perches = ("Buy")
                    Second_purchase_date = current_date
                    Second_purchase_price_1 = 0.9 * New_purchase_price
                    Second_purchase_price = round(Second_purchase_price_1, 1)
                    Second_purchase_price = round(Second_purchase_price, 1)
                    position_2 = 1
                    S_Total_Quantity = Lot_size / Second_purchase_price
                    Second_T_Quantity = int(S_Total_Quantity)
                    Second_P_Value_B = Second_purchase_price * Second_T_Quantity
                    Second_P_Value_B = round(Second_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= Second_P_Value_B

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [Second_purchase_date], 'Stock': [tickers[i]],
                         'Price': [Second_purchase_price],
                         'Quantity': [Second_T_Quantity], 'P_Value': [Second_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [Second_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [Second_T_Quantity], 'Price': [Second_purchase_price],
                         'Value': [Second_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s,
                          New_P_Value_B_s, Second_P_Value_B, third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s,
                          sixth_P_Value_B_s, seventh_P_Value_B_s, eighth_P_Value_B_s,
                          T_Quantity_s, S_Total_Quantity, third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity_s,
                          sixth_T_Quantity_s, seventh_T_Quantity_s, eighth_T_Quantity_s,
                          position_1, position_2, position_3, position_4, position_5, position_6, position_7,
                          position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # THERD_SELL_LOOP
                if position_3 == 1 and current_Price_FS > Sale_percentage * third_purchase_price_5:
                    print("THERD_sell_stock")
                    # Sell the stock and update the amount of money available for trading
                    Sell = ("Sell")
                    position_3 = 0
                    third_Sale_price_1 = 1.1 * third_purchase_price_5
                    third_Sale_price = round(third_Sale_price_1, 1)
                    third = third_Sale_price
                    third_Sale_date = current_date
                    third_profit = third_Sale_price - third_purchase_price_5
                    third_S_Total_Quantity = Lot_size / third_Sale_price
                    third_T_Quantity = third_T_Quantity_s
                    third_P_Value_S = third_Sale_price * third_T_Quantity
                    third_Final_Profit = third_T_Quantity * third_profit
                    third_S_Value = third_Sale_price * third_T_Quantity
                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank = Money_in_Bank + third_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [third_purchase_date_s], 'Stock': [tickers[i]],
                         'Price': [third_purchase_price_5],
                         'Quantity': [third_T_Quantity_s], 'P_Value': [third_P_Value_B_s],
                         'S_date': [third_Sale_date],
                         'Sale_Price': [third_Sale_price], 'S_Value': [third_S_Value],
                         'Profit': [third_Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [third_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [third_T_Quantity], 'Price': [third_Sale_price],
                         'Value': [third_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s,
                          New_P_Value_B_s,
                          Second_P_Value_B_s, third_P_Value_B_s,
                          fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s, seventh_P_Value_B_s,
                          eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s, third_T_Quantity_s,
                          fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s, seventh_T_Quantity_s,
                          eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                    # THERD_BUY_LOOP
                if current_date == New_purchase_date:
                    pass
                elif Money_in_Bank < Lot_size:
                    print("available money end")
                    pass
                elif position_3 == 1:
                    pass
                elif position_2 == 1 and current_price_FB < Buy_percentage * Second_purchase_price_5:
                    print("therd_Buy")
                    # Buy more of the stock and update the purchase details
                    Perches = ("Buy")
                    third_purchase_date = current_date
                    third_purchase_price_1 = 0.9 * Second_purchase_price_5
                    third_purchase_price = round(third_purchase_price_1, 1)
                    third_purchase_price = round(third_purchase_price, 1)

                    position_3 = 1
                    third_S_Total_Quantity = Lot_size / third_purchase_price
                    S_Total_Quantity = Lot_size / third_purchase_price
                    third_T_Quantity = int(S_Total_Quantity)
                    third_P_Value_B = third_purchase_price * third_T_Quantity
                    third_P_Value_B = round(third_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= third_P_Value_B

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [third_purchase_date], 'Stock': [tickers[i]], 'Price': [third_purchase_price],
                         'Quantity': [third_T_Quantity], 'P_Value': [third_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [third_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [third_T_Quantity], 'Price': [third_purchase_price],
                         'Value': [third_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price, fourth_purchase_price_5, fifth_purchase_price_5, sixth_purchase_price_5,
                          seventh_purchase_price_5, eighth_purchase_price_5, New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s,
                          third_P_Value_B, fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s, T_Quantity_s,
                          Second_T_Quantity_s, third_T_Quantity, fourth_T_Quantity_s, fifth_T_Quantity_s,
                          sixth_T_Quantity_s, seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)
                # fourth_SELL_LOOP
                if position_4 == 1 and current_Price_FS > Sale_percentage * fourth_purchase_price_5:
                    print("fourth_sell_stock")
                    # Sell the stock and update the amount of money available for trading
                    Sell = ("Sell")
                    position_4 = 0
                    fourth_Sale_price_1 = 1.1 * fourth_purchase_price_5
                    fourth_Sale_price = round(fourth_Sale_price_1, 1)
                    fourth_Sale_price = round(fourth_Sale_price, 1)

                    fourth = fourth_Sale_price
                    fourth_Sale_date = current_date
                    fourth_profit = fourth_Sale_price - fourth_purchase_price_5
                    fourth_S_Total_Quantity = Lot_size / fourth_Sale_price
                    fourth_T_Quantity = fourth_T_Quantity_s
                    fourth_P_Value_S = fourth_Sale_price * fourth_T_Quantity
                    fourth_Final_Profit = fourth_T_Quantity * fourth_profit
                    fourth_Final_Profit = round(fourth_Final_Profit, 1)
                    fourth_S_Value = fourth_Sale_price * fourth_T_Quantity
                    fourth_S_Value = round(fourth_S_Value, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank = Money_in_Bank + fourth_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [fourth_purchase_date_s], 'Stock': [tickers[i]],
                         'Price': [fourth_purchase_price_5],
                         'Quantity': [fourth_T_Quantity_s], 'P_Value': [fourth_P_Value_B_s],
                         'S_date': [fourth_Sale_date],
                         'Sale_Price': [fourth_Sale_price], 'S_Value': [fourth_S_Value],
                         'Profit': [fourth_Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [fourth_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [third_T_Quantity_s], 'Price': [fourth_Sale_price],
                         'Value': [fourth_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s,
                          third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s,
                          third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s,
                          seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # fourth_BUY_LOOP
                if current_date == New_purchase_date:
                    pass
                elif Money_in_Bank < Lot_size:
                    print("available money end")
                    pass
                elif position_4 == 1:
                    pass
                elif position_3 == 1 and current_price_FB < Buy_percentage * third_purchase_price_5:
                    print("fourth_Buy")
                    # Buy more of the stock and update the purchase details
                    Perches = ("Buy")
                    fourth_purchase_date = current_date
                    fourth_purchase_price_1 = 0.9 * third_purchase_price_5
                    fourth_purchase_price = round(fourth_purchase_price_1, 1)
                    fourth_purchase_price = round(fourth_purchase_price, 1)

                    position_4 = 1
                    fourth_S_Total_Quantity = Lot_size / fourth_purchase_price
                    S_Total_Quantity = Lot_size / fourth_purchase_price
                    fourth_T_Quantity = int(S_Total_Quantity)
                    fourth_P_Value_B = fourth_purchase_price * fourth_T_Quantity
                    fourth_P_Value_B = round(fourth_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= fourth_P_Value_B

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [fourth_purchase_date], 'Stock': [tickers[i]],
                         'Price': [fourth_purchase_price],
                         'Quantity': [fourth_T_Quantity], 'P_Value': [fourth_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [fourth_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [fourth_T_Quantity], 'Price': [fourth_purchase_price],
                         'Value': [fourth_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price, fifth_purchase_price_5, sixth_purchase_price_5,
                          seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s, third_P_Value_B_s, fourth_P_Value_B, fifth_P_Value_B_s, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s,
                          T_Quantity_s, Second_T_Quantity_s, third_T_Quantity_s, fourth_T_Quantity, fifth_T_Quantity_s,
                          sixth_T_Quantity_s, seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # fifth_SELL_LOOP
                if position_5 == 1 and current_Price_FS > Sale_percentage * fifth_purchase_price_5:
                    print("fifth_sell_stock")
                    # Sell the stock and update the amount of money available for trading
                    Sell = ("Sell")
                    position_5 = 0
                    fifth_Sale_price_1 = 1.1 * fifth_purchase_price_5
                    fifth_Sale_price = round(fifth_Sale_price_1, 1)
                    fifth_Sale_price = round(fifth_Sale_price, 1)

                    fifth = fifth_Sale_price
                    fifth_Sale_date = current_date
                    fifth_profit = fifth_Sale_price - fifth_purchase_price_5
                    fifth_S_Total_Quantity = Lot_size / fifth_Sale_price
                    fifth_T_Quantity = fifth_T_Quantity_s
                    fifth_P_Value_S = fifth_Sale_price * fifth_T_Quantity
                    fifth_Final_Profit = fifth_T_Quantity * fifth_profit
                    fifth_Final_Profit = round(fifth_Final_Profit, 1)
                    fifth_S_Value = fifth_Sale_price * fifth_T_Quantity
                    fifth_S_Value = round(fifth_S_Value, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank = Money_in_Bank + fifth_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [fifth_purchase_date_s], 'Stock': [tickers[i]],
                         'Price': [fifth_purchase_price_5],
                         'Quantity': [fifth_T_Quantity_s], 'P_Value': [fifth_P_Value_B_s],
                         'S_date': [fifth_Sale_date],
                         'Sale_Price': [fifth_Sale_price], 'S_Value': [fifth_S_Value],
                         'Profit': [fifth_Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [fifth_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [fourth_T_Quantity_s], 'Price': [fifth_Sale_price],
                         'Value': [fifth_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s, Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s,
                          fifth_purchase_date_s, sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s,
                          New_P_Value_B_s,
                          Second_P_Value_B_s,
                          third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s,
                          third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s,
                          seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # fifth_BUY_LOOP
                if current_date == New_purchase_date:
                    pass
                elif Money_in_Bank < Lot_size:
                    print("available money end")
                    pass
                elif position_5 == 1:
                    pass
                elif position_4 == 1 and current_price_FB < Buy_percentage * fourth_purchase_price_5:
                    print("fifth_Buy")
                    # Buy more of the stock and update the purchase details
                    Perches = ("Buy")
                    fifth_purchase_date = current_date
                    fifth_purchase_price_1 = 0.9 * fourth_purchase_price_5
                    fifth_purchase_price = round(fifth_purchase_price_1, 1)
                    fifth_purchase_price = round(fifth_purchase_price, 1)

                    position_5 = 1
                    fifth_S_Total_Quantity = Lot_size / fifth_purchase_price
                    S_Total_Quantity = Lot_size / fifth_purchase_price
                    fifth_T_Quantity = int(S_Total_Quantity)
                    fifth_P_Value_B = fifth_purchase_price * fifth_T_Quantity
                    fifth_P_Value_B = round(fifth_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= fifth_P_Value_B

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [fifth_purchase_date], 'Stock': [tickers[i]],
                         'Price': [fifth_purchase_price],
                         'Quantity': [fifth_T_Quantity], 'P_Value': [fifth_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [fifth_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [fifth_T_Quantity], 'Price': [fifth_purchase_price],
                         'Value': [fifth_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price, sixth_purchase_price_5,
                          seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s, third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s,
                          T_Quantity_s, Second_T_Quantity_s, third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity,
                          sixth_T_Quantity_s, seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # sixth_SELL_LOOP
                if position_6 == 1 and current_Price_FS > Sale_percentage * sixth_purchase_price_5:
                    print("sixth_sell_stock")
                    # Sell the stock and update the amount of money available for trading
                    Sell = ("Sell")
                    position_6 = 0
                    sixth_Sale_price_1 = 1.1 * sixth_purchase_price_5
                    sixth_Sale_price = round(sixth_Sale_price_1, 1)
                    sixth_Sale_price = round(sixth_Sale_price, 1)

                    sixth = sixth_Sale_price
                    sixth_Sale_date = current_date
                    sixth_profit = sixth_Sale_price - sixth_purchase_price_5
                    sixth_S_Total_Quantity = Lot_size / sixth_Sale_price
                    sixth_T_Quantity = sixth_T_Quantity_s
                    sixth_P_Value_S = sixth_Sale_price * sixth_T_Quantity
                    sixth_Final_Profit = sixth_T_Quantity * sixth_profit
                    sixth_Final_Profit = round(sixth_Final_Profit, 1)
                    sixth_S_Value = sixth_Sale_price * sixth_T_Quantity
                    sixth_S_Value = round(sixth_S_Value, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank = Money_in_Bank + fourth_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [sixth_purchase_date_s], 'Stock': [tickers[i]],
                         'Price': [sixth_purchase_price_5],
                         'Quantity': [sixth_T_Quantity_s], 'P_Value': [sixth_P_Value_B_s],
                         'S_date': [sixth_Sale_date],
                         'Sale_Price': [sixth_Sale_price], 'S_Value': [sixth_S_Value],
                         'Profit': [sixth_Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [sixth_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [sixth_T_Quantity_s], 'Price': [sixth_Sale_price],
                         'Value': [sixth_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s,
                          third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s,
                          third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s,
                          seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # sixth_BUY_LOOP
                if current_date == New_purchase_date:
                    pass
                elif Money_in_Bank < Lot_size:
                    print("available money end")
                    pass
                elif position_6 == 1:
                    pass
                elif position_5 == 1 and current_price_FB < Buy_percentage * fifth_purchase_price_5:
                    print("sixth_Buy")
                    # Buy more of the stock and update the purchase details
                    Perches = ("Buy")
                    sixth_purchase_date = current_date
                    sixth_purchase_price_1 = 0.9 * fifth_purchase_price_5
                    sixth_purchase_price = round(sixth_purchase_price_1, 1)
                    sixth_purchase_price = round(sixth_purchase_price, 1)

                    position_6 = 1
                    sixth_S_Total_Quantity = Lot_size / sixth_purchase_price
                    S_Total_Quantity = Lot_size / sixth_purchase_price
                    sixth_T_Quantity = int(S_Total_Quantity)
                    sixth_P_Value_B = sixth_purchase_price * sixth_T_Quantity
                    sixth_P_Value_B = round(sixth_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= sixth_P_Value_B

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [sixth_purchase_date], 'Stock': [tickers[i]],
                         'Price': [sixth_purchase_price],
                         'Quantity': [sixth_T_Quantity], 'P_Value': [sixth_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [sixth_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [sixth_T_Quantity], 'Price': [sixth_purchase_price],
                         'Value': [sixth_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5, sixth_purchase_price,
                          seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s, third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B,
                          seventh_P_Value_B_s, eighth_P_Value_B_s,
                          T_Quantity_s, Second_T_Quantity_s, third_T_Quantity_s, fourth_T_Quantity_s,
                          fifth_T_Quantity_s, sixth_T_Quantity, seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # seventh_SELL_LOOP
                if position_7 == 1 and current_Price_FS > Sale_percentage * seventh_purchase_price_5:
                    print("seventh_sell_stock")
                    # Sell the stock and update the amount of money available for trading
                    Sell = ("Sell")
                    position_7 = 0
                    seventh_Sale_price_1 = 1.1 * seventh_purchase_price_5
                    seventh_Sale_price = round(seventh_Sale_price_1, 1)
                    seventh_Sale_price = round(seventh_Sale_price, 1)

                    seventh = seventh_Sale_price
                    seventh_Sale_date = current_date
                    seventh_profit = seventh_Sale_price - seventh_purchase_price_5
                    seventh_S_Total_Quantity = Lot_size / seventh_Sale_price
                    seventh_T_Quantity = seventh_T_Quantity_s
                    seventh_P_Value_S = seventh_Sale_price * seventh_T_Quantity
                    seventh_Final_Profit = seventh_T_Quantity * seventh_profit
                    seventh_Final_Profit = round(seventhh_Final_Profit, 1)
                    seventh_S_Value = seventh_Sale_price * seventh_T_Quantity
                    seventh_S_Value = round(seventh_S_Value, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank = Money_in_Bank + seventh_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [seventh_purchase_date_s], 'Stock': [tickers[i]],
                         'Price': [seventh_purchase_price_5],
                         'Quantity': [seventh_T_Quantity_s], 'P_Value': [seventh_P_Value_B_s],
                         'S_date': [seventh_Sale_date],
                         'Sale_Price': [seventh_Sale_price], 'S_Value': [seventh_S_Value],
                         'Profit': [seventh_Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [seventh_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [seventh_T_Quantity_s], 'Price': [seventh_Sale_price],
                         'Value': [seventh_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s,
                          third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s,
                          third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s,
                          seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # seventh_BUY_LOOP
                if current_date == New_purchase_date:
                    pass
                elif Money_in_Bank < Lot_size:
                    print("available money end")
                    pass
                elif position_7 == 1:
                    pass
                elif position_6 == 1 and current_price_FB < Buy_percentage * sixth_purchase_price_5:
                    print("seventh_Buy")
                    # Buy more of the stock and update the purchase details
                    Perches = ("Buy")
                    seventh_purchase_date = current_date
                    seventh_purchase_price_1 = 0.9 * sixth_purchase_price_5
                    seventh_purchase_price = round(seventh_purchase_price_1, 1)
                    seventh_purchase_price = round(seventh_purchase_price, 1)

                    position_7 = 1
                    seventh_S_Total_Quantity = Lot_size / seventh_purchase_price
                    S_Total_Quantity = Lot_size / seventh_purchase_price
                    seventh_T_Quantity = int(S_Total_Quantity)
                    seventh_P_Value_B = seventh_purchase_price * seventh_T_Quantity
                    seventh_P_Value_B = round(sixth_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= seventh_P_Value_B

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [seventh_purchase_date], 'Stock': [tickers[i]],
                         'Price': [seventh_purchase_price],
                         'Quantity': [seventh_T_Quantity], 'P_Value': [seventh_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [seventh_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [seventh_T_Quantity], 'Price': [seventh_purchase_price],
                         'Value': [seventh_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s, third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s,
                          sixth_P_Value_B_s, seventh_P_Value_B, eighth_P_Value_B_s,
                          T_Quantity_s, Second_T_Quantity_s, third_T_Quantity_s, fourth_T_Quantity_s,
                          fifth_T_Quantity_s, sixth_T_Quantity_s, seventh_T_Quantity, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # eighth_SELL_LOOP
                if position_8 == 1 and current_Price_FS > Sale_percentage * eighth_purchase_price_5:
                    print("eighth_sell_stock")
                    # Sell the stock and update the amount of money available for trading
                    Sell = ("Sell")
                    position_8 = 0
                    eighth_Sale_price_1 = 1.1 * eighth_purchase_price_5
                    eighth_Sale_price = round(eighth_Sale_price_1, 1)
                    eighth_Sale_price = round(eighth_Sale_price, 1)

                    eighth = eighth_Sale_price
                    eighth_Sale_date = current_date
                    eighth_profit = eighth_Sale_price - eighth_purchase_price_5
                    eighth_S_Total_Quantity = Lot_size / eighth_Sale_price
                    eighth_T_Quantity = eighth_T_Quantity_s
                    eighth_P_Value_S = eighth_Sale_price * eighth_T_Quantity
                    eighth_Final_Profit = eighth_T_Quantity * eighth_profit
                    eighth_Final_Profit = round(eighth_Final_Profit, 1)
                    eighth_S_Value = eighth_Sale_price * eighth_T_Quantity
                    eighth_S_Value = round(eighth_S_Value, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank = Money_in_Bank + eighth_P_Value_S

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [eighth_purchase_date_s], 'Stock': [tickers[i]],
                         'Price': [eighth_purchase_price_5],
                         'Quantity': [eighth_T_Quantity_s], 'P_Value': [eighth_P_Value_B_s],
                         'S_date': [eighth_Sale_date],
                         'Sale_Price': [eighth_Sale_price], 'S_Value': [eighth_S_Value],
                         'Profit': [eighth_Final_Profit]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [eighth_Sale_date], 'Stock': [tickers[i]], 'Perches/Sell': [Sell],
                         'Quantity': [eighth_T_Quantity_s], 'Price': [eighth_Sale_price],
                         'Value': [eighth_P_Value_S], 'Opening': [Money_in_Bank_1],
                         'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price_5,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date_s, New_P_Value_B_s,
                          Second_P_Value_B_s,
                          third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s, sixth_P_Value_B_s,
                          seventh_P_Value_B_s, eighth_P_Value_B_s, T_Quantity_s, Second_T_Quantity_s,
                          third_T_Quantity_s, fourth_T_Quantity_s, fifth_T_Quantity_s, sixth_T_Quantity_s,
                          seventh_T_Quantity_s, eighth_T_Quantity_s, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # eighth_BUY_LOOP
                if current_date == New_purchase_date:
                    pass
                elif Money_in_Bank < Lot_size:
                    print("available money end")
                    pass
                elif position_8 == 1:
                    pass
                elif position_7 == 1 and current_price_FB < Buy_percentage * seventh_purchase_price_5:
                    print("eighth_Buy")
                    # Buy more of the stock and update the purchase details
                    Perches = ("Buy")
                    eighth_purchase_date = current_date
                    eighth_purchase_price_1 = 0.9 * seventh_purchase_price_5
                    eighth_purchase_price = round(eighth_purchase_price_1, 1)
                    eighth_purchase_price = round(eighth_purchase_price, 1)

                    position_8 = 1
                    eighth_S_Total_Quantity = Lot_size / eighth_purchase_price
                    S_Total_Quantity = Lot_size / eighth_purchase_price
                    eighth_T_Quantity = int(S_Total_Quantity)
                    eighth_P_Value_B = eighth_purchase_price * eighth_T_Quantity
                    eighth_P_Value_B = round(eighth_P_Value_B, 1)

                    Money_in_Bank_1 = Money_in_Bank
                    Money_in_Bank -= eighth_P_Value_B

                    new_transaction_1 = pd.DataFrame(
                        {'Date': [eighth_purchase_date], 'Stock': [tickers[i]],
                         'Price': [eighth_purchase_price],
                         'Quantity': [eighth_T_Quantity], 'P_Value': [eighth_P_Value_B]})
                    trans_1 = pd.concat([trans_1, new_transaction_1], ignore_index=True)

                    new_transaction_2 = pd.DataFrame(
                        {'Date': [eighth_purchase_date], 'Stock': [tickers[i]], 'Perches/Sell': [Perches],
                         'Quantity': [eighth_T_Quantity], 'Price': [eighth_purchase_price],
                         'Value': [eighth_P_Value_B],
                         'Opening': [Money_in_Bank_1], 'Closing': [Money_in_Bank]})
                    trans_2 = pd.concat([trans_2, new_transaction_2], ignore_index=True)
                    master_df = pd.concat([master_df, pd.DataFrame(
                        [[current_date, current_ticker, New_purchase_price, Second_purchase_price_5,
                          third_purchase_price_5, fourth_purchase_price_5, fifth_purchase_price_5,
                          sixth_purchase_price_5, seventh_purchase_price_5, eighth_purchase_price,
                          New_purchase_date_s,
                          Second_purchase_date_s, third_purchase_date_s, fourth_purchase_date_s, fifth_purchase_date_s,
                          sixth_purchase_date_s, seventh_purchase_date_s, eighth_purchase_date, New_P_Value_B_s,
                          Second_P_Value_B_s, third_P_Value_B_s, fourth_P_Value_B_s, fifth_P_Value_B_s,
                          sixth_P_Value_B_s, seventh_P_Value_B_s, eighth_P_Value_B,
                          T_Quantity_s, Second_T_Quantity_s, third_T_Quantity_s, fourth_T_Quantity_s,
                          fifth_T_Quantity_s, sixth_T_Quantity_s, seventh_T_Quantity_s, eighth_T_Quantity, position_1,
                          position_2, position_3, position_4, position_5, position_6, position_7, position_8]],
                        columns=['date', 'ticker', 'new_purchase_price', 'Second_purchase_price',
                                 'third_purchase_price',
                                 'fourth_purchase_price', 'fifth_purchase_price', 'sixth_purchase_price',
                                 'seventh_purchase_price', 'eighth_purchase_price',
                                 'New_purchase_date', 'Second_purchase_date', 'third_purchase_date',
                                 'fourth_purchase_date', 'fifth_purchase_date', 'sixth_purchase_date',
                                 'seventh_purchase_date', 'eighth_purchase_date',
                                 'New_P_Value_B', 'Second_P_Value_B', 'third_P_Value_B', 'fourth_P_Value_B',
                                 'fifth_P_Value_B', 'sixth_P_Value_B', 'seventh_P_Value_B', 'eighth_P_Value_B',
                                 'T_Quantity', 'Second_T_Quantity', 'third_T_Quantity', 'fourth_T_Quantity',
                                 'fifth_T_Quantity', 'sixth_T_Quantity', 'seventh_T_Quantity', 'eighth_T_Quantity',
                                 'position_1', 'position_2', 'position_3', 'position_4', 'position_5', 'position_6',
                                 'position_7', 'position_8'])],
                                          ignore_index=True)

                # print("out_of_loop")

            trans_1.drop_duplicates(subset="Price", keep='last', inplace=True)
            print(trans_1)
            print(trans_2)
            for ticker in tickers:
                with pd.ExcelWriter('TRADE_BOOK.xlsx', engine='openpyxl') as writer:
                    trans_1.to_excel(writer, sheet_name='TRADE_BOOK', index=False)
                    trans_2.to_excel(writer, sheet_name='TRANSACTION_REPORT', index=False)
                    # for date, ticker_data in dfs.items():
        for ticker, df2 in ticker_data.items():
            sheet_name = ticker  # Combine date and ticker symbol for the sheet name
            df1.to_excel(writer, sheet_name=sheet_name)

            # df2.to_excel(writer, sheet_name=ticker)
            # writer.save()

            # print(trans_1)
            # print(trans_2)
            # print(Money_in_Bank)
        excel_file = open('TRADE_BOOK.xlsx', 'rb')

        return FileResponse(excel_file,filename='TRADE_BOOK.xlsx')
        return Response({'message': 'success'})
