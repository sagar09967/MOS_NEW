from .models import TranSum
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.views import APIView
from .serializers import RetTransSumSalesSerializer

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