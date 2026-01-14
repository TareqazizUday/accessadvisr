from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Avg
from .models import Review, ReviewReply, Location, UserProfile
import json


@login_required
def profile_view(request, username=None):
    """View user profile with statistics and activity"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get user's reviews using author_email
    user_reviews = Review.objects.filter(author_email=user.email).order_by('-created_at')[:10]
    
    # Get user's review replies using author_email
    user_replies = ReviewReply.objects.filter(author_email=user.email).select_related('review').order_by('-created_at')[:10]
    
    # Calculate statistics (optimized)
    total_reviews = user_reviews.count() if len(user_reviews) < 10 else Review.objects.filter(author_email=user.email).count()
    total_replies = ReviewReply.objects.filter(author_email=user.email).count()
    
    # Calculate average rating and engagement stats from user_reviews
    if user_reviews:
        avg_rating = sum(review.get_average_rating() for review in user_reviews) / len(user_reviews)
        total_likes = sum(review.likes for review in user_reviews)
        total_dislikes = sum(review.dislikes for review in user_reviews)
        total_hearts = sum(review.hearts for review in user_reviews)
    else:
        avg_rating = 0
        total_likes = total_dislikes = total_hearts = 0
    
    # Get reviewed locations (place_id in Review -> id in Location)
    reviewed_place_ids = Review.objects.filter(author_email=user.email).values_list('place_id', flat=True).distinct()[:6]
    reviewed_locations = Location.objects.filter(id__in=reviewed_place_ids)
    
    context = {
        'profile_user': user,
        'user_reviews': user_reviews,
        'user_replies': user_replies,
        'total_reviews': total_reviews,
        'total_replies': total_replies,
        'avg_rating': round(avg_rating, 1),
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
        'total_hearts': total_hearts,
        'reviewed_locations': reviewed_locations,
        'is_own_profile': user == request.user,
    }
    
    return render(request, 'profile/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        try:
            user = request.user
            
            # Update user information
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            bio = request.POST.get('bio', '').strip()
            location = request.POST.get('location', '').strip()
            website = request.POST.get('website', '').strip()
            
            # Validation
            if not email:
                messages.error(request, 'Email is required')
                return redirect('profile_edit')
            
            # Check if email is already taken by another user
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'This email is already in use')
                return redirect('profile_edit')
            
            # Update user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()
            
            # Update profile
            profile.bio = bio
            profile.location = location
            profile.website = website
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                # Delete old profile picture if exists
                if profile.profile_picture:
                    profile.profile_picture.delete(save=False)
                profile.profile_picture = request.FILES['profile_picture']
            
            profile.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=user.username)
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('profile_edit')
    
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, 'profile/profile_edit.html', context)


@login_required
def my_reviews(request):
    """View all reviews by current user"""
    reviews = Review.objects.filter(author_email=request.user.email).order_by('-created_at')
    
    # Get statistics
    total_reviews = reviews.count()
    if reviews.exists():
        avg_rating = sum(review.get_average_rating() for review in reviews) / reviews.count()
    else:
        avg_rating = 0
    
    context = {
        'reviews': reviews,
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1),
    }
    
    return render(request, 'profile/my_reviews.html', context)


@login_required
def my_favorites(request):
    """View user's favorite locations (locations with liked/hearted reviews)"""
    # Get locations where user has given hearts or likes
    favorite_reviews = Review.objects.filter(author_email=request.user.email, hearts__gt=0)
    
    # Get unique place_ids from Review (place_id in Review -> id in Location)
    place_ids = favorite_reviews.values_list('place_id', flat=True).distinct()
    
    # Get Location objects using id field
    favorite_locations = Location.objects.filter(id__in=place_ids)
    
    context = {
        'favorite_locations': favorite_locations,
        'total_favorites': favorite_locations.count(),
    }
    
    return render(request, 'profile/my_favorites.html', context)


@login_required
def profile_settings(request):
    """User settings page"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'change_password':
            # Password change logic
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not request.user.check_password(old_password):
                messages.error(request, 'Current password is incorrect')
                return redirect('profile_settings')
            
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
                return redirect('profile_settings')
            
            if len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long')
                return redirect('profile_settings')
            
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('profile', username=request.user.username)
    
    return render(request, 'profile/settings.html', {'user': request.user})


@login_required
@require_POST
def delete_review(request, review_id):
    """Delete user's own review"""
    try:
        review = get_object_or_404(Review, id=review_id, author_email=request.user.email)
        review.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Review deleted successfully'})
        
        messages.success(request, 'Review deleted successfully')
        return redirect('my_reviews')
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': str(e)})
        
        messages.error(request, f'Error deleting review: {str(e)}')
        return redirect('my_reviews')
