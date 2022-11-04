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

import itertools


# -------------------- SavePurch API
class SavePurch(APIView):
    # renderer_classes=[UserRender]   
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
            # start_fy=dfy[:4]+"-04-01"
            start_fy = f"{dfy[:4]}-04-01"
            # end_fy=dfy[5:]+"-03-31"
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
    #    transid = self.request.query_params.get('transid')
 
    #    print(oldqty,balqty)
       old = 0 if oldqty is None else oldqty
       balQ = 0 if balqty is None else balqty

       
       dict_ls =  copy.deepcopy(request.data)
       print(dict_ls)
       dict_ls["balQty"] = int(balQ) - int(old) + int((dict_ls["qty"]))

    #    print(dict)

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

 # Retrive API Screen No Two
 
class RetScriptSum(APIView):
    def get(self, request, format=None):
        # ------------ fetching parameter in  Url
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        againstType = self.request.query_params.get('againstType')
        part = self.request.query_params.get('part')
        dfy = self.request.query_params.get('dfy')
        try:
            # start_fy=dfy[:4]+"-04-01"
            start_fy = f"{dfy[:4]}-04-01"
            # end_fy=dfy[5:]+"-03-31"
            end_fy = f"{dfy[5:]}-03-31"
        except:
            raise Http404
        # --------------------- Opening
        opening=TranSum.objects.values('qty','sVal','marketRate','marketValue','isinCode','fmr','avgRate').order_by().annotate(opening=Sum("qty"),opval=Sum("sVal")).filter(trDate__lt=start_fy,group=group,code=code,againstType=againstType,part=part)
        addition=TranSum.objects.values('qty','sVal','marketRate','marketValue','isinCode','fmr','avgRate').order_by().annotate(addition=Sum("qty"),adval=Sum("sVal")).filter(trDate__range=(start_fy,end_fy),group=group,code=code,againstType=againstType,part=part)
        
        print('----------------')
        for opp in opening:
            opdic={'opening':opp['opening'],'opval':int(opp['opval']),'isinCode':opp['isinCode'],'fmr':opp['fmr']}


        # -------------------- all_opening
        all_opening=opdic['opening']
        #---------------------- all opening value Addition
        val_add_opening=opdic['opval']
        # print("value addtion--->",vall_add)

        #---------------- isin Code
        isin_Code=opdic['isinCode']

        # -------------- Fmr Code
        fmr_l=opdic['fmr']

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
            print("Closing---->",closing)
        except:
            closing=0


        # ---------------------->opening_addition_value(Investment Value)
        opening_addition_val=val_add_opening+all_add_value
        opening_addition_val=float(opening_addition_val)
        # print(opening_addition_val)

        #------------------------->Average Rate
        avg_Rate=opening_addition_val/closing

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
        return Response({'status':True,'msg':'done','data':data})

       
        # opening = TranSum.objects.filter(trDate__lt=start_fy,group=group,code=code,againstType=againstType,part=part).values_list('qty','sVal','isinCode','fmr')
        # op_list=list(opening)
        # varop=0
        # varopval=0
        # for i in op_list:
        #     op=int(i[0])
        #     opval=int(i[1])
        #     varop=varop+op
        #     # varopval=varopval+opval 
        #     varopval=varopval+opval

     
        # # --------------------- Additions
        # addition = TranSum.objects.filter(trDate__range=(start_fy,end_fy),group=group,code=code,againstType=againstType,part=part).values_list('qty','sVal','marketRate','marketValue','isinCode','fmr','avgRate')
        # # print("Daaaa",addition)
        # b=list(addition)
        # # print(b)
        # varadd=0
        # varaddval=0
        # for i in b:
        #     ad=int(i[0])
        #     addval=int(i[1])
        #     mktRate=(i[2])
        #     mktvalue = 0 if i[3] is None else i[3]
    
        #     iscode = 0 if i[4] is None  else i[3]
        #     fmr=i[5]
        #     varadd=varadd+ad
        #     varaddval=varaddval+addval
      

            
        # # ------------------------- Closing
        # closing=varadd+varop
        # # #-------------------------- opening and addition all values Sum
        # InvValue=varaddval+varopval
       
        # InvValue=float(InvValue)

        # # -------------------------- Average Rate(total values / total qty)(InvValue/closing)
        # try:
        #     avgRate=InvValue / closing
        #     avgRate=round(avgRate,2)
        # except ZeroDivisionError:
        #     avgRate=0
        # # print('Avg',avgRate,type(avgRate))
       

        # # print("avgRate----->",avgRate)
        
        # context={
        #     # 'isinCode':iscode,
        #     # 'fmr':fmr,
        #     'opening':varop,
        #     'addition':varadd,
        #     'sales':0,
        #     'closing':closing,
        #     'invValue':InvValue,
        #     'avgRate':avgRate,
        #     # 'marketRate':mktRate,
        #     # 'mktvalue':mktvalue
        # }
        # return Response({'status':True,'msg':'done','data':data})

