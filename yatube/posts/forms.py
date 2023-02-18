from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    """Форма для создания/редактирования поста."""
    class Meta:
        model = Post
        fields = ("text", "group")
