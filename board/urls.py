from django.contrib import admin
from django.urls import path
from .views import PostList, PostDetail, PostCreate, CategoryList, ReplyCreate

# posts/
urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('<int:pk>/', PostDetail.as_view(), name='post_details'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/delete', PostCreate.as_view(), name='post_delete'),
    path('categories/<str:category>', CategoryList.as_view(), name='category_list'),
    path('<int:pk>/reply', ReplyCreate.as_view(), name='reply'),
]