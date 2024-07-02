from django.contrib.auth.decorators import login_required
from company.decorators import user_not_superuser_or_staff
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from company.forms import PostForm
from home.models import PostModel

@login_required
@user_not_superuser_or_staff
def all_blogs(request):
    query = request.GET.get("query", None)
    blogs = PostModel.objects.all()
    if query:
        blogs = blogs.filter(title__icontains=query)
    return render(request, 'company/blogs/all-blogs.html', {"blogs": blogs})

@login_required
@user_not_superuser_or_staff
def blog_details(request, post_slug):
    blog = get_object_or_404(PostModel.objects.select_related("category").prefetch_related("comments"), slug=post_slug)
    return render(request, 'company/blogs/blog-details.html', {"blog": blog})

@login_required
@user_not_superuser_or_staff
def create_blog(request):
    form = PostForm()
    if request.method == "POST":
        form = PostForm(data=request.POST)
        if form.is_valid() and form.is_multipart():
            post = form.save(commit=False)
            post.author = request.user
            post.description = form.cleaned_data.get("content", None)[:100]
            post_saved = post.save()
            messages.success(request, "Blog post was created successfully!")
            return redirect("home:news-details", post_saved.category.slug, post_saved.slug)

@login_required
@user_not_superuser_or_staff
def update_blog(request, post_slug):
    blog = get_object_or_404(PostModel.objects.select_related("category").prefetch_related("comments"), slug=post_slug)
    if blog.author != request.user:
        messages.error(request, "Sorry, you cannot update blog post that are not yours")
        return redirect("company:all-blogs")
    
    form = PostForm(instance=blog)
    if request.method == "POST":
        form = PostForm(instance=blog, data=request.POST)
        if form.is_valid() and form.is_multipart():
            post = form.save()
            return redirect("home:news-details", post.category.slug, post.slug)

@login_required
@user_not_superuser_or_staff
def delete_blog(request, post_slug):
    pass