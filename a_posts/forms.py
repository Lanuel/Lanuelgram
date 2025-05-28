from .models import Post
from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field


class PostCreationForm(ModelForm):
    class Meta:
        model = Post
        fields = ["url", "body", "tags",]
        labels = {
            "body": "Caption",
            "url": "Flickr Image URL",
            'tags': "Category"
        }
        widgets = {
            "body" : forms.Textarea(attrs={'rows':3, 'placeholder':'Add a caption...', 'class':'font1 text-4xl'}),
            "url" : forms.TextInput(attrs={'placeholder':'Add url...',}),
            "tags" : forms.CheckboxSelectMultiple(),
        }


class PostEditForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "tags",]
        labels = {
            "body": "Caption",
            'tags': "Category"
        }
        widgets = {
            "body" : forms.Textarea(attrs={'rows':3, 'placeholder':'Add a caption...', 'class':'font1 text-4xl'}),
            "tags" : forms.CheckboxSelectMultiple(),
        }

