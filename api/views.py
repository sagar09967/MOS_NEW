import datetime
import json
import operator
from decimal import Decimal
from io import StringIO, BytesIO

import matplotlib
import numpy
import pandas
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
from django.http import Http404, HttpResponse, StreamingHttpResponse, FileResponse
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
from .constants import AGAINST_TYPE_MAP


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

            return Response({'status': True, 'message': 'You have successfully Created', 'data': serializer.data},
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
            return Response({'status': True, 'message': 'You have successfully Created', 'data': serializer.data},
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
        return Response({'status': True, 'message': 'done', 'data': primary_ls})


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
            "message": "Data successfully updated",
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
        return Response({'status': True, 'message': 'done', 'data1': serializer.data, 'data': context})


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
        return Response({'status': True, 'message': 'done', 'data': ls})


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
        return Response({'status': True, 'message': 'done', 'data': serializer.data})


# <---------------------------- updated delete api mrmber ----------------->
class MemberUpdadeDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = MemberMaster.objects.all()
    serializer_class = SaveMemberSerializer

    @transaction.atomic()
    def delete(self, request, pk):
        try:
            member = MemberMaster.objects.get(pk=pk)
            member.delete()
            return Response({"status": True, "message": "Deleted member id " + str(pk)})
        except Exception as e:
            return Response({"status": False, "message": str(e)})


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
            return Response({'status': True, 'message': 'You have successfully Created', 'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <---------------- RetCustomer API -------------------->
class RetCustomer(APIView):
    def get(self, request, format=None):
        username = self.request.query_params.get('username')
        customer = CustomerMaster.objects.filter(username=username)
        serializer = SavecustomerSerializer(customer, many=True)
        return Response({'status': True, 'message': 'done', 'data': serializer.data})


# <------------ updated delete api Customer ---------------->
class CustomerUpdadeDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerMaster.objects.all()
    serializer_class = SavecustomerSerializer

    def update(self, request, *args, **kwargs):
        print(request.data.copy())
        return super(CustomerUpdadeDelete, self).update(request)


# < --------------- Login Customer Master Api ---------------->

class CustomerLogin(APIView):
    def post(self, request, format=None):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = serializer.data.get('username')
            password = serializer.data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                return Response({'status': True, 'message': 'Login Success', 'data': serializer.data},
                                status=status.HTTP_200_OK)
            else:
                return Response({'status': False, 'message': 'Username or Password is not Valid', 'data': ' '})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# <----------------- RetChangeDefault ----------------->
class RetChangeDefault(APIView):
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        member = MemberMaster.objects.filter(group=group)
        serializer = RetChangeDefaultSerializer(member, many=True)
        return Response({'status': True, 'message': 'done', 'data': serializer.data})


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
            queryset = queryset.filter(trDate__lt=start_fy, fy=dfy)
        # data = request.query_params.dict()
        elif sp == 'A':
            queryset = queryset.filter(trDate__range=(start_fy, end_fy), fy=dfy)

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

    @transaction.atomic
    def delete(self, request, pk):
        try:
            purchase = TranSum.objects.get(pk=pk)
            purchase.delete()
        except Exception as e:
            return Response({"status": False, "message": str(e)})
        return Response({"status": True, "message": "Deleted purchase id " + pk})


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
                                             fy=dfy)
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

    @transaction.atomic
    def delete(self, request, pk):
        sale = MOS_Sales.objects.get(pk=pk)
        sale.delete()
        return Response({"status": True, "message": "Deleted sale id " + pk})


@api_view(['GET'])
@transaction.atomic
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

    masters = TranSum.master_objects.filter(group=group, code=code, againstType=againstType, fy=dfy)
    if len(masters) == 0 and dfy != '2021-2022':
        years = dfy.split("-")
        start_year = int(years[0])
        end_year = int(years[1])
        prev_dfy = str(start_year - 1) + "-" + str(end_year - 1)
        masters = carry_forward_records(group, code, againstType, prev_dfy, dfy)

    for master in masters.values():
        purchases = TranSum.purchase_objects.filter(group=group, code=code, againstType=againstType,
                                                    scriptSno=master['sno'], part=master['part'], fy=dfy)
        if len(purchases) == 0:
            continue
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

        openings = purchases.filter(sp='O')
        sum_opening = list(openings.aggregate(Sum('qty')).values())[0]
        additions = purchases.filter(sp='A')
        sum_addition = list(additions.aggregate(Sum('qty')).values())[0]
        sales = MOS_Sales.objects.filter(group=group, code=code, scriptSno=master['sno'], fy=dfy)
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


@transaction.atomic
def carry_forward_records(group, code, againstType, prev_dfy, next_dfy):
    masters = TranSum.master_objects.filter(group=group, code=code,
                                            againstType=againstType,
                                            fy=prev_dfy)
    if len(masters) == 0:
        years = prev_dfy.split("-")
        start_year = int(years[0])
        end_year = int(years[1])
        if start_year - 1 < 2021:
            return TranSum.master_objects.none()
        new_prev_dfy = str(start_year - 1) + "-" + str(end_year - 1)
        new_next_dfy = prev_dfy
        generated_masters = carry_forward_records(group, code, againstType, new_prev_dfy, new_next_dfy)
        result_masters = carry_forward_records(group, code, againstType, prev_dfy, next_dfy)
        return result_masters
    else:
        purchases = TranSum.purchase_objects.filter(group=group, code=code,
                                                    againstType=againstType,
                                                    fy=prev_dfy)
        years = next_dfy.split("-")
        start_year = int(years[0])
        end_year = int(years[1])
        for purchase in purchases:
            if purchase.balQty > 0:
                carried_purchase = TranSum()
                carried_purchase.group = purchase.group
                carried_purchase.code = purchase.code
                carried_purchase.part = purchase.part
                carried_purchase.qty = purchase.balQty
                carried_purchase.fy = next_dfy
                carried_purchase.againstType = againstType
                carried_purchase.sp = 'O'
                carried_purchase.rate = purchase.rate
                carried_purchase.fmr = purchase.fmr
                carried_purchase.sVal = purchase.HoldingValue
                carried_purchase.trDate = purchase.trDate
                carried_purchase.sttCharges = purchase.sttCharges
                carried_purchase.otherCharges = purchase.otherCharges
                carried_purchase.noteAdd = purchase.noteAdd
                carried_purchase.isinCode = purchase.isinCode
                carried_purchase.save()
            else:
                continue

        carried_masters = TranSum.master_objects.filter(group=group, code=code,
                                                        againstType=againstType,
                                                        fy=next_dfy)
        return carried_masters


@api_view(['GET'])
def member_capital_gain(request):
    group = request.query_params.get('group')
    code = request.query_params.get('code')
    dfy = request.query_params.get('dfy')
    againstType = request.query_params.get('againstType')
    purchases = TranSum.purchase_objects.filter(group=group, code=code, againstType=againstType, fy=dfy)
    sales = MOS_Sales.objects.none()
    for purchase in purchases:
        temp_sales = MOS_Sales.objects.filter(group=group, code=code, fy=dfy, purSno=purchase.sno,
                                              scriptSno=purchase.scriptSno)
        sales = sales | temp_sales
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


def sum_by_key_ul(records, key):
    sum_result = 0
    for record in records:
        sum_result = sum_result + getattr(record, key)
    return sum_result


def sum_by_key_ul(records: dict[str], key):
    sum_result = 0
    for record in records:
        sum_result = sum_result + record[key]
    return sum_result


def sum_by_key(records: dict[str], key):
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    sum_result = Decimal(0)
    for record in records:
        if record[key] == " " or record[key] is None:
            continue
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
        queryset = queryset.filter(trDate__lt=start_fy, fy=dfy)
    # data = request.query_params.dict()
    elif sp == 'A':
        queryset = queryset.filter(trDate__range=(start_fy, end_fy), fy=dfy)

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
    masters = TranSum.master_objects.filter(group=group, code=code, againstType=againstType, fy=dfy)
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
                                                    scriptSno=master['sno'], part=master['part'], fy=dfy)
        if len(purchases) == 0:
            continue
        openings = purchases.filter(sp='O')
        sum_opening = list(openings.aggregate(Sum('qty')).values())[0]
        additions = purchases.filter(sp='A')
        sum_addition = list(additions.aggregate(Sum('qty')).values())[0]
        # sales = MOS_Sales.objects.filter(group=group, code=code, scriptSno=master['sno'], againstType=againstType)
        sales = TranSum.get_all_sales(group=group, code=code, againstType=againstType, fy=dfy).filter(
            scriptSno=master['sno'])
        sum_sales = list(sales.aggregate(Sum('sqty')).values())[0]

        holding['profitLoss'] = Decimal(master['marketValue']) - master['HoldingValue']
        holding['opening'] = 0 if sum_opening is None else int(sum_opening)
        holding['addition'] = 0 if sum_addition is None else int(sum_addition)
        holding['sales'] = 0 if sum_sales is None else int(sum_sales)
        holding['closing'] = holding['opening'] + holding['addition'] - holding['sales']
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
                  'againstType': purchase_record.sp, 'speculation': data['saleValue'] - data['purchaseValue']})
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
                                                                     'againstType': purchase_record.sp,
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

    masters = TranSum.master_objects.filter(**data).order_by('part')
    for master in masters:
        purchases = master.get_child_objects()
        if purchases.count() == 0:
            masters = masters.exclude(pk=master.pk)
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
    for master in masters:
        purchases = master.get_child_objects()
        if purchases.count() == 0:
            masters = masters.exclude(pk=master.pk)
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
    gains_list = []
    for i in range(0, len(total_holding_values_by_script)):
        temp_masters = masters.filter(part=total_holding_values_by_script[i]['part'])
        gain = Decimal(0)
        for master in temp_masters:
            sales = MOS_Sales.objects.filter(group=data['group'], fy=data['fy'],
                                             scriptSno=master.sno, code=master.code)
            sum_stcg = list(sales.aggregate(Sum('stcg')).values())[0]
            if sum_stcg:
                gain = gain + sum_stcg
            sum_ltcg = list(sales.aggregate(Sum('ltcg')).values())[0]
            if sum_ltcg:
                gain = gain + sum_ltcg
        gains_list.append(gain)
    total_gain = sum(gains_list)
    gains_percentages = round_to_100_percent(gains_list)
    for i in range(0, len(total_holding_values_by_script)):
        row = {}
        row['sno'] = i + 1
        row['script'] = total_holding_values_by_script[i]['part']
        row['qty'] = locale.format_string("%d", int(total_qty_by_part[i]['total_qty']), grouping=True)
        row['gain_perc'] = str(gains_percentages[i]) + '%'
        row['gain_value'] = locale.format_string("%.2f", round(gains_list[i], 2), grouping=True)

        rows.append(row)
    total = {
        'sno': " ",
        'script': "Total",
        'qty': locale.format_string("%d", int(total_qty), grouping=True),
        'gain_perc': 100,
        'gain_value': locale.format_string("%.2f", round(total_gain, 2), grouping=True)
    }
    titles = ['S.N.', 'Script', 'Qty', 'Gain%', 'Gain(Rs)']
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

    masters = TranSum.master_objects.filter(**data).order_by('part')
    for master in masters:
        purchases = master.get_child_objects()
        if purchases.count() == 0:
            masters = masters.exclude(pk=master.pk)
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
    gains_list = []
    for i in range(0, len(total_holding_values_by_script)):
        temp_masters = masters.filter(part=total_holding_values_by_script[i]['part'])

        gain = Decimal(0)
        for master in temp_masters:
            sales = MOS_Sales.objects.filter(group=data['group'], fy=data['fy'], againstType=data['againstType'],
                                             scriptSno=master.sno, code=master.code)
            sum_stcg = list(sales.aggregate(Sum('stcg')).values())[0]
            if sum_stcg:
                gain = gain + sum_stcg
            sum_ltcg = list(sales.aggregate(Sum('ltcg')).values())[0]
            if sum_ltcg:
                gain = gain + sum_ltcg
            gains_list.append(gain)
    total_gain = sum(gains_list)
    gains_percentages = round_to_100_percent(gains_list)
    for i in range(0, len(total_holding_values_by_script)):
        row = {}
        row['sno'] = i + 1
        row['script'] = total_holding_values_by_script[i]['part']
        row['qty'] = locale.format_string("%d", int(total_qty_by_part[i]['total_qty']), grouping=True)
        row['gain_perc'] = str(gains_percentages[i]) + '%'
        row['gain_value'] = locale.format_string("%.2f", round(gains_list[i], 2), grouping=True)
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
        row['adj_pur_rate'] = locale.format_string("%.2f", round(
            (total_holding_values_by_script[i]['total_holding_value'] - gains_list[i]) / \
            total_qty_by_part[i]['total_qty'], 2), grouping=True) if total_qty_by_part[i]['total_qty'] != 0 else " "

        rows.append(row)
    total = {
        'sno': " ",
        'script': "Total",
        'qty': locale.format_string("%d", int(total_qty), grouping=True),
        'gain_perc': "100%",
        'gain_value': locale.format_string("%.2f", round(total_gain, 2), grouping=True),
        'purchase_price': " ",
        'purchase_value': locale.format_string("%.2f", round(total_holding, 2), grouping=True),
        'mkt_rate': " ",
        'adj_pur_rate': " "
    }
    titles = ['S.N.', 'Script', 'Qty', 'Gain%', 'Gain(Rs)', 'Purchase Price', 'Purchase Value', 'Market Rate',
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

    purchases = TranSum.purchase_objects.filter(**data).order_by('part')
    data_copy = data.copy()
    data_copy.pop("againstType")
    rows = []
    i = 1
    for purchase in purchases:
        sales = MOS_Sales.objects.filter(**data_copy, purSno=purchase.sno,
                                         scriptSno=purchase.scriptSno).order_by(
            'sDate')
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
            row['s_net'] = locale.format_string("%.2f", float(round(sale.sqty * temp_purchase.rate, 2)), grouping=True)

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
                                                 grouping=True) if temp_purchase.marketRate else " "
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
        'profit': locale.format_string("%.2f", sum_by_key(rows, 'profit'), grouping=True)
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


