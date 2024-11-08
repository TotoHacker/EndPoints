from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

    
class Post_APIView(APIView):    
    def get(self, request, format=None, *args, **kwargs):
        return Response([],status=status.HTTP_200_OK)