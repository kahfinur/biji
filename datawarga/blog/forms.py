from django import forms
from .models import Post, Warga

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

class WargaForm(forms.ModelForm):
    class Meta:
        model = Warga
        fields = ['nama', 'alamat', 'rt', 'rw', 'foto']
        widgets = {
            'alamat': forms.Textarea(attrs={'rows': 3}),
        }