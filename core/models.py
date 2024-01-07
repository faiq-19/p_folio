from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model() # currently logged in user

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    field = models.CharField(max_length=100, blank=True)
    position = models.IntegerField(choices=((0, 'Unemployed'), (1, 'Intern'), (2, 'Employed')), default=0)
    current_workplace = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Experience(models.Model):
    profile = models.ForeignKey(Profile, related_name='experiences', on_delete=models.CASCADE)
    job_title = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)

    def __str__(self):
        return self.job_title

class Skill(models.Model):
    profile = models.ForeignKey(Profile, related_name='skills', on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=100)

class Project(models.Model):
    profile = models.ForeignKey(Profile, related_name='projects', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=100)

class Education(models.Model):
    profile = models.ForeignKey(Profile, related_name='educations', on_delete=models.CASCADE)
    university_name = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)

    def __str__(self):
        return self.university_name

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='posted_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user