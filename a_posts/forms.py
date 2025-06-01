from django import forms
from django.forms import ModelForm
from .models import Post, Comment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field


class PostCreationForm(ModelForm):
    class Meta:
        model = Post
        fields = ["url", "body", "tags"]
        labels = {
            "url": "Flickr Image URL",
            "body": "Caption",
            "tags": "Category",
        }
        widgets = {
            "url": forms.TextInput(attrs={"placeholder": "Add URL...", "class": "w-full"}),
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a caption...", "class": "w-full font1 text-lg"}),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("url", css_class="border rounded p-2"),
            Field("body", css_class="border rounded p-2"),
        )


class PostEditForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "tags"]
        labels = {
            "title": "Title",
            "body": "Caption",
            "tags": "Category",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Add title...", "class": "w-full"}),
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a caption...", "class": "w-full font1 text-lg"}),
            "tags": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("title", css_class="border rounded p-2"),
            Field("body", css_class="border rounded p-2"),
        )


class CommentCreateForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        labels = {
            "body": ""
        }
        