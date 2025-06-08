from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import PostCreationForm, PostEditForm, CommentCreateForm, ReplyCreateForm
from .models import *
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
import requests
import logging
import functools

def custom_404(request, exception):
    return render(request, '404.html', status=404)


logger = logging.getLogger(__name__)


class TagFilterMixin:
    def get_queryset(self):
        tag_slug = self.kwargs.get('tags')
        if tag_slug:
            return Post.objects.filter(tags__slug=tag_slug)
        return Post.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tag_slug'] = self.kwargs.get('tags')
        context["form"] = CommentCreateForm()
        context["reply_form"] = ReplyCreateForm()
        
        return context
    

class HomePageView(TagFilterMixin, ListView):
    model = Post
    template_name = "home.html"
    context_object_name = "post_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            for post in queryset:
                post.user_liked = post.likes.filter(id=user_id).exists()
        return queryset
    
# def home_page_view(request, tags=None):
#     if tags:
#         posts = Post.objects.filter(tags__slug=tags)
#     else:
#         posts = Post.objects.all()
    
#     return render(request, 'home.html', {'posts': posts})


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PostCreationForm
    template_name = "a_posts/post_create.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        post = form.save(commit=False)

        url = form.cleaned_data.get('url', '')

        if not url.startswith("https://www.flickr.com"):
            messages.error(self.request, "Invalid URL. Please enter a valid Flickr link.")
            return self.form_invalid(form)

        try:
            response = requests.get(url)
            sourcecode = BeautifulSoup(response.text, 'html.parser')

            image_meta = sourcecode.find('meta', content=lambda c: c and "https://live.staticflickr.com/" in c)
            if image_meta:
                post.image = image_meta['content']

            title_tag = sourcecode.select_one('h1.photo-title')
            if title_tag:
                post.title = title_tag.get_text(strip=True)

            artist_tag = sourcecode.select_one('a.owner-name')
            if artist_tag:
                post.artist = artist_tag.get_text(strip=True)

            post.title = post.title or "Untitled"
            post.artist = post.artist or "Unknown"

        except Exception as e:
            logger.error("Error scraping Flickr: %s", e)
            messages.warning(self.request, "We couldn't fetch all post details, but your post will still be saved.")

        post.author = self.request.user
        post.save()
        form.instance = post
        form.save_m2m()

        messages.success(self.request, 'Your post has been created successfully.')
        return redirect(self.success_url)



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
    

