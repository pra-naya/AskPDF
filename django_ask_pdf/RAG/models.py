from django.db import models
from django.contrib.auth.models import User
from RAG.scripts.file_upload import upload_location

# Create your models here.
class File(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_location)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    chroma_id = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f'{self.user.username}: {self.name}'

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, null=True, on_delete=models.CASCADE) # null=True to be deleted later
    message = models.TextField()
    response = models.TextField()
    created_at =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message}'
    