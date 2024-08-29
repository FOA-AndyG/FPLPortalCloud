from django import forms
from .models import Ticket, Comment


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'submitter', 'assignee', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'submitter': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'assignee': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'commenter']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'commenter': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

