from decimal import Decimal
from .models import TranSum, MemberMaster, CustomerMaster, MOS_Sales
from rest_framework import generics
from rest_framework import status
from django.db.models import Sum, Q, F
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
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
        serializer.is_valid()
        object = serializer.save()
        serializer = serializers.RetrieveTranSumSerializer(object)
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

        try:
            start_fy = f"{dfy[:4]}-04-01"
            end_fy = f"{dfy[5:]}-03-31"
        except:
            raise Http404

        serializer = serializers.SalePurchaseSerializer(queryset, many=True)
        purchase_data = serializer.data
        for i in range(0, len(purchase_data)):
            sales = MOS_Sales.objects.filter(group=purchase_data[i]['group'], code=purchase_data[i]['code'],
                                             purSno=purchase_data[i]['sno'], scriptSno=purchase_data[i]['scriptSno'])
            totalSoldQty = list(sales.aggregate(Sum('sqty')).values())[0]
            stcg = list(sales.aggregate(Sum('stgc')).values())[0]
            ltcg = list(sales.aggregate(Sum('ltgc')).values())[0]
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
            serializer.is_valid()
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
        sum_opening = list(openings.aggregate(Sum('balQty')).values())[0]
        additions = purchases.filter(trDate__range=(from_date, to_date))
        sum_addition = list(additions.aggregate(Sum('balQty')).values())[0]
        sales = MOS_Sales.objects.filter(group=group, code=code, scriptSno=master['sno'])
        sum_sales = list(sales.aggregate(Sum('sqty')).values())[0]
        holding['opening'] = 0 if sum_opening is None else int(sum_opening)
        holding['addition'] = 0 if sum_addition is None else int(sum_addition)
        holding['sales'] = 0 if sum_sales is None else int(sum_sales)
        holding['closing'] = holding['opening'] + holding['addition']
        holdings.append(holding)

    return Response({'status': True, 'msg': 'Retrieved Holdings', 'data': holdings})


def sum_by_key(records, key):
    sum_result = 0
    for record in records:
        sum_result = sum_result + getattr(record, key)
    return sum_result
