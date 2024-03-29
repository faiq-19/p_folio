from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount, Education, Project, Skill, Experience
from itertools import chain
import random

# Create your views here.
@login_required(login_url='signin') # make sure you don't go to the news feed without logging in
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # User Suggestion

    all_users = User.objects.exclude(username__in=user_following_list).exclude(username=request.user.username)
    final_suggestions_list = random.sample(list(all_users), min(4, len(all_users)))

    # Fetch profiles for the suggestions
    suggestions_username_profile_lists = Profile.objects.filter(user__in=final_suggestions_list)

    posts = Post.objects.all()

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_lists': suggestions_username_profile_lists[:4]})


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def search(request):

    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    else:
        return redirect('/')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('image') is None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            field = request.POST['field']
            position = request.POST['position']
            current_workplace = request.POST['current_workplace']
            city = request.POST['city']
            language = request.POST['language']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.field = field
            user_profile.position = position
            user_profile.current_workplace = current_workplace
            user_profile.city = city
            user_profile.language = language
            user_profile.save()

        if request.FILES.get('image') is not None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            field = request.POST['field']
            position = request.POST['position']
            current_workplace = request.POST['current_workplace']
            city = request.POST['city']
            language = request.POST['language']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.field = field
            user_profile.position = position
            user_profile.current_workplace = current_workplace
            user_profile.city = city
            user_profile.language = language
            user_profile.save()

        skills = request.POST.getlist('skills[]')
        user_profile.skills.all().delete()  # Remove existing skills before saving new ones
        for skill in skills:
            Skill.objects.create(profile=user_profile, skill_name=skill)

        # Save projects information to the Project model
        projects = request.POST.getlist('projects[]')
        user_profile.projects.all().delete()  # Remove existing projects before saving new ones
        for project in projects:
            Project.objects.create(profile=user_profile, project_name=project)

        university_name = request.POST.getlist('university_name[]')
        degree = request.POST.getlist('degree[]')

        # Save education information to the Profile model
        user_profile.educations.all().delete()
        for university, degree in zip(university_name, degree):
            Education.objects.create(profile=user_profile, university_name=university, degree=degree)

        # Experiences

        job_titles = request.POST.getlist('job_titles[]')
        durations = request.POST.getlist('durations[]')

        user_profile.experiences.all().delete()  # Remove existing experiences before saving new ones
        for job_title, duration in zip(job_titles, durations):
            Experience.objects.create(profile=user_profile, job_title=job_title, duration=duration)

        return redirect('/')

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # creating profile model for user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')

        else:
            messages.info(request, 'Password Don\'t Match')
            return redirect('signup.html')

    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:    # if it is present in the databse
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid Username or Password')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')
