from .models import TranSum
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.views import APIView
from .serializers import RetTransSumSalesSerializer,RetSalesDetSerializer,SaleSaveAPISerializer

# ------------------------------- RetSalesSum API
class RetSaleSum(APIView):
    def get(self,request,format=None):
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        part = self.request.query_params.get('part')
        againstType = self.request.query_params.get('againstType')
        dfy = self.request.query_params.get('dfy')
        sales=TranSum.objects.filter(group=group,code=code,part=part,againstType=againstType)
        serializer = RetTransSumSalesSerializer(sales, many=True)
        return Response({'status':True,'msg': 'done','data':serializer.data})

#---------------------------------SalesSaveAPI
class SaleSaveAPI(APIView):
    def post(self, request, format=None):
        serializer = SaleSaveAPISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save() 
            return Response({'status':True,'msg': 'You have successfully Created','data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# -------------------------------RetSalesDet API
class RetSalesDet(APIView):
    def get(self,request,format=None):
        group = self.request.query_params.get('group')
        code = self.request.query_params.get('code')
        dfy = self.request.query_params.get('dfy')
        againstType = self.request.query_params.get('againstType')
        mos_transum=TranSum.objects.filter(group=group,code=code,fy=dfy,againstType=againstType)
        serializer=RetSalesDetSerializer(mos_transum,many=True)
        return Response({'status':True,'msg':'done','data':serializer.data})
