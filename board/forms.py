from django import forms
from tinymce.widgets import TinyMCE
from .models import Post, Reply, News


class PostForm(forms.ModelForm):
    title = forms.CharField(max_length=200)
    # content = forms.Field(label='Содержимое')
    category = forms.ChoiceField(choices=Post.CATEGORIES)

    class Meta:
        model = Post
        widgets = {'content': TinyMCE(attrs={'cols': 80, 'rows': 30})}
        fields = [
            'title',
            'content',
            'category',
        ]


class ReplyForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Reply
        fields = [
            'text',
        ]


class NewsForm(forms.ModelForm):
    title = forms.CharField(max_length=255, required=True)
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = News
        fields = [
            'title',
            'text'
        ]