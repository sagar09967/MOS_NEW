from rest_framework import serializers
from .models import TranSum,CustomerMaster,MemberMaster
from django.contrib.auth.hashers import make_password


 # ---------------------- Saving API
class SavePurchSerializer(serializers.ModelSerializer):
    class Meta:
        model=TranSum
        fields=('trId','group','code','fy','againstType','sp','part','fmr','isinCode','trDate','qty','rate','sVal','sttCharges','otherCharges','noteAdd','balQty','marketRate')
# ------------------------ Retriveing API
class RetTransSumSerializer(serializers.ModelSerializer):
    class Meta:
        model=TranSum
        fields=['trId','trDate','qty','balQty','rate','sVal','sttCharges','otherCharges','noteAdd']

# ------------------------ Retrivng API Screen No2 (opening, addition, closing)
class TranSumRetrivesc2Serializer(serializers.ModelSerializer):
    class Meta:
        model=TranSum
        fields=['fmr','isinCode']
    
    
# class RetInvSc1serializer(serializers.ModelSerializer):
#     class Meta:
#         model=TranSum
#         fields=['trId','part','marketValue']

# ---------------------- Member saving API
class SaveMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model=MemberMaster
        fields=['group','name','code','emailId','contactNo']

# # -----------------------RetMember api
class RetMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model=MemberMaster
        fields=['memberId','name','emailId','contactNo']

class SavecustomerSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    class Meta:
        model=CustomerMaster
        fields=['userId','username','group','firstName','lastName','emailId','contactNo','dob','photo','address','active','companyCode','sw_CustomerId','registration_Date','valid_Date','password','password2']
      
        extra_kwargs = {
            'password': {'write_only':True}
        }
  
    #------------------Validating  Password and ConformPasswordwhie Registration

    def create(self, validated_data):
        if validated_data.get('password') != validated_data.get('password2'):
            raise serializers.ValidationError("Those password don't match") 

        elif validated_data.get('password') == validated_data.get('password2'):
            validated_data['password'] = make_password(
                    validated_data.get('password')
                )

        validated_data.pop('password2') # add this
        return super(SavecustomerSerializer, self).create(validated_data)

# ------------------------------- Sales Api Serializer (Sales)
class RetTransSumSalesSerializer(serializers.ModelSerializer):
    class Meta:
        model=TranSum
        fields=['trId','trDate','qty','rate','sVal','balQty']







        
    