class RetHolding(APIView):
    def get(self,request,format=None):
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        dfy = self.request.query_params.get('dfy')
        againstType = self.request.query_params.get('againstType')
        # all_data = TranSum.objects.filter(group=group,code=code,againstType=againstType,fy=dfy).values_list('rate','balQty','marketRate','part')
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


        # data_ls = []
        # for data in all_data:
        #     dic = {'part': data[3], "holdQty": int(data[1])}
        #     data_1 = 0 if data[1] is None else data[1]
        #     data_2 = 0 if data[2] is None else data[2]
        #     dic["InvValue"] = float((data[0]))* (int(data_1))
        #     dic["mktvalue"] = float(data_1 * (data_2))
        #     # print("Dataaaa--->",dic)
        #     data_ls.append(dic)
        # print(data_ls)
        
        # import pandas as pd
        # import json
        # df = pd.DataFrame(data_ls)
        # df = df.groupby('part').sum()
        # print(df,type(df))

        # df = pd.DataFrame(data_ls)
        # print(df)
        # df = df.groupby('part').sum()
        # print(df,type(df))
        # df2 = df.to_json(orient ='values')
        # df2 = df.to_json(orient = 'table')
        # df2 = df.to_json(orient = 'split')
        # df2 = df.to_json(orient ='index')
        # df = df.to_json(orient = 'records')
        # df2 = df.to_json(orient = 'columns')  

        # print(df,type(df))
        # ss=df.to_json(orient='records')
        # print("------------------")
        # print(ss,type(ss))
       
        # final_data = [(a, list(b)) for a, b in itertools.groupby([i.items() for i in data_ls], key=lambda x:dict(x)["part"])] 
        # new_final_data = [{i[0][0]:sum(c[-1] for c in i if isinstance(c[-1],Decimal)) if i[0][0] != "part" else i[0][-1] for i in zip(*b)} for a, b in final_data]
        # # print('---------------------------')
        # print('Data------>',new_final_data)
        # print('---------------------------')
       
        # holding=df.groupby('part').sum()
       
        # print('out---',out)

        # return Response({'status':True,'msg':'done'})



# -------------------------- SaveMember api
class SaveMember(APIView):
    # renderer_classes=[UserRender]
    def post(self, request, format=None):
        try:
            mem=MemberMaster.objects.filter(group=request.data['group']).latest('code')
        except:
          mem ='00000'
        print("Member-->",mem)
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

# ----------------------Generate Token Manually
# def get_tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)

#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#     }


# -------------------------- SaveCutomer api
class SaveCustomer(APIView):
   
    # renderer_classes=[UserRender]
    def post(self, request,format=None):       
        stu=CustomerMaster.objects.latest('group')
        if stu==None or 0:
            ss=stu+1
            group=ss.zfill(5)
        else:
            gp=stu
            gpp=str(gp)
            gpp=int(gpp)+1
            group=str(gpp).zfill(5)
        # print(group,type(group))
        # print("groupp",group)
           
        # request.data['group'] = group 
        request.data['group'] = group       
        # print("requ grp",request.data.get("group"))
        serializer = SavecustomerSerializer(data=request.data)
       
        if serializer.is_valid():
            serializer.save()
            # calling function token
            # token=get_tokens_for_user(user)
             # print("Serializer---->",serializer.data)
            return Response({'status':True,'msg': 'You have successfully Created','data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 # -------------------------- RetCustomer API
class RetCustomer(APIView):
    # queryset=CustomerMaster.objects.all()
    # serializer_class=SavecustomerSerializer
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
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAuthenticated]
    renderer_classes=[UserRender]
    def post(self,request,format=None):
        serializer=CustomerLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username=serializer.data.get('username')
            password=serializer.data.get('password')
            firstName=serializer.data.get('firstName')
            print("fies name",firstName)
            user=authenticate(username=username,password=password,firstName=firstName)
           
          
            if user is not None: 
                # token=get_tokens_for_user(user)
                return Response({'status':True,'msg':'Login Success','data':serializer.data},status=status.HTTP_200_OK)
            else:
                return Response({'errors':{'non_field_errors':['Username or Password is not Valid']}},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                


class RetChangeDefault(APIView):
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        group = self.request.query_params.get('group')
        member=MemberMaster.objects.filter(group=group)
        serializer=RetChangeDefaultSerializer(member,many=True)
        return Response({'status':True,'msg':'done','data':serializer.data})


