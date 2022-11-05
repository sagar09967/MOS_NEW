from decimal import Decimal
from .models import TranSum,MemberMaster,CustomerMaster
from rest_framework import generics
from rest_framework import status
from django.db.models import Sum,Q
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404
from rest_framework.views import APIView
from .serializers import (SavePurchSerializer,RetTransSumSerializer,
SaveMemberSerializer,RetMemberSerializer,SavecustomerSerializer,RetChangeDefaultSerializer,CustomerLoginSerializer)
import copy
from django.contrib.auth import authenticate
from .renderers import UserRender

# -------------------- SavePurch API
class SavePurch(APIView):
    def post(self, request, format=None):
        dic = copy.deepcopy(request.data)
        dic["balQty"] = request.data["qty"]
        serializer = SavePurchSerializer(data=dic)
        if serializer.is_valid():
            serializer.save() 
            return Response({'status':True,'msg': 'You have successfully Created','data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------- RetTransSum API
class RetTransSum(generics.ListAPIView):
    queryset=TranSum.objects.all()
    serializer_class=RetTransSumSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['group','code','againstType','part']

    # -------------------- Overriding Queryset
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
            
        elif option=='A':
            
            return self.queryset.filter(trDate__range=(start_fy,end_fy))
             
             
#   ------------------------- Update and Retrive API
class RetTransSumUpdate(generics.RetrieveUpdateAPIView):
    queryset=TranSum.objects.all()
    serializer_class=RetTransSumSerializer
    def update(self, request, *args, **kwargs):
       oldqty = self.request.query_params.get('oldqty')
       balqty = self.request.query_params.get('balqty')

       old = 0 if oldqty is None else oldqty
       balQ = 0 if balqty is None else balqty

       dict_ls =  copy.deepcopy(request.data)
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
        "data":dict_ls
        
       }
       return Response(result)

 # -------------------------- Retrive API Screen No Two
 
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
        opening=TranSum.objects.values('qty','sVal','marketRate','marketValue','isinCode','fmr','avgRate').order_by().annotate(opening=Sum("qty"),opval=Sum("sVal")).filter(trDate__lt=start_fy,group=group,code=code,againstType=againstType,part=part)
        addition=TranSum.objects.values('qty','sVal','marketRate','marketValue','isinCode','fmr','avgRate').order_by().annotate(addition=Sum("qty"),adval=Sum("sVal")).filter(trDate__range=(start_fy,end_fy),group=group,code=code,againstType=againstType,part=part)
        
        for opp in opening:
            opdic={'opening':opp['opening'],'opval':int(opp['opval']),'isinCode':opp['isinCode'],'fmr':opp['fmr']}

        # -------------------- all_opening
        try:
            all_opening=opdic['opening']
        except:
            all_opening=0

        #---------------------- all opening value Addition
        try:
            val_add_opening=opdic['opval']
        except:
            val_add_opening=0

        # print("value addtion--->",vall_add)

        #---------------- isin Code
        try: 
            isin_Code=opdic['isinCode']
        except:
            isin_Code=0

        # -------------- Fmr Code
        try:
            fmr_l=opdic['fmr']
        except:
            fmr_l=0


        for add in addition:
            adddic={'addition':add['addition'],'addval':int(add['adval'])}
        # print("adddd",adddic)
         
        # -------------------->all_addition
        # all_addition = 0 if add['addition'] is None else add['addition']
        try:
            all_addition=adddic['addition']
        except:
            all_addition=0

        # -------------------> all Addition value
        try:
            all_add_value=adddic['addval']
        except:
            all_add_value=0

        # print("All Value--->",all_add_value)
    
        # ----------------------> closing
        try:
            closing=all_opening+all_addition
            # print("Closing---->",closing)
        except:
            closing=0


        # ---------------------->opening_addition_value(Investment Value)
        opening_addition_val=val_add_opening+all_add_value
        opening_addition_val=float(opening_addition_val)
        # print(opening_addition_val)

        #------------------------->Average Rate
        try:
            avg_Rate=opening_addition_val/closing
        except:
            avg_Rate=0
        # ------------------------ Market 
        data={
            "isin_Code":isin_Code,
            "fmr":fmr_l,
            "opening":all_opening,
            "addition":all_addition,
            "closing":closing,
            "InvValue":opening_addition_val,
            "avgRate":avg_Rate
        }
        # print("RetTranSum----->",data)
        return Response({'status':True,'msg':'done','data':data})

class RetHolding(APIView):
    def get(self,request,format=None):
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        dfy = self.request.query_params.get('dfy')
        againstType = self.request.query_params.get('againstType')
        holding=TranSum.objects.values('part','rate','marketRate').order_by().annotate(HoldQty=Sum("balQty")).filter(group=group,code=code,againstType=againstType,fy=dfy)
        data_ls = []
        for data in holding:
            dic = {'part': data['part'],'holdQty':int(data['HoldQty'])}
            hodQty = 0 if data['HoldQty'] is None else data['HoldQty']
            mktrate = 0 if data['marketRate'] is None else data['marketRate']
            dic["InvValue"] = (hodQty)*data['rate']
            dic["mktValue"] = (hodQty)*(mktrate)
            data_ls.append(dic)
        print('------------------------------')
        print("Holding---_",data_ls)
        print('------------------------------')
        return Response({'status':True,'msg':'done','data':data_ls})

# -------------------------- SaveMember api
class SaveMember(APIView):
    def post(self, request, format=None):
        try:
            mem=MemberMaster.objects.filter(group=request.data['group']).latest('code')
        except:
          mem ='00000'
        # print("Member-->",mem)
        if mem==None or 0:
            me=mem+1
            code=me.zfill(5)
        else:
            cp=mem
            cpp=str(cp)
            cpp=int(cpp)+1
            code=str(cpp).zfill(5)
        request.data['code'] = code

        # print("Code --->",code) 
        # print("requ code",request.data.get("code"))
        
        serializer = SaveMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':True,'Message': 'You have successfully Created','data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # -------------------------- RetMember API
class RetMember(APIView):
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        member=MemberMaster.objects.filter(group=group)
        serializer=RetMemberSerializer(member,many=True)
        return Response({'status':True,'msg':'done','data':serializer.data})

# ---------------------------- updated delete api mrmber
class MemberUpdadeDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset=MemberMaster.objects.all()
    serializer_class=SaveMemberSerializer

# -------------------------- SaveCutomer api
class SaveCustomer(APIView):
    def post(self, request,format=None):       
        gro=CustomerMaster.objects.latest('group')
        if gro==None or 0:
            ss=gro+1
            group=ss.zfill(5)
        else:
            gp=gro
            gpp=str(gp)
            gpp=int(gpp)+1
            group=str(gpp).zfill(5)
        # print("groupp",group)
           
        request.data['group'] = group       
        # print("requ grp",request.data.get("group"))
        serializer = SavecustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':True,'msg': 'You have successfully Created','data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 # -------------------------- RetCustomer API
class RetCustomer(APIView):
    def get(self, request, format=None):
        username = self.request.query_params.get('username')
        customer=CustomerMaster.objects.filter(username=username)
        serializer=SavecustomerSerializer(customer,many=True)
        return Response({'status':True,'msg':'done','data':serializer.data})

# ---------------------------- updated delete api Customer
class CustomerUpdadeDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset=CustomerMaster.objects.all()
    serializer_class=SavecustomerSerializer

# --------------------------------- Login Customer Master Api

class CustomerLogin(APIView):
    def post(self,request,format=None):
        serializer=CustomerLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username=serializer.data.get('username')
            password=serializer.data.get('password')
            user=authenticate(username=username,password=password)
            if user is not None: 
                return Response({'status':True,'msg':'Login Success','data':serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':['Username or Password is not Valid']}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                
class RetChangeDefault(APIView):
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        member=MemberMaster.objects.filter(group=group)
        serializer=RetChangeDefaultSerializer(member,many=True)
        return Response({'status':True,'msg':'done','data':serializer.data})
    
  
