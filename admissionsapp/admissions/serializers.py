from .models import Category, Course, User, Lesson, Tag, Post_category, Post, Comments, Comment, University_info, \
    Slider, Major, Falcuty, Questions, Livestream_info
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField(source='image')

    def get_image(self, course):
        if course.image:
            request = self.context.get('request')
            return request.build_absolute_uri('/static/%s' % course.image.name) if request else ''


class CategorySerializer(ImageSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'subject', 'description', 'created_date', 'image', 'category_id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'subject', 'created_date', 'image']


class LessonDetailSerializer(LessonSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = LessonSerializer.Meta.model
        fields = LessonSerializer.Meta.fields + ['content', 'tags']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar']
        extra_kwargs = {
            'avatar': {'write_only': 'True'},
            'password': {'write_only': 'True'}
        }

    def get_image(self, user):
        if user.avatar:
            request = self.context.get('request')
            return request.build_absolute_uri('/static/%s' % user.avatar.name) if request else ''

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.set_password(validated_data['password'])
        u.save()
        return u


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_date', 'updated_date']


class UniversitySerializer(ModelSerializer):
    class Meta:
        model = University_info
        fields = ["id", "university_name", "logo_url", "website_url", "address", "email", "phone_number", "created_at"]


class PostCategorySerializer(ModelSerializer):
    class Meta:
        model = Post_category
        fields = ["id", "name", "created_at"]


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = ["id", "title", "content", "post_category", "status", "created_at"]


class CommentsSerializer(ModelSerializer):
    class Meta:
        model = Comments
        fields = ["id", "content", "user_id", "post_id", "parent_id", "created_at"]


class LivestreamSerializer(ModelSerializer):
    class Meta:
        model = Livestream_info
        fields = ["id", "discription", "start_time", "end_time", "start_question_time", "end_question_time", "status",
                  "created_at"]


class QuestionsSerializer(ModelSerializer):
    class Meta:
        model = Questions
        fields = ["id", "livestream_info_id", "user_id", "content", "created_at"]


class FalcutySerializer(ModelSerializer):
    class Meta:
        model = Falcuty
        fields = ["id", "falcuty_name", "falcuty_gpa", "discription", "website_url", "status", "created_at"]


class MajorSerializer(ModelSerializer):
    class Meta:
        model = Major
        fields = ["id", "major_name", "discription", "falcuty_id", "status", "created_at"]


class SliderSerializer(ModelSerializer):
    image = serializers.SerializerMethodField(source='image')

    def get_image(self, slider):
        if slider.image:
            request = self.context.get('request')
            return request.build_absolute_uri('/static/%s' % slider.image.name) if request else ''

    class Meta:
        model = Slider
        fields = ["id", "title", "image", "discription", "status", "created_at"]