from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import InstructorRegisterSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class InstructorRegisterView(APIView):
    def post(self, request):
        serializer = InstructorRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "message": "Instructor registered successfully"
        })
class InstructorLoginView(APIView):
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password")
        )

        if user and user.role == 'instructor':
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            })

        return Response({
            "error": "Invalid instructor credentials"
        }, status=400)