import seaborn as sns
from matplotlib import pyplot as plt


@api_view(['GET'])
def get_profit_chart(request):
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
    # for i in range(0, len(masters)):
    #     masters[i].save()
    #     masters[i].refresh_from_db()

    purchases = TranSum.purchase_objects.filter(**data).order_by('part')
    rows = []
    cummulative_profit = Decimal(0)
    for purchase in purchases:
        sales = MOS_Sales.objects.filter(group=data['group'], code=data['code'], fy=data['fy'], purSno=purchase.sno,
                                         scriptSno=purchase.scriptSno).order_by(
            'sDate')
        temp_purchase = purchase
        if len(sales) > 0:
            for sale in sales:
                row = {}
                row['sDate'] = sale.sDate
                row['profit'] = float(sale.sVal - temp_purchase.sVal) if sale.sVal - temp_purchase.sVal > 0 else 0
                rows.append(row)
        else:
            row = {}
            row['sDate'] = purchase.trDate
            row['profit'] = 0
            rows.append(row)

    rows_df = pandas.DataFrame.from_records(rows)
    rows_df = rows_df.sort_values('sDate')
    rows_df['month'] = pandas.to_datetime(rows_df['sDate'], format="%Y-%m-%d").dt.strftime('%B %Y')
    df2 = rows_df.groupby('month', sort=False, as_index=False)['profit'].sum()
    df2['cummulative_profit'] = df2['profit'].cumsum()
    fig, ax = plt.subplots()
    # ax.set_ylim(bottom=int(df2['cummulative_profit'].min()),top=int(df2['cummulative_profit'].max()))
    # ax.axis(ymin=int(df2['cummulative_profit'].min()), ymax=int(df2['cummulative_profit'].max()))
    # ax.ticklabel_format(style='plain')
    # ax.autoscale(False)
    line1 = ax.plot(df2['month'].values, df2['profit'].values, marker='o', label="Profit")[0]
    line2 = ax.plot(df2['month'].values, df2['cummulative_profit'].values, marker='o', label="Cummulative Profit")[0]
    add_labels(ax, line1)
    add_labels(ax, line2)

    # ax = df2.plot(x='month', marker='o')
    ax.ticklabel_format(style='plain', axis='y')
    # ax.set_ylim(int(df2['cummulative_profit'].min()), int(df2['cummulative_profit'].max()))

    # ax.get_yaxis().set_major_formatter(
    #     matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    # ax.ticklabel_format(style='plain',axis='y')
    # ax.plot(df2['month'], df2['profit'])
    # ax.plot(df2['month'], df2['profit'], marker='o', label="Profit")
    # ax.plot(df2['month'], df2['cummulative_profit'], marker='o', label="Cummulative Profit")
    ax.legend()
    # fig, ax = pyplot.subplots(figsize=a4_dims)
    # ax.plot(df2['month'],df2['profit'])
    # ax.plot(df2['month'],df2['cummulative_profit'])
    # lineplot = sns.lineplot(x='month', y='profit', data=df2, ci=False, ax=ax)
    # fig.show()
    fig.tight_layout()
    fig.set_size_inches(16, 4)
    fig.savefig('out.png')
    # fig.savefig("out.png")
    response = FileResponse(open('out.png', 'rb'), filename="Profit_Chart.png", content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="Profit_Chart.png"'

    return response


def add_labels(ax, line):
    x, y = line.get_data()
    labels = map(','.join, zip(map(lambda s: '%g' % s, x), map(lambda s: '%g' % s, y)))
    map(ax.text, x, y, labels)


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

    filter = "both"
    if data.get("filter"):
        filter = data.pop('filter')

    ltcg_released = []
    ltcg_unreleased = []
    stcg_released = []
    stcg_unreleased = []
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    sales = MOS_Sales.objects.filter(**data)
    if filter == 'both' or filter == 'released':
        for sale in sales:
            purchase = TranSum.purchase_objects.filter(group=data['group'], code=sale.code, sno=sale.purSno,
                                                       scriptSno=sale.scriptSno).first()
            if purchase is None:
                continue
            sale_row = {}

            # sale_row['sno'] = 0
            sale_row['script'] = purchase.part
            sale_row['qty'] = sale.sqty
            sale_row['pur_date'] = purchase.trDate.strftime('%d-%m-%Y')
            sale_row['pur_rate'] = round(purchase.rate, 2)
            sale_row['sale_date'] = sale.sDate.strftime('%d-%m-%Y')
            sale_row['sale_rate'] = round(sale.srate, 2)
            time_delta = relativedelta(sale.sDate, purchase.trDate)
            if (time_delta.years * 12 + time_delta.months) <= 12:
                sale_row['cg'] = (sale.srate - purchase.rate) * sale.sqty
                sale_row['cg'] = locale.format_string("%.2f", round(sale.stcg, 2), grouping=True)
                stcg_released.append(sale_row)
            else:
                sale_row['cg'] = (sale.srate - purchase.rate) * sale.sqty
                sale_row['cg'] = locale.format_string("%.2f", round(sale_row['cg'], 2), grouping=True)
                ltcg_released.append(sale_row)

    if filter == 'both' or filter == 'unreleased':
        purchases = TranSum.purchase_objects.filter(**data).filter(balQty__gt=0).order_by('part')
        for purchase in purchases:
            purchase_row = {}
            # purchase_row['sno'] = 0
            purchase_row['script'] = purchase.part
            purchase_row['qty'] = locale.format_string("%d", int(purchase.balQty), grouping=True)
            purchase_row['pur_date'] = purchase.trDate.strftime('%d-%m-%Y')
            purchase_row['pur_rate'] = round(purchase.rate, 2)
            purchase_row['closing'] = locale.format_string("%d", purchase.balQty, grouping=True)
            mkt_rate = services.get_market_rate_value(purchase.part)
            purchase_row['marketRate'] = locale.format_string("%.2f", round(mkt_rate, 2),
                                                              grouping=True) if mkt_rate is not None else " "
            purchase_row['cg'] = locale.format_string("%.2f", (Decimal(mkt_rate) - purchase.rate) * purchase.balQty,
                                                      grouping=True) if mkt_rate is not None else " "
            time_delta = relativedelta(datetime.date.today(), purchase.trDate)
            if (time_delta.years * 12 + time_delta.months) <= 12:

                stcg_unreleased.append(purchase_row)
            else:
                ltcg_unreleased.append(purchase_row)

    stcg_unreleased_total = sum_by_key(stcg_unreleased, 'cg')
    stcg_released_total = sum_by_key(stcg_released, 'cg')
    ltcg_released_total = sum_by_key(ltcg_released, 'cg')
    ltcg_unreleased_total = sum_by_key(ltcg_unreleased, 'cg')

    totals = {
        'stcg_unreleased_total': locale.format_string("%.2f", round(stcg_unreleased_total, 2), grouping=True),
        'stcg_released_total': locale.format_string("%.2f", round(stcg_released_total, 2), grouping=True),
        'ltcg_released_total': locale.format_string("%.2f", round(ltcg_released_total, 2), grouping=True),
        'ltcg_unreleased_total': locale.format_string("%.2f", round(ltcg_unreleased_total, 2), grouping=True)
    }
    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name
    description = 'MOS Report ( ' + data['againstType'] + ' )' + " FY " + "2021-2022"
    context = {
        'released': filter == 'both' or filter == 'released',
        'unreleased': filter == 'both' or filter == 'unreleased',
        'ltcg_released': sorted(ltcg_released,
                                key=lambda x: (x['script'], datetime.datetime.strptime(x['pur_date'], '%d-%m-%Y'))),
        'ltcg_unreleased': sorted(ltcg_unreleased,
                                  key=lambda x: (x['script'], datetime.datetime.strptime(x['pur_date'], '%d-%m-%Y'))),
        'stcg_released': sorted(stcg_released,
                                key=lambda x: (x['script'], datetime.datetime.strptime(x['pur_date'], '%d-%m-%Y'))),
        'stcg_unreleased': sorted(stcg_unreleased,
                                  key=lambda x: (x['script'], datetime.datetime.strptime(x['pur_date'], '%d-%m-%Y'))),
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


@api_view(['GET'])
def script_review_report(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    masters = TranSum.master_objects.filter(**data).order_by('part')
    for master in masters:
        purchases = master.get_child_objects()
        if purchases.count() == 0:
            masters = masters.exclude(pk=master.pk)
    master_rows = []
    for master in masters:
        purchases = TranSum.purchase_objects.filter(**data, part=master.part, scriptSno=master.sno).order_by('trDate')
        master_row = {
            "part": master.part,
            "purchases": []
        }
        mkt_rate = services.get_market_rate_value(master.part)
        for purchase in purchases:
            pur_cg = locale.format_string("%.2f", (Decimal(mkt_rate) - purchase.rate) * purchase.balQty,
                                          grouping=True) if mkt_rate is not None else " "
            purchase_row = {
                "pur_date": purchase.trDate.strftime('%d-%m-%Y'),
                "pur_qty": locale.format_string('%d', purchase.qty, grouping=True),
                "pur_rate": locale.format_string('%.2f', purchase.rate, grouping=True),
                "pur_value": locale.format_string('%.2f', purchase.sVal, grouping=True),
                "sales": [],
                "bal_qty": locale.format_string('%d', purchase.balQty, grouping=True),
                "mkt_rate": locale.format_string('%.2f', mkt_rate, grouping=True),
                "stcg": " ",
                "ltcg": " ",
                "speculation": " ",

            }
            time_delta = relativedelta(datetime.date.today(), purchase.trDate)
            if (time_delta.years * 12 + time_delta.months) <= 12:
                purchase_row['stcg'] = pur_cg
            else:
                purchase_row['ltcg'] = pur_cg

            sales = MOS_Sales.objects.filter(group=purchase.group, code=purchase.code, purSno=purchase.sno,
                                             scriptSno=purchase.scriptSno, againstType=data['againstType'],
                                             fy=purchase.fy).order_by('sDate')
            if len(sales) == 0:
                sale_row = {
                    "s_date": " ",
                    "s_qty": " ",
                    "s_rate": " ",
                    "s_val": " ",
                    "stcg": " ",
                    "ltcg": " ",
                    "speculation": " "
                }
                purchase_row['sales'].append(sale_row)
                purchase_row['sales_range'] = range(0, 1)
            else:
                for sale in sales:
                    s_time_delta = relativedelta(sale.sDate, purchase.trDate)
                    sale_row = {
                        "s_date": sale.sDate.strftime('%d-%m-%Y'),
                        "s_qty": locale.format_string('%d', sale.sqty, grouping=True),
                        "s_rate": locale.format_string('%.2f', sale.srate, grouping=True),
                        "s_val": locale.format_string('%.2f', sale.sVal, grouping=True),
                        "stcg": " ",
                        "ltcg": " ",
                        "speculation": sale.speculation if sale.speculation else " "
                    }
                    if (s_time_delta.years * 12 + s_time_delta.months) <= 12:
                        sale_row['stcg'] = (sale.srate - purchase.rate) * sale.sqty
                        sale_row['stcg'] = locale.format_string("%.2f", round(sale_row['stcg'], 2), grouping=True)
                    else:
                        sale_row['ltcg'] = (sale.srate - purchase.rate) * sale.sqty
                        sale_row['ltcg'] = locale.format_string("%.2f", round(sale_row['ltcg'], 2), grouping=True)
                    purchase_row['sales_range'] = range(1, len(sales))
                    purchase_row['sales'].append(sale_row)
            purchase_row['sale_qty_total'] = locale.format_string("%d", sum_by_key(purchase_row['sales'], 's_qty'),
                                                                  grouping=True)
            purchase_row['sale_value_total'] = locale.format_string("%.2f", sum_by_key(purchase_row['sales'], 's_val'),
                                                                    grouping=True)
            purchase_row['sale_stcg_total'] = locale.format_string("%.2f", sum_by_key(purchase_row['sales'], 'stcg'),
                                                                   grouping=True)
            purchase_row['sale_ltcg_total'] = locale.format_string("%.2f", sum_by_key(purchase_row['sales'], 'ltcg'),
                                                                   grouping=True)
            purchase_row['sale_spec_total'] = locale.format_string("%.2f",
                                                                   sum_by_key(purchase_row['sales'], 'speculation'),
                                                                   grouping=True)
            master_row['purchases'].append(purchase_row)
        master_row['purchase_qty_total'] = sum_by_key(master_row['purchases'], 'pur_qty')
        master_row['purchase_value_total'] = sum_by_key(master_row['purchases'], 'pur_value')
        master_row['purchase_bal_qty_total'] = sum_by_key(master_row['purchases'], 'bal_qty')
        master_row['purchase_stcg_total'] = locale.format_string("%.2f", sum_by_key(master_row['purchases'], 'stcg'),
                                                                 grouping=True)
        master_row['purchase_ltcg_total'] = locale.format_string("%.2f", sum_by_key(master_row['purchases'], 'ltcg'),
                                                                 grouping=True)
        master_row['purchase_speculation_total'] = locale.format_string("%.2f", sum_by_key(master_row['purchases'],
                                                                                           'speculation'),
                                                                        grouping=True)
        master_row['sale_qty_total'] = sum_by_key(master_row['purchases'], 'sale_qty_total')
        master_row['sale_value_total'] = sum_by_key(master_row['purchases'], 'sale_value_total')
        master_row['sale_stcg_total'] = locale.format_string("%.2f",
                                                             sum_by_key(master_row['purchases'], 'sale_stcg_total'),
                                                             grouping=True)
        master_row['sale_ltcg_total'] = locale.format_string("%.2f",
                                                             sum_by_key(master_row['purchases'], 'sale_ltcg_total'),
                                                             grouping=True)
        master_row['sale_spec_total'] = locale.format_string("%.2f",
                                                             sum_by_key(master_row['purchases'], 'sale_spec_total'),
                                                             grouping=True)
        master_rows.append(master_row)
    grand_totals = {}
    grand_totals['purchase_qty_total'] = sum_by_key_ul(master_rows, 'purchase_qty_total')
    grand_totals['purchase_value_total'] = sum_by_key_ul(master_rows, 'purchase_value_total')
    grand_totals['purchase_bal_qty_total'] = sum_by_key_ul(master_rows, 'purchase_bal_qty_total')
    grand_totals['purchase_stcg_total'] = locale.format_string("%.2f", sum_by_key(master_rows, 'purchase_stcg_total'),
                                                               grouping=True)
    grand_totals['purchase_ltcg_total'] = locale.format_string("%.2f", sum_by_key(master_rows, 'purchase_ltcg_total'),
                                                               grouping=True)
    grand_totals['purchase_speculation_total'] = locale.format_string("%.2f", sum_by_key(master_rows,
                                                                                         'purchase_speculation_total'),
                                                                      grouping=True)
    grand_totals['sale_qty_total'] = sum_by_key_ul(master_rows, 'sale_qty_total')
    grand_totals['sale_value_total'] = sum_by_key_ul(master_rows, 'sale_value_total')
    grand_totals['sale_stcg_total'] = locale.format_string("%.2f", sum_by_key(master_rows, 'sale_stcg_total'),
                                                           grouping=True)
    grand_totals['sale_ltcg_total'] = locale.format_string("%.2f", sum_by_key(master_rows, 'sale_ltcg_total'),
                                                           grouping=True)
    grand_totals['sale_spec_total'] = locale.format_string("%.2f", sum_by_key(master_rows, 'sale_spec_total'),
                                                           grouping=True)
    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name
    description = 'Script Review Report ( ' + data['againstType'] + ' )' + " FY " + data['fy']
    context = {
        'masters': master_rows,
        'grand_totals': grand_totals,
        'heading': heading,
        'description': description,
        'pre_table': pre_table,
    }
    html = render_to_string('reports/script_review_report.html', context)
    # html = render_to_string('reports/test.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Script Review_Report.pdf"'

    pisaStatus = pisa.CreatePDF(html, dest=response)
    return response


@api_view(['GET'])
def portfolio_returns_report(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    purchases = TranSum.purchase_objects.filter(**data).order_by('part', 'trDate')
    total_purchase_value = purchases.aggregate(total_pur_value=Sum("sVal"))['total_pur_value']
    purchases_rows = []
    for purchase in purchases:
        pur_wtg = purchase.sVal / total_purchase_value * 100
        purchase_row = {
            "part": purchase.part,
            "pur_date": purchase.trDate.strftime("%d-%m-%Y"),
            "pur_qty": purchase.qty,
            "pur_rate": purchase.rate,
            "pur_value": purchase.sVal,
            "pur_wtg": pur_wtg,
            "sales_rows": []
        }
        sales = MOS_Sales.objects.filter(**data, purSno=purchase.sno, scriptSno=purchase.scriptSno).order_by("sDate")
        if len(sales) == 0:
            sale_row = {}
            sale_row['valuation_date'] = datetime.datetime.today().strftime("%d-%m-%Y")
            sale_row['days_held'] = (datetime.date.today() - purchase.trDate).days
            mkt_rate = services.get_market_rate_value(purchase.part)
            sale_row['sale_rate'] = mkt_rate
            sale_value = purchase.qty * mkt_rate
            sale_row['sale_value'] = sale_value
            profit = Decimal(sale_value) - purchase.sVal
            sale_row['profit'] = profit
            returns = profit / purchase.sVal
            sale_row['returns'] = returns
            per_day_return = returns / sale_row['days_held']
            sale_row['per_day_return'] = per_day_return
            annual_return = per_day_return * 365
            sale_row['annual_return'] = annual_return
            return_wtg = annual_return * pur_wtg
            sale_row['return_wtg'] = return_wtg
            return_perc = profit / purchase.sVal * 100
            sale_row['return_perc'] = return_perc
            ann_return_perc = returns / sale_row['days_held'] * 365
            sale_row['ann_return_perc'] = ann_return_perc
            wtg_ret = ann_return_perc * pur_wtg
            sale_row['wtg_ret'] = wtg_ret
            purchase_row['sales_rows'].append(sale_row)
        else:
            for sale in sales:
                sale_row = {}
                sale_row['valuation_date'] = sale.sDate.strftime("%d-%m-%Y")
                sale_row['days_held'] = (sale.sDate - purchase.trDate).days
                sale_row['sale_rate'] = sale.srate
                sale_row['sale_value'] = sale.sVal
                profit = sale.sVal - purchase.sVal
                sale_row['profit'] = profit
                returns = profit / purchase.sVal
                sale_row['returns'] = returns
                per_day_return = returns / sale_row['days_held']
                sale_row['per_day_return'] = per_day_return
                annual_return = per_day_return * 365
                sale_row['annual_return'] = annual_return
                return_wtg = annual_return * pur_wtg
                sale_row['return_wtg'] = return_wtg
                return_perc = profit / purchase.sVal * 100
                sale_row['return_perc'] = return_perc
                ann_return_perc = returns / sale_row['days_held'] * 365
                sale_row['ann_return_perc'] = ann_return_perc
                wtg_ret = ann_return_perc * pur_wtg
                sale_row['wtg_ret'] = wtg_ret
                purchase_row['sales_rows'].append(sale_row)
        purchases_rows.append(purchase_row)
    total_pur_qty = Decimal(0)
    total_pur_val = Decimal(0)
    total_annual_returns = Decimal(0)
    total_days_held = 0
    total_profit = Decimal(0)
    total_returns = Decimal(0)
    total_per_day_return = Decimal(0)
    total_return_wtg = Decimal(0)
    total_return_perc = Decimal(0)
    total_ann_return_perc = Decimal(0)
    total_return_wtg = Decimal(0)
    total_sale_value = Decimal(0)

    for purchase_row in purchases_rows:
        total_pur_qty += purchase_row['pur_qty']
        total_pur_val += purchase_row['pur_value']
        for sale_row in purchase_row['sales_rows']:
            total_sale_value += Decimal(sale_row['sale_value'])
            total_annual_returns += sale_row['annual_return']
            total_profit += sale_row['profit']
            total_returns += sale_row['returns']
            total_per_day_return += sale_row['per_day_return']
            total_return_wtg += sale_row['wtg_ret']
            total_return_perc += sale_row['return_perc']
            total_ann_return_perc += sale_row['ann_return_perc']
    total_ann_return_wtg_perc = Decimal(0)
    for purchase_row in purchases_rows:
        for sale_row in purchase_row['sales_rows']:
            sale_row['ann_return_wtg_perc'] = sale_row['annual_return'] / total_annual_returns * 100
            total_ann_return_wtg_perc += sale_row['ann_return_wtg_perc']
    result_df = pandas.DataFrame(
        columns=["Name of Script", "Purchase Date", "Qty", "PR", "PV", "Wtg", "Sale/Valuation Date", "Days Held", "SR",
                 "SV", "Profit", "Returns", "Per Day Return", "Annual Return", "Return Weightage", "Return Weightage %",
                 "Return %", "Wtg * Ret", "Ann Return %"])
    for index, purchase_row in enumerate(purchases_rows):
        sales_rows = purchase_row.pop('sales_rows')
        first_row = list({**purchase_row, **sales_rows[0]}.values())
        result_df = pandas.concat([result_df, pandas.DataFrame([first_row], columns=result_df.columns)],
                                  ignore_index=True)
        if len(sales_rows) > 1:
            for i in range(1, len(sales_rows)):
                blanks = numpy.full(6, numpy.nan).tolist()
                sale_line = list(sales_rows[i].values())
                result_df = pandas.concat(
                    [result_df, pandas.DataFrame([blanks + sale_line], columns=result_df.columns)],
                    ignore_index=True)
    totals_list = [numpy.nan, numpy.nan, total_pur_qty, numpy.nan, total_pur_val, 100, numpy.nan, total_days_held,
                   numpy.nan, total_sale_value, total_profit, total_returns, total_per_day_return, total_annual_returns,
                   total_return_wtg, 100, total_return_perc, total_return_wtg, total_ann_return_wtg_perc]
    result_df = pandas.concat(
        [result_df, pandas.DataFrame([totals_list], columns=result_df.columns)],
        ignore_index=True)

    for key in ["Qty", "PR", "PV", "Wtg", "SR", "SV", "Profit", "Returns", "Per Day Return", "Annual Return",
                "Return Weightage",
                "Return Weightage %", "Return %",
                "Wtg * Ret", "Ann Return %"]:
        result_df[key] = result_df[key].apply(localize)

    sio = BytesIO()
    PandasWriter = pandas.ExcelWriter(sio, engine='xlsxwriter')
    result_df.to_excel(PandasWriter, sheet_name="Sheet 1", index=False, na_rep=" ")
    for column in result_df:
        column_length = max(result_df[column].astype(str).map(len).max(), len(column))
        col_idx = result_df.columns.get_loc(column)
        PandasWriter.sheets['Sheet 1'].set_column(col_idx, col_idx, column_length)
    PandasWriter.save()
    sio.seek(0)
    workbook = sio.getvalue()
    response = HttpResponse(workbook,
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=%s' % "Portfolio_Returns_Report.xlsx"
    return response


def localize(x):
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    return locale.format_string("%.2f", float(x), grouping=True)


@api_view(['GET'])
def day_trading_report(request):
    data = request.query_params.dict()
    data['fy'] = data.pop('dfy')
    data['againstType'] = "Day Trading"
    name = ""
    if data.get('code'):
        member = MemberMaster.objects.filter(group=data['group'], code=data['code']).first()
        name = member.name
    else:
        group = CustomerMaster.objects.filter(group=data['group']).first()
        name = group.firstName + " " + group.lastName

    purchases = TranSum.purchase_objects.filter(**data).order_by('part', 'trDate')
    purchases_rows = []
    locale.setlocale(locale.LC_ALL, 'en_IN.utf8')
    for purchase in purchases:
        purchase_row = {
            "part": purchase.part,
            "pur_date": purchase.trDate.strftime('%d-%m-%Y'),
            "pur_qty": purchase.qty,
            "pur_rate": locale.format_string("%.2f", purchase.rate, grouping=True),
            "pur_value": locale.format_string("%.2f", purchase.sVal, grouping=True)
        }
        sale = MOS_Sales.objects.filter(**data, purSno=purchase.sno,
                                        scriptSno=purchase.scriptSno).first()
        purchase_row['sale_rate'] = locale.format_string("%.2f", sale.srate, grouping=True)
        purchase_row['sale_value'] = locale.format_string("%.2f", sale.sVal, grouping=True)
        purchase_row['speculation'] = locale.format_string("%.2f", sale.speculation, grouping=True)
        purchases_rows.append(purchase_row)

    pre_table = "Report Date : " + datetime.date.today().strftime('%d/%m/%Y')
    heading = name + " (FY " + data['fy'] + ")"
    description = 'Day Trading Report'
    context = {
        'heading': heading,
        'description': description,
        'pre_table': pre_table,
        'rows': purchases_rows,
        'post_table': " "
    }

    html = render_to_string('reports/day-trading-report.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Holding Report.pdf"'

    pisaStatus = pisa.CreatePDF(html, dest=response)
    return response


@transaction.atomic
@api_view(['POST'])
def shift_to_trading(request):
    data = copy.deepcopy(request.data)
    trId_list = data['trId']
    group = data['group']
    code = data['code']

    purchase_records = TranSum.purchase_objects.filter(trId__in=trId_list, group=group, code=code)

    for purchase in purchase_records:
        sno, scriptSno, current_againstType, part = purchase.sno, purchase.scriptSno, purchase.againstType, purchase.part
        master = TranSum.master_objects.filter(sno=scriptSno, againstType=current_againstType, group=group,
                                               code=code, part=part).first()
        purchase.againstType = "Trading"
        purchase.save()
        purchase.refresh_from_db()
        sales_queryset = MOS_Sales.objects.filter(group=group, code=code, purSno=sno, scriptSno=scriptSno,
                                                  fy=purchase.fy)
        values = {"againstType": purchase.sp, "purSno": purchase.sno, "scriptSno": purchase.scriptSno}
        sales_queryset.update(**values)
        master.save()

    return Response({"status": True, "message": "Purchases shifted to Trading"})


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


from django.core.files.storage import default_storage, FileSystemStorage


class DataExchangeView(APIView):

    def post(self, request):
        file_uploaded = request.FILES.get('file_uploaded')
        extension = file_uploaded.name.split(".")[1].lower()
        if extension != 'json':
            return Response({"status": False, "message": "Only JSON files are allowed"},
                            status=403)
        username = request.data['username']
        password = request.data['password']
        customer = authenticate(username=username, password=password)
        if customer:
            dir_name = "_".join([customer.group, customer.username])
            file_name = dir_name + "." + extension
            abs_path = "/".join(["customer_exports", dir_name, file_name])
            if default_storage.exists(abs_path):
                default_storage.delete(abs_path)
            saved_file = default_storage.save(abs_path, file_uploaded)
            return Response({"status": True, "message": "File uploaded successfully"},
                            status=200)
        else:
            return Response({"status": False, "message": "Authentication Failed. Please check your credentials"},
                            status=403)
        content_type = file_uploaded.content_type
        response = "POST API and you have uploaded a {} file".format(content_type) + file_uploaded.name
        return Response(response)

    def get(self, request):
        req = request.query_params.dict()
        group = req['group']
        customer = CustomerMaster.objects.filter(group=group).first()
        if customer:
            dir_name = "_".join([customer.group, customer.username])
            def_dirs, def_files = default_storage.listdir("customer_exports")
            if dir_name in def_dirs:
                dirs, files = default_storage.listdir("/".join(["customer_exports", dir_name]))
                return Response({"status": True, "message": "Files retrieved", "data": files},
                                status=200)
            else:
                return Response({"status": False, "message": "No files present."},
                                status=200)


@api_view(['POST'])
@transaction.atomic()
def import_data(request):
    group = request.data['group']
    file_name = request.data['file_name']
    dir_name = "_".join([request.data['group'], request.data['username']])
    try:
        dirs, files = default_storage.listdir("/".join(["customer_exports", dir_name]))
        if file_name in files:
            with default_storage.open("/".join(["customer_exports", dir_name, file_name]), mode='r') as import_file:
                import_data = json.loads(import_file.read())
            if len(import_data) < 0:
                return Response({"status": False, "message": "Selected import file was empty."})

            old_purchase_set = TranSum.objects.filter(group=group)
            old_purchase_set.delete()
            old_sale_set = MOS_Sales.objects.filter(group=group)
            old_sale_set.delete()

            for purchase in import_data:
                if purchase['trDate'] == "":
                    purchase['trDate'] = None
                if purchase['sp'] == '':
                    continue
                purchase_obj = TranSum(group=group, code=purchase['code'], part=purchase['part'],
                                       fy=purchase['fy'],
                                       trDate=datetime.datetime.strptime(purchase['trDate'], '%d/%m/%Y %H:%M:%S') if
                                       purchase[
                                           'trDate'] is not None else None,
                                       againstType=AGAINST_TYPE_MAP[purchase['againstType']], sp=purchase['sp'],
                                       qty=purchase['qty'],
                                       sVal=purchase['sVal'], rate=purchase['rate'], fmr=purchase['fmr'],
                                       isinCode=purchase['isinCode'], empCode=purchase['empCode'],
                                       sttCharges=purchase['sttCharges'], otherCharges=purchase['otherCharges'],
                                       noteAdd=purchase['noteAdd'])

                purchase_obj.save()
                purchase_obj.refresh_from_db()
                for sale in purchase['sales']:
                    if sale['sDate'] == "":
                        sale['sDate'] = None
                    sale_obj = MOS_Sales(group=group, code=purchase['code'],
                                         sDate=datetime.datetime.strptime(sale['sDate'], '%d/%m/%Y %H:%M:%S'),
                                         srate=sale['srate'],
                                         sqty=sale['sqty'], sVal=sale['sVal'], purSno=purchase_obj.sno,
                                         scriptSno=purchase_obj.scriptSno,
                                         againstType=sale['againstType'],
                                         stt_Paid=sale['stt_Paid'], stt=sale['stt'], other=sale['other'],
                                         fno=sale['fno'], empCode=sale['empCode'])
                    sale_obj.group = purchase_obj.group
                    sale_obj.purSno = purchase_obj.sno
                    sale_obj.scriptSno = purchase_obj.scriptSno
                    sale_obj.save()

            return Response({"status": True, "message": "File import initiated successfully."})
        else:
            return Response({"status": False, "message": "File not found. Please check the name of the file."})
    except Exception as e:
        raise e
        return Response({"status": False, "message": "Error while importing file."})


import pyotp
import base64
from django.core.mail import send_mail


@api_view(['GET'])
def get_otp(request):
    data = request.query_params.dict()
    email = data['email']
    key = base64.b32encode(email.encode())
    otp = pyotp.TOTP(key, digits=6, interval=180)
    otp_str = otp.now()
    send_mail(
        'Your One-time Password for changing your password on the MOS app.',
        'Your One-time Password for changing your password on the MOS app is ' + otp_str,
        'otp@sinewave.co.in',
        [email],
        fail_silently=False,
    )
    return Response({"status": True,
                     "message": "A mail was sent to your registered email address. Please enter the one-time password it contains."})


@api_view(['GET'])
def verify_otp(request):
    data = request.query_params.dict()
    email = data['email']
    otp_str = data['otp']
    key = base64.b32encode(email.encode())
    otp = pyotp.TOTP(key, digits=6, interval=180)
    if otp.verify(otp_str):
        set_pass_key = base64.b32encode((email + otp_str).encode())
        set_pass_token = pyotp.TOTP(set_pass_key, digits=6, interval=180).now()
        return Response({"status": True, "pass_token": set_pass_token})
    else:
        return Response({"status": False,
                         "pass_token": "Incorrect OTP. This might be expired please generate a new one and try again"})


@api_view(['POST'])
def set_password(request):
    email = request.data['email']
    set_pass_token = request.data['pass_token']
    password = request.data['password']
    otp_str = request.data['otp']
    set_pass_key = base64.b32encode((email + otp_str).encode())
    set_pass_otp = pyotp.TOTP(set_pass_key, digits=6, interval=180)
    if set_pass_otp.verify(set_pass_token):
        customer = CustomerMaster.objects.get(emailId=email)
        customer.set_password(password)
        return Response({"status": True, "message": "Password reset complete"})
    else:
        return Response({"status": False, "message": "Password reset session has expired. Please try again."})


def round_to_100_percent(number_set, digit_after_decimal=2):
    """
        This function take a list of number and return a list of percentage, which represents the portion of each number in sum of all numbers
        Moreover, those percentages are adding up to 100%!!!
        Notice: the algorithm we are using here is 'Largest Remainder'
        The down-side is that the results won't be accurate, but they are never accurate anyway:)
    """

    if len(number_set) == 0:
        return None

    if sum(number_set) == 0:
        return [0] * len(number_set)

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
