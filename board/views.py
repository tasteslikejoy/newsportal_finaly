from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Post, Reply, News
from .forms import PostForm, ReplyForm, NewsForm
from .filters import ReplyFilter
from .tasks import send_reply_accept_notification, send_mass_notification


class PostList(ListView):
    model = Post
    ordering = 'created'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    queryset = Post.objects.all()


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_edit.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)


class PostEdit(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj.author != self.request.user:
            raise PermissionDenied()
        return obj


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = 'post_list'
    template_name = 'post_delete'

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj.author != self.request.user:
            raise PermissionDenied()
        return obj


class CategoryList(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        queryset = Post.objects.filter(category=self.kwargs['category']).order_by('-created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = dict(Post.CATEGORIES)

        if self.kwargs['category'] in category.keys():
            context['category'] = category[self.kwargs['category']]
        return context


class ReplyCreate(LoginRequiredMixin, CreateView):
    model = Reply
    template_name = 'reply_edit.html'
    form_class = ReplyForm

    def form_valid(self, form):
        reply = form.save(commit=False)
        reply.author = self.request.user
        post_ = Post.objects.get(pk=self.kwargs['pk'])
        reply.post = post_
        reply.save()
        post_.replies.add(reply)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs['pk']).author
        if request.user == author:
            return HttpResponseRedirect(reverse('post_details', args=[self.kwargs['pk']]))
        return super().dispatch(request, *args, **kwargs)


class ReplyDelete(DeleteView):
    model = Reply
    template_name = 'reply_delete.html'

    def get_success_url(self):
        user = self.object.post.author
        return reverse_lazy('board', kwargs={'username': user.username})


class BoardPostsList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-created'
    template_name = 'board_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.method == "GET":
            return queryset.filter(author=self.request.user)
        return Post.objects.none()

    def dispatch(self, request, *args, **kwargs):

        if request.user.username != self.kwargs['username']:
            return HttpResponseRedirect(reverse_lazy('board', args=[request.user.username]))

        return super().dispatch(request, *args, **kwargs)


class BoardPostReplies(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'board_post_replies.html'
    context_object_name = 'replies'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(BoardPostReplies, self).get_context_data(**kwargs)
        post = Post.objects.get(pk=self.kwargs['pk'])
        context['title'] = post.title
        context['category'] = post.get_category_display
        context['created'] = post.created
        print('===============')
        print(context)
        print('===============')
        return context

    def get_queryset(self):
        post_ = get_object_or_404(Post, id=self.kwargs['pk'])
        queryset = post_.replies.all().order_by('-created')
        return queryset


class BoardReplyList(ListView):
    model = Reply
    template_name = 'board.html'
    context_object_name = 'replies'
    ordering = '-created'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().exclude(author=self.request.user)
        self.filterset = ReplyFilter(self.request.GET, queryset)
        if self.request.GET:
            return self.filterset.qs
        return Reply.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


@login_required()
def reply_accept(request, reply_id):
    reply = Reply.objects.get(pk=reply_id)
    reply.accept = True
    reply.save()
    user = request.user.username
    send_reply_accept_notification.delay(reply_id=reply.pk)
    return redirect(f'/board/{user}'+'?post=&o=')


class NewsNotification(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'board.news.add_post'
    model = News
    template_name = 'create_news.html'
    form_class = NewsForm
    success_url = reverse_lazy('success')

    def form_valid(self, form):
        news = form.save()
        send_mass_notification.delay(title=news.title, text=news.text)
        return super().form_valid(form)


def news_success(request):
    return render(request, 'msg_success.html')