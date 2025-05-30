from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.contrib.messages.views import SuccessMessageMixin
from .forms import PostCreationForm, PostEditForm
from .models import Post, Tag
from django.urls import reverse_lazy
from bs4 import BeautifulSoup
import requests
import logging


def custom_404(request, exception):
    return render(request, '404.html', status=404)

class TagFilterMixin:
    def get_queryset(self):
        tag_slug = self.kwargs.get('tags')
        if tag_slug:
            return Post.objects.filter(tags__slug=tag_slug)
        return Post.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Tag.objects.all()
        context['current_tag_slug'] = self.kwargs.get('tags')
        return context
    

class HomePageView(TagFilterMixin, ListView):
    model = Post
    template_name = "home.html"
    context_object_name = "post_list"

    
    
# def home_page_view(request, tags=None):
#     if tags:
#         posts = Post.objects.filter(tags__slug=tags)
#     else:
#         posts = Post.objects.all()
    
#     return render(request, 'home.html', {'posts': posts})


logger = logging.getLogger(__name__)

class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostCreationForm
    template_name = "a_posts/post_create.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        post = form.save(commit=False)
        # post.user = self.request.user  # Set owner if applicable

        url = form.cleaned_data.get('url', '')

        # Optional: Only allow Flickr URLs
        if not url.startswith("https://www.flickr.com"):
            messages.error(self.request, "Invalid URL. Please enter a valid Flickr link.")
            return self.form_invalid(form)

        try:
            response = requests.get(url)
            sourcecode = BeautifulSoup(response.text, 'html.parser')

            # Extract image
            image_meta = sourcecode.find('meta', content=lambda c: c and "https://live.staticflickr.com/" in c)
            if image_meta:
                post.image = image_meta['content']

            # Extract title
            title_tag = sourcecode.select_one('h1.photo-title')
            if title_tag:
                post.title = title_tag.get_text(strip=True)

            # Extract artist
            artist_tag = sourcecode.select_one('a.owner-name')
            if artist_tag:
                post.artist = artist_tag.get_text(strip=True)

            # Provide fallback values (optional)
            post.title = post.title or "Untitled"
            post.artist = post.artist or "Unknown"

        except Exception as e:
            logger.error("Error scraping Flickr: %s", e)
            messages.warning(self.request, "We couldn't fetch all post details, but your post will still be saved.")

        post.save()
        form.instance = post
        form.save_m2m()
        messages.success(self.request, 'Your post has been created successfully.')
        return super().form_valid(form)


class PostUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostEditForm
    template_name = "a_posts/post_update.html"
    success_message = "Post updated successfully"

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk':self.object.pk})


class PostDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "a_posts/post_delete.html"
    success_url = reverse_lazy("home")
    success_message = "Post deleted successfully"
    

class PostDetailView(TagFilterMixin, DetailView):
    model = Post
    template_name = "a_posts/post_detail.html"

