from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('courses', views.CourseViewSet)
router.register('lessons', views.LessonViewSet)
router.register('users', views.UserViewSet)
router.register('comment', views.CommentViewSet)
router.register('post-category', views.PostCategoryViewSet)
router.register('posts', views.PostViewSet)
router.register('comments', views.CommentsViewSet)
router.register('livestream', views.LivestreamViewSet)
router.register('questions', views.QuestionsViewSet)
router.register('falcuty', views.FalcutyViewSet)
router.register('major', views.MajorViewSet)
router.register('slider', views.SliderViewSet)
router.register('university', views.UniversityViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
