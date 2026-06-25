from django.conf import settings
from django.db import models


class Post(models.Model):
    class Category(models.TextChoices):
        FREE       = 'FREE',       '자유'
        DEPOSIT    = 'DEPOSIT',    '예금·적금'
        EXCHANGE   = 'EXCHANGE',   '환율·해외'
        STOCK      = 'STOCK',      '주식·ETF'
        REALESTATE = 'REALESTATE', '부동산'
        QNA        = 'QNA',        '질문'

    author   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    title    = models.CharField(max_length=200)
    content  = models.TextField()
    image    = models.ImageField(upload_to='community/', null=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.FREE)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    post    = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} - {self.post}'


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
