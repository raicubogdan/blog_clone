from django.shortcuts import render
from blog.models import Post, Comment
from blog.forms import PostForm , CommentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (TemplateView, ListView,
                                DetailView, CreateView,
                                UpdateView, DeleteView)

class AboutView(TemplateView):
    
    # Links to "about.html"
    template_name = "about.html"

class PostListView(ListView):
    model = Post # Requires "post_list.html"

    def get_queryset(self):
        # Orders all the Post objects by 'published_date' (posts must pe published)
        # Links to "post_list.html"
        return Post.objects.filter(published_date__lte=timezone.now()).order_by("-published_date")

class PostDetailView(DetailView): # Links to "post_detail.html"
    model = Post # Requires "post_detail.html"

class CreatePostView(LoginRequiredMixin, CreateView):
    # When a person is not logged it, they will be prompted to "login_url"
    login_url = "/login"

    # After a succesful post, the user will be redirected to "redirect_field_name"
    redirect_field_name = "blog/post_detail.html"

    # Links to "post_form.html"
    form_class = PostForm

    model = Post

class UpdatePostView(LoginRequiredMixin, UpdateView):
    # When a person is not logged it, they will be prompted to "login_url"
    login_url = "/login"

    # After a succesful post, the user will be redirected to "redirect_field_name"
    redirect_field_name = "blog/post_detail.html"

    # Links to "post_form.html"
    form_class = PostForm

    model = Post

class DeletePostView(LoginRequiredMixin, DeleteView):
    model = Post 

    # If deletion is succesful, the user is taken to "succes_url"
    success_url = reverse_lazy("post_list") # 

class DraftListView(LoginRequiredMixin, ListView):
    # When a person is not logged it, they will be prompted to "login_url"
    login_url = "/login/" 

    # Redirects user to "redirect_field_name"
    redirect_field_name = "blog/post_list.html"
    model = Post

    # Selects posts that haven't been published yet (Post.published_date = False)
    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by("created_date")

#######################################
## Functions that require a pk match ##
#######################################

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # models.Post.publish() - Post class method from models (Post.published_date = True)
    post.publish()

    # Redirects to "post_detail" view of respective post
    return redirect('post_detail', pk=pk)

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()

            # Redirects to "post_detail" view of respective post
            return redirect('post_detail', pk=post.pk)
    else:

        # Links to "comment_form.html" (template name not required by default, can be changed)
        form = CommentForm() 

    return render(request, 'blog/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # models.Comment.approve() - Comment class method (approved_comment = True)
    comment.approve() 

    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk

    # models.Comment.delete()
    comment.delete()

    return redirect('post_draft_list', pk=post_pk)
