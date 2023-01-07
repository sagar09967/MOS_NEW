from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework import viewsets, generics
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
from .models import Feedback, ReleaseNote, Post


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = serializers.FeedbackSerializer

    def list(self, request):
        data = request.query_params.dict()
        queryset = Feedback.objects.filter(group=data['group'])
        serializer = serializers.FeedbackSerializer(queryset, many=True)

        return Response({'status': True, 'message': 'Retrieved Feedbacks', 'data': serializer.data})

    def create(self, request):
        response = super(FeedbackViewSet, self).create(request=request)
        return Response({'status': True, 'message': 'Created Feedback', 'data': response.data})


class ReleaseNoteList(generics.ListAPIView):
    queryset = ReleaseNote.objects.all()
    serializer_class = serializers.ReleaseNoteSerializer

    def list(self, request, *args, **kwargs):
        response = super(ReleaseNoteList, self).list(request=request)
        return Response({'status': True, 'message': 'Retrieved Release Notes', 'data': response.data})


class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer

    def list(self, request, *args, **kwargs):
        response = super(PostList, self).list(request=request)
        return Response({'status': True, 'message': 'Retrieved Posts', 'data': response.data})
