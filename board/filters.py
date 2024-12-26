from django.contrib.auth.models import User
from django.forms import DateInput
from django_filters import FilterSet, ModelChoiceFilter, DateFilter, OrderingFilter
from .models import Post, Reply


class ReplyFilter(FilterSet):
    post = ModelChoiceFilter(
        field_name='post__title',
        label='Пост',
        empty_label='Все',
        queryset=Post.objects.all()
    )

    o = OrderingFilter(
        fields=(
            ('author', 'author'),
            ('created', 'date')
        ),
        field_labels={
            'author': 'Автор',
            'created': 'Дата'
        },
        label='Порядок',
    )

    class Meta:
        model = Reply
        fields = {}