from rest_framework import serializers
from .models import *


class UserSerializer ( serializers.ModelSerializer ) :
    class Meta :
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
                  'is_active', 'is_staff', 'is_admin', 'is_manager']
        read_only_fields = ['id']


class UserCreateSerializer ( serializers.ModelSerializer ) :
    password = serializers.CharField ( write_only=True, required=True, style={'input_type' : 'password'} )
    password_confirm = serializers.CharField ( write_only=True, required=True, style={'input_type' : 'password'} )

    class Meta :
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number',
                  'password', 'password_confirm']

    def validate_email(self, value) :
        if not value :
            raise serializers.ValidationError ( "Email is required" )
        if User.objects.filter ( email=value ).exists () :
            raise serializers.ValidationError ( "Email already exists" )
        return value

    def validate_username(self, value) :
        if User.objects.filter ( username=value ).exists () :
            raise serializers.ValidationError ( "Username already exists" )
        return value

    def validate(self, data) :
        if data['password'] != data['password_confirm'] :
            raise serializers.ValidationError ( {"password" : "Passwords do not match"} )
        return data

    def create(self, validated_data) :
        validated_data.pop ( 'password_confirm' )
        password = validated_data.pop ( 'password' )
        user = User.objects.create_user ( password=password, **validated_data )
        return user


class LoginSerializer ( serializers.Serializer ) :
    username = serializers.CharField ()
    password = serializers.CharField ( write_only=True, style={'input_type' : 'password'} )

    def validate(self, data) :
        username = data.get ( 'username' )
        password = data.get ( 'password' )

        if username and password :
            try :
                user = User.objects.get ( username=username )
            except User.DoesNotExist :
                raise serializers.ValidationError ( 'Username or password is invalid' )

            if not user.check_password ( password ) :
                raise serializers.ValidationError ( 'Username or password is invalid' )

            if not user.is_active :
                raise serializers.ValidationError (
                    'Your account is not active. Please contact administrator.'
                )

            data['user'] = user
            return data
        else :
            raise serializers.ValidationError ( 'Must include "username" and "password"' )


class CategorySerializer ( serializers.Serializer ) :
    id = serializers.IntegerField ( read_only=True )
    name = serializers.CharField ( max_length=100 )
    slug = serializers.SlugField ( read_only=True )
    created_at = serializers.DateTimeField ( read_only=True )
    updated_at = serializers.DateTimeField ( read_only=True )

    def create(self, validated_data) :
        return Category.objects.create ( **validated_data )

    def update(self, instance, validated_data) :
        instance.name = validated_data.get ( 'name', instance.name )
        instance.slug = validated_data.get ( 'slug', instance.slug )
        instance.save ()
        return instance


class NewsSerializer ( serializers.Serializer ) :
    id = serializers.IntegerField ( read_only=True )
    title = serializers.CharField ( max_length=200 )
    content = serializers.CharField ()
    category = serializers.PrimaryKeyRelatedField ( queryset=Category.objects.all () )
    author = serializers.PrimaryKeyRelatedField ( read_only=True )
    created_at = serializers.DateTimeField ( read_only=True )
    updated_at = serializers.DateTimeField ( read_only=True )

    def create(self, validated_data) :
        validated_data['author'] = self.context['request'].user
        return News.objects.create ( **validated_data )

    def update(self, instance, validated_data) :
        instance.title = validated_data.get ( 'title', instance.title )
        instance.content = validated_data.get ( 'content', instance.content )
        instance.category = validated_data.get ( 'category', instance.category )
        instance.save ()
        return instance


class CommentSerializer ( serializers.Serializer ) :
    id = serializers.IntegerField ( read_only=True )
    content = serializers.CharField ()
    news = serializers.PrimaryKeyRelatedField ( queryset=News.objects.all () )
    user = serializers.PrimaryKeyRelatedField ( read_only=True )
    created_at = serializers.DateTimeField ( read_only=True )
    updated_at = serializers.DateTimeField ( read_only=True )

    def create(self, validated_data) :
        validated_data['user'] = self.context['request'].user
        return Comment.objects.create ( **validated_data )

    def update(self, instance, validated_data) :
        instance.content = validated_data.get ( 'content', instance.content )
        instance.news = validated_data.get ( 'news', instance.news )
        instance.save ()
        return instance