class PostDetailView(TagFilterMixin, FormMixin, DetailView):
    model = Post
    form_class = CommentCreateForm
    template_name = "a_posts/post_detail.html"
    
    def get_success_url(self):
        return self.request.path
    
    def get_reply_form(self):
        return ReplyCreateForm(self.request.POST or None)
    
    def get_object(self, queryset=None):
        """Override to ensure proper object retrieval with UUID"""
        try:
            return super().get_object(queryset)
        except Exception as e:
            logger.error(f"Error retrieving post object: {e}")
            logger.error(f"URL kwargs: {self.kwargs}")
            raise

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        # Get the object first
        try:
            self.object = self.get_object()
            print(f"[DEBUG] Resolved Post: {self.object}, ID: {self.object.pk}")
        except Exception as e:
            logger.error(f"Failed to get post object: {e}")
            if request.headers.get('HX-Request'):
                return HttpResponse(f"Error: Post not found", status=404)
            return redirect('home')  # or wherever you want to redirect
        
        form = self.get_form()
        reply_form = self.get_reply_form()
        form_type = request.POST.get("form_type")
        
        # Check if this is an HTMX request
        is_htmx = request.headers.get('HX-Request', False)
        
        logger.debug(f"Processing {form_type} form for post {self.object.pk}")
        logger.debug(f"HTMX request: {is_htmx}")
        
        if form_type == "comment":
            if form.is_valid():
                try:
                    comment = form.save(commit=False)
                    comment.author = request.user
                    comment.parent_post = self.object
                    comment.save()
                    
                    logger.debug(f"Comment created successfully: {comment.pk}")
                    
                    # If HTMX request, return partial template
                    if is_htmx:
                        html = render_to_string(
                            'snippets/add_comment.html',
                            {
                                'comment': comment, 
                                'post': self.object,
                                'user': request.user
                            },
                            request=request
                        )
                        return HttpResponse(html)
                    
                    if is_htmx:
                        comments = self.object.comments.all()
                        return render(self.request, "snippets/loop_postdetail_comments.html", {"comments": comments})
                    
                    # Regular form submission
                    return redirect(self.get_success_url())
                    
                except Exception as e:
                    logger.error(f"Error saving comment: {e}")
                    if is_htmx:
                        return HttpResponse(f"Error saving comment: {str(e)}", status=400)
                    
            else:
                logger.debug(f"Comment form validation failed: {form.errors}")
                # Handle form errors for HTMX
                if is_htmx:
                    html = render_to_string(
                        'a_posts/partials/comment_form_errors.html',
                        {'form': form},
                        request=request
                    )
                    return HttpResponse(html, status=400)
                    
        elif form_type == "reply":
            parent_comment_id = request.POST.get("parent_comment_id")
            logger.debug(f"Processing reply to comment: {parent_comment_id}")
            
            if reply_form.is_valid():
                try:
                    if not parent_comment_id:
                        raise ValueError("Parent comment ID is required for reply")
                    
                    # Get parent comment with proper error handling
                    try:
                        parent_comment = Comment.objects.get(pk=parent_comment_id)
                    except Comment.DoesNotExist:
                        logger.error(f"Parent comment {parent_comment_id} not found")
                        raise ValueError(f"Parent comment not found")
                    except Exception as e:
                        logger.error(f"Error retrieving parent comment {parent_comment_id}: {e}")
                        raise ValueError(f"Invalid parent comment ID")
                    
                    reply = reply_form.save(commit=False)
                    reply.author = request.user
                    reply.parent_comment = parent_comment
                    reply.save()
                    
                    logger.debug(f"Reply created successfully: {reply.pk}")
                    
                    # If HTMX request, return partial template and updated counts
                    if is_htmx:
                        # Refresh the post object to get updated counts
                        self.object.refresh_from_db()
                        parent_comment.refresh_from_db()  # Refresh parent comment too
                        
                        # Return the reply HTML
                        reply_html = render_to_string(
                            'snippets/add_reply.html',
                            {
                                'reply': reply, 
                                'post': self.object,
                                'comment': parent_comment,
                                'user': request.user
                            },
                            request=request
                        )
                        
                        # Return the updated replies toggle
                        toggle_html = render_to_string(
                            'snippets/replies_toggle.html',
                            {
                                'comment': parent_comment,
                                'post': self.object
                            },
                            request=request
                        )
                        
                        # Combine both Html responses
                        combined_html = reply_html + toggle_html
                        return HttpResponse(combined_html)
                    
                    # Regular form submission
                    return redirect(self.get_success_url())
                    
                except Exception as e:
                    logger.error(f"Error saving reply: {e}")
                    if is_htmx:
                        return HttpResponse(f"Error saving reply: {str(e)}", status=400)
                    
            else:
                logger.debug(f"Reply form validation failed: {reply_form.errors}")
                # Handle form errors for HTMX
                if is_htmx:
                    html = render_to_string(
                        'a_posts/partials/reply_form_errors.html',
                        {'reply_form': reply_form},
                        request=request
                    )
                    return HttpResponse(html, status=400)
        
        # If we get here, something went wrong
        logger.warning("Reached fallback in post method")
        if is_htmx:
            return HttpResponse("An error occurred processing your request", status=400)
        
        # Fallback for non-HTMX requests
        return self.form_invalid(form if form_type == "comment" else reply_form)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        context["reply_form"] = self.get_reply_form()
        context["post"] = self.object

        # Check if sorting by top comments is requested
        if self.request.GET.get("top") == "1":
            comments = Comment.top_comments_for_post(self.object)
        else:
            comments = self.object.comments.order_by("-created")
        
        context["comments"] = comments
        
        if self.request.user.is_authenticated:
            context["user_liked"] = self.object.likes.filter(id=self.request.user.id).exists()
        
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()

        if request.headers.get('HX-Request'):
            return render(request, "snippets/loop_postdetail_comments.html", context)

        return self.render_to_response(context)
    

class CommentDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = "a_posts/comment_delete.html"
    success_message = "Comment deleted successfully"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.object  # for backwards compatibility in templates
        context["post"] = self.object.parent_post
        return context


    def get_success_url(self):
        if self.object and getattr(self.object, "parent_post", None):
            return reverse_lazy("post_detail", kwargs={"pk": self.object.parent_post.pk})
        messages.warning(self.request, "Comment had no parent post. Redirecting to home.")
        return reverse_lazy("home")


class ReplyDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = "a_posts/reply_delete.html"
    success_message = "Reply deleted successfully"

    def get_success_url(self):
        return reverse_lazy("post_detail", kwargs={'pk': self.object.parent_comment.parent_post.pk})
    

def like_toggle(model, pk_field='pk'):
    def inner_func(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            obj_id = kwargs.get(pk_field)
            obj = get_object_or_404(model, id=obj_id)

            # Only allow users to like/unlike posts that aren't their own
            if obj.author != request.user:
                if obj.likes.filter(id=request.user.id).exists():
                    obj.likes.remove(request.user)
                else:
                    obj.likes.add(request.user)

            # Pass the object to the wrapped function
            return func(request, obj, *args, **kwargs)
        return wrapper
    return inner_func

# Usage examples:
@login_required 
@like_toggle(Post)
def like_post(request, post, *args, **kwargs):
    return render(request, 'snippets/like_post.html', {"post": post})

@login_required 
@like_toggle(Comment)
def like_comment(request, post, *args, **kwargs):
    return render(request, 'snippets/like_comment.html', {"comment": post})

@login_required 
@like_toggle(Reply)
def like_reply(request, post, *args, **kwargs):
    return render(request, 'snippets/like_reply.html', {"reply": post})


# # Redirect logic
# next_url = request.GET.get("next")
# if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
#     next_url = "home"
# return HttpResponse(post.likes.count())