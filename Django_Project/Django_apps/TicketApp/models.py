from django.db import models


# Create your models here.
class Ticket(models.Model):
    TICKET_STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    submitter = models.CharField(max_length=100)  # Changed to CharField
    assignee = models.CharField(max_length=100, blank=True, null=True)  # Changed to CharField
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    commenter = models.CharField(max_length=100)  # Changed to CharField
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commenter} on {self.ticket}"
