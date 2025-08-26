from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Poll(models.Model):
    question = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.question
    
    def total_votes(self):
        return Vote.objects.filter(poll=self).count()
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    def is_available_for_voting(self):
        return self.is_active and not self.is_expired()
    
    def time_remaining(self):
        if self.expires_at:
            remaining = self.expires_at - timezone.now()
            if remaining.total_seconds() > 0:
                days = remaining.days
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                return {'days': days, 'hours': hours, 'minutes': minutes}
        return None

class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    
    def __str__(self):
        return self.text
    
    def vote_count(self):
        return self.votes.count()
    
    def vote_percentage(self):
        total = self.poll.total_votes()
        if total == 0:
            return 0
        return (self.vote_count() / total) * 100

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, related_name='votes', on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'poll')
    
    def __str__(self):
        return f"{self.user.username} voted for {self.option.text}"
