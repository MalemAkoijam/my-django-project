from django import forms

class URLForm(forms.Form):
    youtube_url = forms.URLField(label="YouTube URL", widget=forms.URLInput(attrs={'class': 'form-control'}))
