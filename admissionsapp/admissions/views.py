from rest_framework import viewsets, generics, parsers, permissions, status
from rest_framework.permissions import AllowAny
from .models import (
    Category, Course, User, Lesson, Tag, Post, Post_category, Comments, Comment, University_info, Livestream_info,
    Questions, Falcuty, Major, Slider, Rating, Like
)
from .serializers import (
    CategorySerializer, CourseSerializer, LessonSerializer, UserSerializer, LessonDetailSerializer, PostSerializer,
    PostCategorySerializer, CommentsSerializer, CommentSerializer, UniversitySerializer, LivestreamSerializer,
    QuestionsSerializer, FalcutySerializer, MajorSerializer, SliderSerializer
)
from .paginators import CoursePaginator
from rest_framework.decorators import action
from rest_framework.views import Response
from .perms import CommentOwner
import math
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse


# Custom generic response oauth2
class ApiEndpoint(ProtectedResourceView):
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "note": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def filter_queryset(self, queryset):
        kw = self.request.query_params.get('kw')
        if self.action.__eq__('list') and kw:
            queryset = queryset.filter(subject__icontains=kw)

        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            queryset = queryset.filter(category_id=cate_id)

        return queryset

    @action(methods=['get'], detail=True, url_path='lessons')
    def lessons(self, request, pk):
        c = self.get_object()
        lessons = c.lesson_set.filter(active=True)

        kw = request.query_params.get('kw')
        if kw:
            lessons = lessons.filter(subject__icontains=kw)

        return Response(LessonSerializer(lessons, many=True).data)


class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.filter(active=True)
    serializer_class = LessonDetailSerializer

    def get_permissions(self):
        if self.action in ['comments', 'like']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['post'], detail=True, url_path='tags')
    def assign_tags(self, request, pk):
        lesson = self.get_object()
        tags = request.data['tags']
        for t in tags:
            tag, _ = Tag.objects.get_or_create(name=t)
            lesson.tags.add(tag)
        lesson.save()

        return Response(LessonDetailSerializer(lesson, context={'request': request}).data)

    @action(methods=['post'], detail=True, url_path='comments')
    def comments(self, request, pk):
        lesson = self.get_object()
        c = Comment(content=request.data['content'], lesson=lesson, user=request.user)
        c.save()

        return Response(CommentSerializer(c).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, url_path='like')
    def like(self, request, pk):
        lesson = self.get_object()
        l, created = Like.objects.get_or_create(lesson=lesson, user=request.user)
        if not created:
            l.liked = not l.liked
        l.save()

        return Response(status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='rating')
    def rate(self, request, pk):
        lesson = self.get_object()
        r, _ = Rating.objects.get_or_create(lesson=lesson, user=request.user)
        r.rate = request.data['rate']
        r.save()

        return Response(status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet,
                  generics.ListAPIView,
                  generics.CreateAPIView,
                  generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [parsers.MultiPartParser, ]

    # permission_classes = [permissions.IsAuthenticated]

    # Set quyen xem thong tin user:
    def get_permissions(self):
        if self.action == 'current_user':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get', 'put'], detail=False, url_path='current-user')
    def current_user(self, request):
        u = request.user
        if request.method.__eq__('PUT'):
            for k, v in request.data.items():
                if k.__eq__('password'):
                    u.set_password(k)
                else:
                    setattr(u, k, v)
            u.save()
        return Response(self.serializer_class(request.user).data)

    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_falcuty(self, request, pk):
        try:
            u = User.objects.get(pk=pk)
            u.status = False
            u.save()
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=UserSerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [CommentOwner()]

        return [permissions.AllowAny()]


# Thong tin truong
class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University_info.objects.filter(status=True)
    serializer_class = UniversitySerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]

    # viet schema cho redoc
    @swagger_auto_schema(
        operation_description='Tắt trạng thái 1 thông tin của trường',
        responses={
            status.HTTP_200_OK: UniversitySerializer()
        }
    )
    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_university(self, request, pk):
        try:
            u = University_info.objects.get(pk=pk)
            u.status = False
            u.save()
        except University_info.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=UniversitySerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# Danh muc bai post
class PostCategoryViewSet(viewsets.ModelViewSet):
    queryset = Post_category.objects.filter(status=True)
    serializer_class = PostCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]

        return [permissions.IsAuthenticated()]

    def get(self, request):
        page_num = int(request.GET.get("page", 1))
        limit_num = int(request.GET.get("limit", 1000))
        start_num = (page_num - 1) * limit_num
        end_num = limit_num * page_num
        search_param = request.GET.get("search")
        data = Post_category.objects.all()
        total_data = data.count()
        if search_param:
            data = data.filter(title__icontains=search_param)
        serializer = self.serializer_class(data[start_num:end_num], many=True)
        return Response({
            "status": "success",
            "total": total_data,
            "page": page_num,
            "last_page": math.ceil(total_data / limit_num),
            "data": serializer.data
        })

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "note": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_post_category(self, request, pk):
        try:
            u = Post_category.objects.get(pk=pk)
            u.status = False
            u.save()
        except Post_category.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=PostCategorySerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# Bai post
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status=True)
    serializer_class = PostSerializer

    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_post(self, request, pk):
        try:
            u = Post.objects.get(pk=pk)
            u.status = False
            u.save()
        except Post.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=PostSerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# Binh luan cua thi sinh
class CommentsViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsAuthenticated]


# Thong tin cua livestream
class LivestreamViewSet(viewsets.ModelViewSet):
    queryset = Livestream_info.objects.filter(status=True)
    serializer_class = LivestreamSerializer

    # permission_classes = [permissions.IsAuthenticated]

    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_livestream(self, request, pk):
        try:
            u = Livestream_info.objects.get(pk=pk)
            u.status = False
            u.save()
        except Livestream_info.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=LivestreamSerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# Tong hop cau hoi
class QuestionsViewSet(viewsets.ModelViewSet):
    queryset = Questions.objects.all()
    serializer_class = QuestionsSerializer
    permission_classes = [permissions.IsAuthenticated]


# Thong tin cua khoa
class FalcutyViewSet(viewsets.ModelViewSet):
    queryset = Falcuty.objects.filter(status=True)
    serializer_class = FalcutySerializer

    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_falcuty(self, request, pk):
        try:
            u = Falcuty.objects.get(pk=pk)
            u.status = False
            u.save()
        except Falcuty.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=FalcutySerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# Thong tin cua lop
class MajorViewSet(viewsets.ModelViewSet):
    queryset = Major.objects.filter(status=True)
    serializer_class = MajorSerializer

    # permission_classes = [permissions.IsAuthenticated]

    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_major(self, request, pk):
        try:
            u = Major.objects.get(pk=pk)
            u.status = False
            u.save()
        except Major.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=MajorSerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)


# Thong tin cua lop
class SliderViewSet(viewsets.ModelViewSet):
    queryset = Slider.objects.filter(status=True)
    serializer_class = SliderSerializer

    # api thay doi trang thai
    @action(methods=['post'], detail=True, url_path="change-status", url_name="change-status")
    def hide_slider(self, request, pk):
        try:
            u = Slider.objects.get(pk=pk)
            u.status = False
            u.save()
        except Slider.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=SliderSerializer(u, context={'request': request}).data,
                        status=status.HTTP_200_OK)

