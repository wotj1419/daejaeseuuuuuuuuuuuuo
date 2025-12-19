from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate

from .serializers import UserRegistrationSerializer, UserSerializer

User = get_user_model()


class UserRegistrationAPIView(generics.CreateAPIView):
    """회원가입 API"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': '회원가입이 완료되었습니다.'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """로그인 API"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': '사용자명과 비밀번호를 입력해주세요.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # JWT 토큰 생성
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },
        'message': '로그인 성공'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """로그아웃 API (토큰 블랙리스트)"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': '로그아웃되었습니다.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': '로그아웃 중 오류가 발생했습니다.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile_view(request):
    """현재 사용자 정보 조회"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def user_profile_update_view(request):
    """현재 사용자 정보 수정"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
