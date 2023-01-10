import datetime
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from xhtml2pdf import pisa

from .models import TranSum, MemberMaster, CustomerMaster, MOS_Sales
from rest_framework import generics
from rest_framework import status
from django.db.models import Sum, Q, F, Avg
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework import viewsets
from .serializers import (SavePurchSerializer, RetTransSumSerializer,
                          SaveMemberSerializer, RetMemberSerializer, SavecustomerSerializer,
                          RetChangeDefaultSerializer, CustomerLoginSerializer, TranSumRetrivesc2Serializer,
                          SavePurchSerializer1)
from . import serializers
from django.core import serializers as dj_serializers
import copy
from django.contrib.auth import authenticate
from .renderers import UserRender
from django.db import transaction
from django.db.models import Sum
import decimal
from . import services
from django.template.loader import render_to_string
import locale


# <-------------------- SavePurch API ---------------------->
class SavePurch(APIView):
    def post(self, request, format=None):
        try:
            save = TranSum.objects.filter(sno=request.data['sno']).latest('scriptSno')
            print("Primry--->", save)
        except:
            save = 0
        try:
            sno1 = save.sno
        except:
            sno1 = 0

        print("Serial no", sno1)
        if sno1 == 0 or None:
            s = sno1 + 1
        else:
            s = sno1 + 1
            # print("ssss",s)
        request.data['sno'] = s
        print("requ code", request.data.get("sno"))

        dic = copy.deepcopy(request.data)
        dic["balQty"] = request.data["qty"]

        serializer = SavePurchSerializer(data=dic)
        if serializer.is_valid():
            serializer.save()
            print("Saving Records---->", serializer.data)

            return Response({'status': True, 'msg': 'You have successfully Created', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavePrimaryAPI(APIView):
    def post(self, request, format=None):
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        againstType = self.request.query_params.get('againstType')
        part = self.request.query_params.get('part')
        dfy = self.request.query_params.get('dfy')
        sp = self.request.query_params.get('sp')

        # primary=TranSum.objects.filter(group=group,code=code,againstType=againstType,fy=dfy,part=part,sp=sp).latest('sno')
        # primary1=TranSum.objects.filter(group=group,code=code,againstType=againstType,fy=dfy,part=part,sp=sp).aggregate(total_balQty=Sum('balQty'),holding_Val=Sum(F('rate') * F('balQty')))
        primary = TranSum.objects.latest('sno')
        # print("Primry--->",primary1)

        sno1 = primary.sno
        if sno1 == 0 or None:
            s = sno1 + 1
        else:
            s = sno1 + 1
        request.data['sno'] = s
        scriptno = TranSum.objects.update(scriptSno=s)
        # print("requ code",request.data.get("sno"))
        serializer = SavePurchSerializer1(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # print("Primary Records---->",serializer.data)
            return Response({'status': True, 'msg': 'You have successfully Created', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetPrimaryAPI(APIView):
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        againstType = self.request.query_params.get('againstType')
        dfy = self.request.query_params.get('dfy')
        part = self.request.query_params.get('part')
        # sp = self.request.query_params.get('sp')
        # primary=TranSum.objects.filter(group=group,code=code,againstType=againstType,fy=dfy,part=part).annotate(total_balQty=Sum('balQty')).annotate(holding_val=Sum(F('rate') * F('balQty'))).annotate(average_rate=(F('holding_val')/F('total_balQty')))

        primary = TranSum.objects.filter(group=group, code=code, againstType=againstType, fy=dfy, part=part).aggregate(
            total_balQty=Sum('balQty'), holding_Val=Sum(F('rate') * F('balQty')))
        primary1 = TranSum.objects.values('isinCode', 'fmr').filter(group=group, code=code, againstType=againstType,
                                                                    fy=dfy, part=part)

        bal_qty = 0 if primary['total_balQty'] is None else primary['total_balQty']
        hold_val1 = 0 if primary['holding_Val'] is None else primary['holding_Val']

        hold_val = hold_val1
        bal_Qt = bal_qty
        avg_rate = round(hold_val / bal_Qt)
        print("Hold val", hold_val)
        print("avg_rate ", avg_rate)
        print("bal_Qt ", bal_Qt)
        primary2 = TranSum.objects.filter(group=group, code=code, againstType=againstType, fy=dfy, part=part)
        # primary2.patch(balQty=bal_Qt)

        primary_ls = {
            'isinCode': primary1[0]['isinCode'],
            'fmr': primary1[0]['fmr'],

            'avg_rate': avg_rate,
            'holdVal': primary['holding_Val'],
            'balQty': primary['total_balQty'],
            # 'avgRate':round(primary['holding_Val'] / primary['total_balQty'],2)
        }
        return Response({'status': True, 'msg': 'done', 'data': primary_ls})


# <--------------------RetTransSum API --------------------->
class RetTransSum(generics.ListAPIView):
    queryset = TranSum.objects.all()
    serializer_class = RetTransSumSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group', 'code', 'againstType', 'part']

    # <-------------------- Overriding Queryset --------------->
    def get_queryset(self):
        option = self.request.query_params.get('option')
        dfy = self.request.query_params.get('dfy')
        try:
            start_fy = f"{dfy[:4]}-04-01"
            end_fy = f"{dfy[5:]}-03-31"
        except:
            raise Http404

        if option == 'O':

            return self.queryset.filter(trDate__lt=start_fy)

        elif option == 'A':

            return self.queryset.filter(trDate__range=(start_fy, end_fy))


# <------------------------- Update and Retrive API ------------------->
class RetTransSumUpdate(generics.RetrieveUpdateAPIView):
    queryset = TranSum.objects.all()
    serializer_class = RetTransSumSerializer

    def update(self, request, *args, **kwargs):
        oldqty = self.request.query_params.get('oldqty')
        balqty = self.request.query_params.get('balqty')

        old = 0 if oldqty is None else oldqty
        balQ = 0 if balqty is None else balqty

        dict_ls = copy.deepcopy(request.data)
        print(dict_ls)
        dict_ls["balQty"] = int(balQ) - int(old) + int((dict_ls["qty"]))

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=dict_ls, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        result = {
            "status": True,
            "msg": "Data successfully updated",
            "data": dict_ls

        }
        return Response(result)


# <-------------------------- Retrive API Screen No Two ------------->

class RetScriptSum(APIView):
    def get(self, request, format=None):
        # ------------ fetching parameter in  Url
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        againstType = self.request.query_params.get('againstType')
        part = self.request.query_params.get('part')
        dfy = self.request.query_params.get('dfy')
        try:
            start_fy = f"{dfy[:4]}-04-01"
            end_fy = f"{dfy[5:]}-03-31"
        except:
            raise Http404
        # --------------------- Opening
        opening = TranSum.objects.values('qty', 'sVal', 'marketRate', 'marketValue', 'isinCode', 'fmr',
                                         'avgRate').order_by().filter(trDate__lt=start_fy, group=group, code=code,
                                                                      againstType=againstType, part=part).aggregate(
            opening_sum=Sum("qty"), opening_values=Sum("sVal"))
        # print("Opening1--->",opening,type(opening))
        addition = TranSum.objects.values('qty', 'sVal', 'marketRate', 'marketValue', 'isinCode', 'fmr',
                                          'avgRate').order_by().filter(trDate__range=(start_fy, end_fy), group=group,
                                                                       code=code, againstType=againstType,
                                                                       part=part).aggregate(addition_sum=Sum("qty"),
                                                                                            addition_values=Sum("sVal"))
        # print("Addition1--->",addition)

        opening_su = 0 if opening['opening_sum'] is None else opening['opening_sum']
        addition_su = 0 if addition['addition_sum'] is None else addition['addition_sum']
        opening_val = 0 if opening['opening_values'] is None else opening['opening_values']
        addition_val = 0 if addition['addition_values'] is None else addition['addition_values']

        context = {
            "opening": opening_su,
            "addition": addition_su,
            "sales": 0,
            "closing": opening_su + addition_su,
            "invVal": opening_val + addition_val,
            "avgRate": round((opening_val + addition_val) / (opening_su + addition_su), 2),
        }
        open_add = TranSum.objects.filter(group=group, code=code, part=part)
        serializer = TranSumRetrivesc2Serializer(open_add)
        return Response({'status': True, 'msg': 'done', 'data1': serializer.data, 'data': context})


class RetHolding(APIView):
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        dfy = self.request.query_params.get('dfy')
        againstType = self.request.query_params.get('againstType')

        holding = TranSum.objects.filter(group=group, code=code, againstType=againstType).values(
            'part').order_by().annotate(total_balQty=Sum('balQty')).annotate(
            invVal=Sum(F('rate') * F('balQty'))).annotate(mktVal=Sum(F('balQty') * F('marketRate')))
        # print("Ballllllll--->",holding)

        ls = []
        for data in holding:
            data_ls = {'part': data['part'], 'holdQty': int(data['total_balQty']), 'invValue': float(data['invVal']),
                       'mktVal': float(data['mktVal'])}
            ls.append(data_ls)
        return Response({'status': True, 'msg': 'done', 'data': ls})


# <-------------------------- SaveMember api ----------------------->
class SaveMember(APIView):
    def post(self, request, format=None):
        try:
            mem = MemberMaster.objects.filter(group=request.data['group']).latest('code')
        except Exception:
            mem = '00000'
        # print("Member-->",mem)
        if mem == None or 0:
            me = mem + 1
            code = me.zfill(5)
        else:
            cp = mem
            cpp = str(cp)
            cpp = int(cpp) + 1
            code = str(cpp).zfill(5)
        request.data['code'] = code

        # print("Code --->",code)
        # print("requ code",request.data.get("code"))

        serializer = SaveMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True, 'Message': 'You have successfully Created', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <-------------------------- RetMember API -------------------->
class RetMember(APIView):
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        member = MemberMaster.objects.filter(group=group)
        serializer = RetMemberSerializer(member, many=True)
        return Response({'status': True, 'msg': 'done', 'data': serializer.data})


# <---------------------------- updated delete api mrmber ----------------->
class MemberUpdadeDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = MemberMaster.objects.all()
    serializer_class = SaveMemberSerializer


# <-------------------------- SaveCutomer api ---------------------------->
class SaveCustomer(APIView):
    def post(self, request, format=None):
        gro = CustomerMaster.objects.latest('group')
        if gro == None or 0:
            ss = gro + 1
            group = ss.zfill(5)
        else:
            gp = gro
            gpp = str(gp)
            gpp = int(gpp) + 1
            group = str(gpp).zfill(5)
        # print("groupp",group)

        request.data['group'] = group
        # print("requ grp",request.data.get("group"))
        serializer = SavecustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True, 'msg': 'You have successfully Created', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <---------------- RetCustomer API -------------------->
class RetCustomer(APIView):
    def get(self, request, format=None):
        username = self.request.query_params.get('username')
        customer = CustomerMaster.objects.filter(username=username)
        serializer = SavecustomerSerializer(customer, many=True)
        return Response({'status': True, 'msg': 'done', 'data': serializer.data})


# <------------ updated delete api Customer ---------------->
class CustomerUpdadeDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerMaster.objects.all()
    serializer_class = SavecustomerSerializer


# < --------------- Login Customer Master Api ---------------->

class CustomerLogin(APIView):
    def post(self, request, format=None):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            password = serializer.data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                return Response({'status': True, 'msg': 'Login Success', 'data': serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'status': False, 'msg': 'Username or Password is not Valid', 'data': ' '})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <----------------- RetChangeDefault ----------------->
class RetChangeDefault(APIView):
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        member = MemberMaster.objects.filter(group=group)
        serializer = RetChangeDefaultSerializer(member, many=True)
        return Response({'status': True, 'msg': 'done', 'data': serializer.data})


class TranSumViewSet(viewsets.ViewSet):

    def list(self, request):
        data = request.query_params.dict()
        data.pop('sp')
        data.pop('dfy')
        queryset = TranSum.objects.filter(**data)
        sp = request.query_params.get('sp')
        dfy = request.query_params.get('dfy')
        try:
            start_fy = f"{dfy[:4]}-04-01"
            end_fy = f"{dfy[5:]}-03-31"
        except:
            raise Http404

        if sp == 'O':
            queryset = queryset.filter(trDate__lt=start_fy)
        # data = request.query_params.dict()
        elif sp == 'A':
            queryset = queryset.filter(trDate__range=(start_fy, end_fy))

        # queryset = TranSum.objects.filter(**data)
        serializer = serializers.RetrieveTranSumSerializer(queryset, many=True)
        purchase_data = serializer.data
        # for i in range(0, len(purchase_data)):
        #     sales = MOS_Sales.objects.filter(group=purchase_data[i]['group'], code=purchase_data[i]['code'],
        #                                      purSno=purchase_data[i]['sno'], scriptSno=purchase_data[i]['scriptSno'])
        #     serializer = serializers.SaleSerializer(sales, many=True)
        #     purchase_data[i]['sales'] = serializer.data

        return Response({"status": True, "message": "Retrieved Purchases", "data": purchase_data})

    @transaction.atomic
    def create(self, request):
        data = request.data
        serializer = serializers.TranSumSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        object = serializer.save()
        updated_object = TranSum.purchase_objects.filter(pk=object.pk).first()
        serializer = serializers.RetrieveTranSumSerializer(updated_object)
        response = {"status": True, "message": "Purchase Record Added", "data": serializer.data}
        return Response(response)

    @transaction.atomic
    def update(self, request, pk):
        data = request.data
        purchase_record = TranSum.purchase_objects.filter(group=data['group']).filter(code=data['code']).filter(
            pk=pk).first()
        if purchase_record:
            serializer = serializers.TranSumSerializer(purchase_record, data=data)
            serializer.is_valid()
            purchase_record = serializer.save()
            serializer = serializers.RetrieveTranSumSerializer(purchase_record)
            response = {"status": True, "message": "Purchase Record Updated", "data": serializer.data}
            return Response(response)
        return Response({"status": False, "message": "Purchase record does not exist"})


class SalesViewSet(viewsets.ViewSet):

    def list(self, request):
        data = request.query_params.dict()
        data['fy'] = data['dfy']
        data.pop('dfy')
        queryset = TranSum.purchase_objects.filter(**data)
        dfy = request.query_params.get('dfy')
        againstType = request.query_params.get('againstType')
        try:
            start_fy = f"{dfy[:4]}-04-01"
            end_fy = f"{dfy[5:]}-03-31"
        except:
            raise Http404

        serializer = serializers.SalePurchaseSerializer(queryset, many=True)
        purchase_data = serializer.data
        for i in range(0, len(purchase_data)):
            sales = MOS_Sales.objects.filter(group=purchase_data[i]['group'], code=purchase_data[i]['code'],
                                             purSno=purchase_data[i]['sno'], scriptSno=purchase_data[i]['scriptSno'],
                                             againstType=againstType)
            totalSoldQty = list(sales.aggregate(Sum('sqty')).values())[0]
            stcg = list(sales.aggregate(Sum('stcg')).values())[0]
            ltcg = list(sales.aggregate(Sum('ltcg')).values())[0]
            purchase_data[i]['totalSoldQty'] = totalSoldQty
            purchase_data[i]['stcg'] = stcg
            purchase_data[i]['ltcg'] = ltcg
            serializer = serializers.SaleSerializer(sales, many=True)
            purchase_data[i]['sales'] = serializer.data

        # queryset = TranSum.objects.filter(**data)
        return Response({"status": True, "message": "Retrieved Sales", "data": purchase_data})

    @transaction.atomic
    def create(self, request):
        data = request.data.copy()
        purchase_record = TranSum.purchase_objects.get(pk=data['pur_trId'])
        data.pop('pur_trId')
        if purchase_record:
            data['purSno'] = purchase_record.sno
            data['scriptSno'] = purchase_record.scriptSno
            serializer = serializers.SaleSerializer(data=data)
            serializer.is_valid()
            serializer.save()
            response = {"status": True, "message": "Sales Record Created", "data": serializer.data}
            return Response(response)

    @transaction.atomic
    def update(self, request, pk):
        data = request.data.copy()
        purchase_record = TranSum.purchase_objects.get(pk=data['pur_trId'])
        sales_record = MOS_Sales.objects.get(pk=pk)
        data.pop('pur_trId')
        if purchase_record:
            data['trId'] = pk
            data['purSno'] = purchase_record.sno
            data['scriptSno'] = purchase_record.scriptSno
            serializer = serializers.SaleSerializer(sales_record, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = {"status": True, "message": "Sales Record Updated", "data": serializer.data}
            return Response(response)


@api_view(['GET'])
def get_holdings_for_member(request):
    group = request.query_params.get('group')
    code = request.query_params.get('code')
    dfy = request.query_params.get('dfy')
    years = dfy.split("-")
    from_date = years[0] + "-04-01"
    to_date = years[1] + "-03-31"
    againstType = request.query_params.get('againstType')

    # holding = TranSum.objects.filter(group=group, code=code, againstType=againstType).values(
    #     'part').order_by().annotate(total_balQty=Sum('balQty')).annotate(
    #     invVal=Sum(F('rate') * F('balQty'))).annotate(mktVal=Sum(F('balQty') * F('marketRate')))
    # print("Ballllllll--->",holding)
    holdings = []

    masters = TranSum.master_objects.filter(group=group, code=code, againstType=againstType)
    for master in masters.values():
        holding = {
            "part": master['part'],
            "balQty": int(master['balQty']),
            "HoldingValue": master['HoldingValue'],
            "marketValue": master['marketValue'],
            "isinCode": master['isinCode'],
            "fmr": master['fmr'],
            "marketRate": master['marketRate'],
            "avgRate": master['avgRate']
        }
        purchases = TranSum.purchase_objects.filter(group=group, code=code, againstType=againstType,
                                                    scriptSno=master['sno'], part=master['part'])
        openings = purchases.filter(trDate__lt=from_date)
        sum_opening = list(openings.aggregate(Sum('qty')).values())[0]
        additions = purchases.filter(trDate__range=(from_date, to_date))
        sum_addition = list(additions.aggregate(Sum('qty')).values())[0]
        sales = MOS_Sales.objects.filter(group=group, code=code, scriptSno=master['sno'], againstType=againstType)
        sum_sales = list(sales.aggregate(Sum('sqty')).values())[0]

        holding['profitLoss'] = Decimal(master['marketValue']) - master['HoldingValue']
        holding['opening'] = 0 if sum_opening is None else int(sum_opening)
        holding['addition'] = 0 if sum_addition is None else int(sum_addition)
        holding['sales'] = 0 if sum_sales is None else int(sum_sales)
        holding['closing'] = holding['opening'] + holding['addition'] - holding['sales']
        holding['stcg'] = list(sales.aggregate(Sum('stcg')).values())[0]
        holding['ltcg'] = list(sales.aggregate(Sum('ltcg')).values())[0]
        holdings.append(holding)

    return Response({'status': True, 'message': 'Retrieved Holdings', 'data': holdings})


@api_view(['GET'])
def member_capital_gain(request):
    group = request.query_params.get('group')
    code = request.query_params.get('code')
    dfy = request.query_params.get('dfy')
    againstType = request.query_params.get('againstType')
    sales = MOS_Sales.objects.filter(group=group, code=code, fy=dfy, againstType=againstType)
    sum_stcg = list(sales.aggregate(Sum('stcg')).values())[0]
    sum_ltcg = list(sales.aggregate(Sum('ltcg')).values())[0]
    sum_speculation = list(sales.aggregate(Sum('speculation')).values())[0]
    result = {"group": group, "code": code, "fy": dfy, "stcg": sum_stcg, "ltcg": sum_ltcg,
              "speculation": sum_speculation}

    return Response({"status": True, "message": "Retrieved Total Capital Gains", "data": result})


@api_view(['GET'])
def get_market_rate(request):
    request_dict = request.query_params.dict()
    request_dict['fy'] = request_dict['dfy']
    request_dict.pop('dfy')
    if 'sp' in request_dict:
        request_dict.pop('sp')

    masters = TranSum.master_objects.filter(**request_dict)
    for master in masters:
        market_rate = services.get_market_rate(master.part)
        if market_rate:
            market_rate = market_rate['Adj Close']
            master.marketRate = market_rate
            master.marketValue = Decimal(market_rate) * master.balQty
            super(TranSum, master).save()
            purchases = TranSum.purchase_objects.filter(group=request_dict['group'], code=request_dict['code'],
                                                        fy=request_dict['fy'],
                                                        scriptSno=master.sno,
                                                        part=master.part)
            for purchase in purchases:
                purchase.marketRate = market_rate
                purchase.marketValue = Decimal(market_rate) * purchase.balQty
                super(TranSum, purchase).save()

    if request.query_params.get('sp') and request.query_params.get('part'):
        temp_request = request.query_params.dict()
        temp_request['sp'] = request.query_params.get('sp')
        temp_request['dfy'] = request.query_params.get('dfy')
        data = prepare_purchases_response(temp_request)
    else:
        temp_request = request.query_params.dict()
        temp_request['againstType'] = temp_request['againstType'] if 'againstType' in temp_request else "Shares"
        data = prepare_holdings_response(temp_request)

    return Response({"status": True, "message": "Retrieved Market Rates", "data": data})


def sum_by_key(records, key):
    sum_result = 0
    for record in records:
        sum_result = sum_result + getattr(record, key)
    return sum_result


def sum_by_key(records: dict[str], key):
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    sum_result = Decimal(0)
    for record in records:
        sum_result = sum_result + Decimal(locale.atof(record[key]))
    return sum_result


def prepare_purchases_response(request):
    data = request.copy()
    data.pop('sp')
    data.pop('dfy')
    queryset = TranSum.objects.filter(**data)
    sp = request['sp']
    dfy = request['dfy']
    try:
        start_fy = f"{dfy[:4]}-04-01"
        end_fy = f"{dfy[5:]}-03-31"
    except:
        raise Http404

    if sp == 'O':
        queryset = queryset.filter(trDate__lt=start_fy)
    # data = request.query_params.dict()
    elif sp == 'A':
        queryset = queryset.filter(trDate__range=(start_fy, end_fy))

    # queryset = TranSum.objects.filter(**data)
    serializer = serializers.RetrieveTranSumSerializer(queryset, many=True)
    purchase_data = serializer.data
    return purchase_data


def prepare_holdings_response(request):
    group = request['group']
    code = request['code']
    dfy = request['dfy']
    years = dfy.split("-")
    from_date = years[0] + "-04-01"
    to_date = years[1] + "-03-31"
    againstType = request['againstType']

    # holding = TranSum.objects.filter(group=group, code=code, againstType=againstType).values(
    #     'part').order_by().annotate(total_balQty=Sum('balQty')).annotate(
    #     invVal=Sum(F('rate') * F('balQty'))).annotate(mktVal=Sum(F('balQty') * F('marketRate')))
    # print("Ballllllll--->",holding)
    holdings = []
    masters = TranSum.master_objects.filter(group=group, code=code, againstType=againstType)
    for master in masters.values():
        holding = {
            "part": master['part'],
            "balQty": int(master['balQty']),
            "HoldingValue": master['HoldingValue'],
            "marketValue": master['marketValue'],
            "isinCode": master['isinCode'],
            "fmr": master['fmr'],
            "marketRate": master['marketRate'],
            "avgRate": master['avgRate']
        }
        purchases = TranSum.purchase_objects.filter(group=group, code=code, againstType=againstType,
                                                    scriptSno=master['sno'], part=master['part'])
        openings = purchases.filter(trDate__lt=from_date)
        sum_opening = list(openings.aggregate(Sum('balQty')).values())[0]
        additions = purchases.filter(trDate__range=(from_date, to_date))
        sum_addition = list(additions.aggregate(Sum('balQty')).values())[0]
        sales = MOS_Sales.objects.filter(group=group, code=code, scriptSno=master['sno'])
        sum_sales = list(sales.aggregate(Sum('sqty')).values())[0]
        holding['profitLoss'] = Decimal(master['marketValue']) - master['HoldingValue']
        holding['opening'] = 0 if sum_opening is None else int(sum_opening)
        holding['addition'] = 0 if sum_addition is None else int(sum_addition)
        holding['sales'] = 0 if sum_sales is None else int(sum_sales)
        holding['closing'] = holding['opening'] + holding['addition']
        holding['stcg'] = list(sales.aggregate(Sum('stcg')).values())[0]
        holding['ltcg'] = list(sales.aggregate(Sum('ltcg')).values())[0]
        holdings.append(holding)

    return holdings


class DayTradingViewSet(viewsets.ModelViewSet):

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        purchase_serializer = serializers.TranSumSerializer(
            data={'group': data['group'], 'code': data['code'], 'fy': data['fy'], 'trDate': data['trDate'],
                  'qty': data['qty'], 'rate': data['rate'], 'sVal': data['purchaseValue'],
                  'part': data['part'], 'againstType': 'Day Trading', 'sp': 'A'})
        purchase_serializer.is_valid(raise_exception=True)
        purchase_record = purchase_serializer.save()
        updated_purchase = TranSum.purchase_objects.filter(pk=purchase_record.pk).first()

        sale_serializer = serializers.DayTradingSaleSerializer(
            data={'group': data['group'], 'code': data['code'], 'fy': data['fy'], 'sDate': data['trDate'],
                  'sqty': data['qty'], 'srate': data['srate'], 'sVal': data['saleValue'],
                  'part': data['part'], 'purSno': updated_purchase.sno, 'scriptSno': updated_purchase.scriptSno,
                  'againstType': 'Day Trading', 'speculation': data['saleValue'] - data['purchaseValue']})
        sale_serializer.is_valid(raise_exception=True)
        sale_serializer.save()

        purchase_data = serializers.SalePurchaseSerializer(updated_purchase).data

        purchase_data['sales'] = [sale_serializer.data]

        response = {"status": True, "message": "Day Trading Record Created", "data": purchase_data}

        return Response(response)

    def list(self, request, *args, **kwargs):
        data = request.query_params.dict()
        data['fy'] = data.pop('dfy')
        data['againstType'] = 'Day Trading'
        purchase_queryset = TranSum.purchase_objects.filter(**data)
        result = []
        for purchase in purchase_queryset:
            sale = MOS_Sales.objects.filter(**data, purSno=purchase.sno, scriptSno=purchase.scriptSno).first()
            object = {
                "trId": purchase.trId,
                "part": purchase.part,
                "qty": purchase.qty,
                "trDate": purchase.trDate,
                "rate": purchase.rate,
                "srate": sale.srate,
                "purchaseValue": purchase.sVal,
                "saleValue": sale.sVal,
                "speculation": sale.speculation
            }
            result.append(object)

        return Response({"status": True, "message": "Retrieved Day Trades", "data": result})

    @transaction.atomic()
    def update(self, request, pk, *args, **kwargs):
        data = request.data.copy()
        purchase_object = TranSum.purchase_objects.get(pk=pk)
        purchase_serializer = serializers.TranSumSerializer(instance=purchase_object,
                                                            data={'group': data['group'], 'code': data['code'],
                                                                  'fy': data['fy'], 'trDate': data['trDate'],
                                                                  'qty': data['qty'], 'rate': data['rate'],
                                                                  'sVal': data['purchaseValue'],
                                                                  'part': data['part'], 'againstType': 'Day Trading',
                                                                  'sp': 'A'})
        purchase_serializer.is_valid(raise_exception=True)
        purchase_record = purchase_serializer.save()
        updated_purchase = TranSum.purchase_objects.filter(pk=purchase_record.pk).first()
        sale_object = MOS_Sales.objects.filter(group=data['group'], code=data['code'], fy=data['fy'],
                                               purSno=purchase_object.sno, scriptSno=purchase_object.scriptSno,
                                               againstType='Day Trading').first()

        sale_serializer = serializers.DayTradingSaleSerializer(instance=sale_object,
                                                               data={'group': data['group'], 'code': data['code'],
                                                                     'fy': data['fy'], 'sDate': data['trDate'],
                                                                     'sqty': data['qty'], 'srate': data['srate'],
                                                                     'sVal': data['saleValue'],
                                                                     'part': data['part'],
                                                                     'purSno': updated_purchase.sno,
                                                                     'scriptSno': updated_purchase.scriptSno,
                                                                     'againstType': 'Day Trading',
                                                                     'speculation': data['saleValue'] - data[
                                                                         'purchaseValue']})
        sale_serializer.is_valid(raise_exception=True)
        sale_serializer.save()
        purchase_object.refresh_from_db()
        purchase_data = serializers.SalePurchaseSerializer(purchase_object).data

        purchase_data['sales'] = [sale_serializer.data]

        response = {"status": True, "message": "Day Trading Record Updated", "data": purchase_data}

        return Response(response)


@api_view(['GET'])
def get_holding_report(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    masters = TranSum.master_objects.filter(**data).filter(balQty__gt=0).order_by('part')
    if len(masters) == 0:
        return Response({"status": False, "message": "No data present for selected parameters"})

    total_holding_values_by_part = masters.values('part').annotate(total_holding_value=(Sum('HoldingValue')))
    total_holding = list(total_holding_values_by_part.aggregate(Sum('total_holding_value')).values())[0]
    total_qty_by_part = masters.values('part').annotate(total_qty=(Sum('balQty')))
    total_qty = list(total_qty_by_part.aggregate(Sum('total_qty')).values())[0]
    list_holding_values = total_holding_values_by_part.values_list('total_holding_value', flat=True)
    percentages = round_to_100_percent(list_holding_values, 2)
    rows = []
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    for i in range(0, len(total_holding_values_by_part)):
        row = {}
        row['sno'] = i + 1
        row['script'] = total_holding_values_by_part[i]['part']
        row['qty'] = locale.format_string("%d", int(total_qty_by_part[i]['total_qty']), grouping=True)
        row['holding_perc'] = str(percentages[i]) + '%'
        row['holding_value'] = locale.format_string("%.2f",
                                                    round(total_holding_values_by_part[i]['total_holding_value'], 2),
                                                    grouping=True)
        rows.append(row)

    total = {
        'sno': " ",
        'script': "Total",
        'qty': locale.format_string("%d", int(total_qty), grouping=True),
        'holding_perc': 100,
        'holding_value': locale.format_string("%.2f", round(total_holding, 2), grouping=True)
    }
    titles = ['S.N.', 'Script', 'Qty', 'Holding%', 'Holding(Rs)']
    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name + " (FY " + data['fy'] + ")"
    description = 'Holding Report (' + data['againstType'] + ')'
    context = {
        'heading': heading,
        'description': description,
        'pre_table': pre_table,
        'table': rows,
        'titles': titles,
        'total': total,
        'post_table': " "
    }

    html = render_to_string('reports/holding-report-member.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Holding Report.pdf"'

    pisaStatus = pisa.CreatePDF(html, dest=response)
    return response


@api_view(['GET'])
def get_scriptwise_profit_report(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    masters = TranSum.master_objects.filter(**data).order_by('part')

    if len(masters) == 0:
        return Response({"status": False, "message": "No data present for selected parameters"})
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    for i in range(0, len(masters)):
        masters[i].save()
        masters[i].refresh_from_db()

    total_holding_values_by_part = masters.values('part', 'sno').annotate(total_holding_value=(Sum('HoldingValue')))
    total_holding_values_by_script = masters.values('part').annotate(total_holding_value=(Sum('HoldingValue')))
    total_market_values_by_part = masters.values('part', 'sno').annotate(total_market_value=(Sum('marketValue')))
    total_market_values_by_script = masters.values('part').annotate(total_market_value=(Sum('marketValue')))
    total_qty_by_part = masters.values('part').annotate(total_qty=(Sum('balQty')))
    total_qty = list(total_qty_by_part.aggregate(Sum('total_qty')).values())[0]
    list_profit_values = []

    for i in range(0, len(total_holding_values_by_script)):
        list_profit_values.append(
            Decimal(total_market_values_by_script[i]['total_market_value']) - total_holding_values_by_script[i][
                'total_holding_value'])
    total_profit = sum(list_profit_values)
    percentages = round_to_100_percent(list_profit_values, 2)
    rows = []
    total_stcg = Decimal(0)
    total_ltcg = Decimal(0)
    total_speculation = Decimal(0)
    for i in range(0, len(total_holding_values_by_script)):
        temp_masters = masters.filter(part=total_holding_values_by_script[i]['part'])
        stcg = Decimal(0)
        ltcg = Decimal(0)
        speculation = Decimal(0)
        for master in temp_masters:
            sales = MOS_Sales.objects.filter(group=data['group'], fy=data['fy'], againstType=data['againstType'],
                                             scriptSno=master.sno, code=master.code)
            sum_stcg = list(sales.aggregate(Sum('stcg')).values())[0]
            if sum_stcg:
                stcg = stcg + sum_stcg
            sum_ltcg = list(sales.aggregate(Sum('ltcg')).values())[0]
            if sum_ltcg:
                ltcg = ltcg + sum_ltcg
            sum_speculation = list(sales.aggregate(Sum('speculation')).values())[0]
            if sum_speculation:
                speculation = speculation + sum_speculation
        total_stcg = total_stcg + stcg
        total_ltcg = total_ltcg + ltcg
        total_speculation = total_speculation + speculation

        row = {}
        row['sno'] = i + 1
        row['script'] = total_holding_values_by_script[i]['part']
        row['qty'] = locale.format_string("%d", int(total_qty_by_part[i]['total_qty']), grouping=True)
        row['profit_perc'] = str(percentages[i]) + '%'
        row['profit_value'] = locale.format_string("%.2f", round(list_profit_values[i], 2), grouping=True)
        row['stcg'] = locale.format_string("%.2f", round(stcg, 2), grouping=True)
        row['ltcg'] = locale.format_string("%.2f", round(ltcg, 2), grouping=True)
        row['speculation'] = locale.format_string("%.2f", round(speculation, 2), grouping=True)

        rows.append(row)
    total = {
        'sno': " ",
        'script': "Total",
        'qty': locale.format_string("%d", int(total_qty), grouping=True),
        'profit_perc': 100,
        'profit_value': locale.format_string("%.2f", round(total_profit, 2), grouping=True),
        'stcg': locale.format_string("%.2f", round(total_stcg, 2), grouping=True),
        'ltcg': locale.format_string("%.2f", round(total_ltcg, 2), grouping=True),
        'speculation': locale.format_string("%.2f", round(total_speculation, 2), grouping=True)
    }
    titles = ['S.N.', 'Script', 'Qty', 'Profit%', 'Profit(Rs)', 'STCG', 'LTCG', 'Speculation']
    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name + " (FY " + data['fy'] + ")"
    description = 'Scriptwise Profit Report (' + data['againstType'] + ')'
    context = {
        'heading': heading,
        'description': description,
        'pre_table': pre_table,
        'table': rows,
        'titles': titles,
        'total': total,
        'post_table': " "
    }

    html = render_to_string('reports/scriptwise-profit-report.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Scriptwise_Profit_Report.pdf"'

    pisaStatus = pisa.CreatePDF(html, dest=response)
    return response


@api_view(['GET'])
def get_profit_adj_report(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    masters = TranSum.master_objects.filter(**data)
    if len(masters) == 0:
        return Response({"status": False, "message": "No data present for selected parameters"})
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    for i in range(0, len(masters)):
        masters[i].save()
        masters[i].refresh_from_db()

    total_holding_values_by_part = masters.values('part', 'sno').annotate(total_holding_value=(Sum('HoldingValue')))
    total_holding_values_by_script = masters.values('part').annotate(total_holding_value=(Sum('HoldingValue')),
                                                                     avg_mkt_rate=(Avg('marketRate')))

    total_market_values_by_part = masters.values('part', 'sno').annotate(total_market_value=(Sum('marketValue')))
    total_market_values_by_script = masters.values('part').annotate(total_market_value=(Sum('marketValue')))
    total_qty_by_part = masters.values('part').annotate(total_qty=(Sum('balQty')))
    total_qty = list(total_qty_by_part.aggregate(Sum('total_qty')).values())[0]
    total_holding = list(total_holding_values_by_script.aggregate(Sum('total_holding_value')).values())[0]
    list_profit_values = []
    for i in range(0, len(total_holding_values_by_script)):
        list_profit_values.append(
            Decimal(total_market_values_by_script[i]['total_market_value']) - total_holding_values_by_script[i][
                'total_holding_value'])
    total_profit = sum(list_profit_values)
    percentages = round_to_100_percent(list_profit_values, 2)
    rows = []
    total_stcg = Decimal(0)
    total_ltcg = Decimal(0)
    total_speculation = Decimal(0)
    for i in range(0, len(total_holding_values_by_script)):
        temp_masters = masters.filter(part=total_holding_values_by_script[i]['part'])
        stcg = Decimal(0)
        ltcg = Decimal(0)
        speculation = Decimal(0)
        for master in temp_masters:
            sales = MOS_Sales.objects.filter(group=data['group'], fy=data['fy'], againstType=data['againstType'],
                                             scriptSno=master.sno, code=master.code)
            sum_stcg = list(sales.aggregate(Sum('stcg')).values())[0]
            if sum_stcg:
                stcg = stcg + sum_stcg
            sum_ltcg = list(sales.aggregate(Sum('ltcg')).values())[0]
            if sum_ltcg:
                ltcg = ltcg + sum_ltcg
            sum_speculation = list(sales.aggregate(Sum('speculation')).values())[0]
            if sum_speculation:
                speculation = speculation + sum_speculation
        total_stcg = total_stcg + stcg
        total_ltcg = total_ltcg + ltcg
        total_speculation = total_speculation + speculation

        row = {}
        row['sno'] = i + 1
        row['script'] = total_holding_values_by_script[i]['part']
        row['qty'] = locale.format_string("%d", int(total_qty_by_part[i]['total_qty']), grouping=True)
        row['profit_perc'] = str(percentages[i]) + '%'
        row['profit_value'] = locale.format_string("%.2f", round(list_profit_values[i], 2), grouping=True)
        if total_qty_by_part[i]['total_qty'] == 0:
            row['purchase_price'] = 0
        else:
            row['purchase_price'] = locale.format_string("%.2f", round(
                total_holding_values_by_script[i]['total_holding_value'] / total_qty_by_part[i]['total_qty'], 2),
                                                         grouping=True)
        row['purchase_value'] = locale.format_string("%.2f",
                                                     round(total_holding_values_by_script[i]['total_holding_value'], 2),
                                                     grouping=True)
        row['mkt_rate'] = locale.format_string("%.2f", round(total_holding_values_by_script[i]['avg_mkt_rate'], 2),
                                               grouping=True)
        row['adj_pur_rate'] = " "

        rows.append(row)
    total = {
        'sno': " ",
        'script': "Total",
        'qty': locale.format_string("%d", int(total_qty), grouping=True),
        'profit_perc': 100,
        'profit_value': locale.format_string("%.2f", round(total_profit, 2), grouping=True),
        'purchase_price': " ",
        'purchase_value': locale.format_string("%.2f", round(total_holding, 2), grouping=True),
        'mkt_rate': " ",
        'adj_pur_rate': " "
    }
    titles = ['S.N.', 'Script', 'Qty', 'Profit%', 'Profit(Rs)', 'Purchase Price', 'Purchase Value', 'Market Rate',
              'Adjusted Purchase Rate']
    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name + " (FY " + data['fy'] + ")"
    description = 'Holding Report (Profit Adjusted - ' + data['againstType'] + ')'
    context = {
        'heading': heading,
        'description': description,
        'pre_table': pre_table,
        'table': rows,
        'titles': titles,
        'total': total,
        'post_table': " "
    }

    html = render_to_string('reports/profit-adjusted-report.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Profit_Adjusted_Report.pdf"'

    pisaStatus = pisa.CreatePDF(html, dest=response)
    return response


@api_view(['GET'])
def get_transaction_report(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    masters = TranSum.master_objects.filter(**data)
    if len(masters) == 0:
        return Response({"status": False, "message": "No data present for selected parameters"})
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    for i in range(0, len(masters)):
        masters[i].save()
        masters[i].refresh_from_db()

    purchases = TranSum.purchase_objects.filter(**data)
    rows = []
    i = 1
    for purchase in purchases:
        sales = MOS_Sales.objects.filter(group=data['group'], code=data['code'], fy=data['fy'], purSno=purchase.sno,
                                         scriptSno=purchase.scriptSno)
        temp_purchase = purchase
        for sale in sales:
            row = {}
            row['sno'] = i
            row['s_date'] = sale.sDate.strftime('%d-%m-%Y')
            row['part'] = purchase.part
            row['s_qty'] = locale.format_string("%d", sale.sqty, grouping=True)
            row['s_rate'] = float(round(sale.srate, 2))
            row['s_value'] = locale.format_string("%.2f", float(round(sale.sVal, 2)), grouping=True)
            row['s_stt'] = locale.format_string("%.2f", float(round(sale.stt, 2)),
                                                grouping=True) if sale.stt is not None else " "
            row['s_other'] = locale.format_string("%.2f", float(round(sale.other, 2)),
                                                  grouping=True) if sale.other is not None else " "
            row['s_net'] = locale.format_string("%f", float(sale.sqty * temp_purchase.rate), grouping=True)

            row['pur_qty'] = locale.format_string("%d", float(round(temp_purchase.qty, 2)), grouping=True)
            row['pur_rate'] = float(round(temp_purchase.rate, 2))
            row['pur_value'] = locale.format_string("%.2f", float(round(temp_purchase.rate * temp_purchase.qty, 2)),
                                                    grouping=True)
            row['pur_stt'] = locale.format_string("%.2f", float(round(temp_purchase.sttCharges, 2)), grouping=True)
            row['pur_other'] = locale.format_string("%.2f", float(round(temp_purchase.otherCharges, 2)), grouping=True)
            row['pur_net'] = locale.format_string("%.2f",
                                                  float(round(
                                                      temp_purchase.rate * temp_purchase.qty + temp_purchase.sttCharges + temp_purchase.otherCharges,
                                                      2)),
                                                  grouping=True)
            row['profit'] = locale.format_string("%.2f", float(round(temp_purchase.marketRate * temp_purchase.qty, 2)),
                                                 grouping=True)
            rows.append(row)
            i = i + 1
    total = {
        'sno': " ",
        's_date': "Total",
        'part': " ",
        's_qty': " ",
        's_rate': " ",
        's_value': " ",
        's_stt': " ",
        's_other': " ",
        's_net': " ",
        'pur_qty': " ",
        'pur_rate': " ",
        'pur_value': " ",
        'pur_stt': " ",
        'pur_other': " ",
        'pur_net': " ",
        'profit': sum_by_key(rows, 'profit')
    }
    titles = [' ', 'Date', 'Script', 'Qty', 'Rate', 'Value', 'STT', 'Other', 'Net',
              'Qty', 'Rate', 'Value', 'STT', 'Other', 'Net', 'Profit']
    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name + " (FY " + data['fy'] + ")"
    description = 'Transaction Report ( ' + data['againstType'] + ')'
    context = {
        'heading': heading,
        'description': description,
        'pre_table': pre_table,
        'table': rows,
        'titles': titles,
        'total': total,
        'post_table': " "
    }

    html = render_to_string('reports/transaction-report.html', context)
    # html = render_to_string('reports/test.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Transaction_Report.pdf"'

    pisaStatus = pisa.CreatePDF(html, dest=response)
    return response


@api_view(['GET'])
def get_mos_report(request):
    data = request.query_params.dict()
    # data['fy'] = data.pop('dfy')
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    ltcg_released = []
    ltcg_unreleased = []
    stcg_released = []
    stcg_unreleased = []

    sales = MOS_Sales.objects.filter(**data)
    for sale in sales:
        purchase = TranSum.purchase_objects.filter(group=data['group'], code=sale.code, sno=sale.purSno,
                                                   scriptSno=sale.scriptSno).first()
        if purchase is None:
            continue
        sale_row = {}

        # sale_row['sno'] = 0
        sale_row['script'] = purchase.part
        sale_row['qty'] = sale.sqty
        sale_row['pur_date'] = purchase.trDate
        sale_row['pur_rate'] = round(purchase.rate, 2)
        sale_row['sale_date'] = sale.sDate
        sale_row['sale_rate'] = round(sale.srate, 2)
        time_delta = relativedelta(sale.sDate, purchase.trDate)
        if (time_delta.years * 12 + time_delta.months) <= 12:
            sale_row['cg'] = round(sale.stcg, 2)
            stcg_released.append(sale_row)
        else:
            sale_row['cg'] = round(sale.ltcg, 2)
            ltcg_released.append(sale_row)

    purchases = TranSum.purchase_objects.filter(**data).filter(balQty__gt=0)
    for purchase in purchases:
        purchase_row = {}
        # purchase_row['sno'] = 0
        purchase_row['script'] = purchase.part
        purchase_row['qty'] = purchase.balQty
        purchase_row['pur_date'] = purchase.trDate
        purchase_row['pur_rate'] = round(purchase.rate, 2)
        purchase_row['closing'] = purchase.balQty
        mkt_rate = services.get_market_rate_value(purchase.part)
        purchase_row['marketRate'] = round(mkt_rate, 2) if mkt_rate is not None else " "
        purchase_row['cg'] = (Decimal(mkt_rate) - purchase.rate) * purchase.balQty if mkt_rate is not None else " "
        time_delta = relativedelta(datetime.date.today(), purchase.trDate)
        if (time_delta.years * 12 + time_delta.months) <= 12:
            sale_row['cg'] = round(sale.stcg, 2)
            stcg_unreleased.append(sale_row)
        else:
            sale_row['cg'] = round(sale.ltcg, 2)
            ltcg_unreleased.append(sale_row)

    stcg_unreleased_total = sum_by_key(stcg_unreleased, 'cg')
    stcg_released_total = sum_by_key(stcg_released, 'cg')
    ltcg_released_total = sum_by_key(ltcg_released, 'cg')
    ltcg_unreleased_total = sum_by_key(ltcg_unreleased, 'cg')

    totals = {
        'stcg_unreleased_total': round(stcg_unreleased_total, 2),
        'stcg_released_total': round(stcg_released_total, 2),
        'ltcg_released_total': round(ltcg_released_total, 2),
        'ltcg_unreleased_total': round(ltcg_unreleased_total, 2)
    }
    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name
    description = 'MOS Report ( ' + data['againstType'] + ')'
    context = {
        'ltcg_released': ltcg_released,
        'ltcg_unreleased': ltcg_unreleased,
        'stcg_released': stcg_released,
        'stcg_unreleased': stcg_unreleased,
        'totals': totals,
        'heading': heading,
        'description': description,
        'pre_table': pre_table,
    }

    html = render_to_string('reports/mos_report.html', context)
    # html = render_to_string('reports/test.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="MOS_Report.pdf"'

    pisaStatus = pisa.CreatePDF(html, dest=response)
    return response


@transaction.atomic
@api_view(['GET'])
def get_strategy(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    days = data.pop('days')
    records = TranSum.objects.filter(**data)
    part_list = list(records.values_list('part', flat=True).distinct())
    strategy_record = services.get_strategy_values(part_list, days)
    print(strategy_record)
    for strategy in strategy_record:
        temp_records = records.filter(part=strategy['part'])
        temp_records.update(strategyDate=datetime.datetime.strptime(strategy['date'], '%d-%m-%Y'),
                            strategyTrigger=strategy['trigger'])
    wb_file = services.get_strategy_file(part_list, days)
    # data = prepare_holdings_response(request.query_params.dict())

    response = HttpResponse(content=wb_file, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=strategy.xlsx'

    return response


def round_to_100_percent(number_set, digit_after_decimal=2):
    """
        This function take a list of number and return a list of percentage, which represents the portion of each number in sum of all numbers
        Moreover, those percentages are adding up to 100%!!!
        Notice: the algorithm we are using here is 'Largest Remainder'
        The down-side is that the results won't be accurate, but they are never accurate anyway:)
    """
    if len(number_set) == 0:
        return None
    unround_numbers = [x / Decimal(float(sum(number_set))) * 100 * 10 ** digit_after_decimal for x in number_set]
    decimal_part_with_index = sorted([(index, unround_numbers[index] % 1) for index in range(len(unround_numbers))],
                                     key=lambda y: y[1], reverse=True)
    remainder = 100 * 10 ** digit_after_decimal - sum([int(x) for x in unround_numbers])
    index = 0
    while remainder > 0:
        unround_numbers[decimal_part_with_index[index][0]] += 1
        remainder -= 1
        index = (index + 1) % len(number_set)
    return [int(x) / float(10 ** digit_after_decimal) for x in unround_numbers]
