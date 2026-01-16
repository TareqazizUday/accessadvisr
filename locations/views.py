from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import json

from .models import Review, ReviewReply, Category
from .serializers import CategorySerializer


class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context


class GooglePlaceDetailView(TemplateView):
    """
    Full details page for a Google Place (hotel, restaurant, education, etc.)
    """
    template_name = 'place_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        place_id = kwargs.get('place_id')
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')

        place = {}
        lat = lng = None
        location_obj = None
        error_message = None
        
        if api_key and place_id:
            params = {
                'place_id': place_id,
                'key': api_key,
                'fields': (
                    'name,formatted_address,geometry,types,rating,user_ratings_total,'
                    'photos,website,international_phone_number,formatted_phone_number,'
                    'opening_hours,price_level,reviews,url,vicinity,editorial_summary,'
                    'business_status,current_opening_hours,plus_code'
                ),
            }
            try:
                resp = requests.get(
                    'https://maps.googleapis.com/maps/api/place/details/json',
                    params=params,
                    timeout=10,
                )
                data = resp.json()
                if data.get('status') == 'OK':
                    place = data.get('result', {}) or {}
                    loc = (place.get('geometry') or {}).get('location') or {}
                    lat = loc.get('lat')
                    lng = loc.get('lng')
                    
                    # Ensure photos is a list
                    if 'photos' not in place or not place['photos']:
                        place['photos'] = []
                else:
                    error_message = data.get('status')
                    place = {'error': error_message, 'name': 'Place Not Found'}
            except requests.RequestException as e:
                error_message = f'REQUEST_FAILED: {str(e)}'
                place = {'error': error_message, 'name': 'Error Loading Place'}
        else:
            if not api_key:
                error_message = 'GOOGLE_MAPS_API_KEY not configured'
            elif not place_id:
                error_message = 'INVALID_PLACE_ID'
            place = {'error': error_message, 'name': 'Configuration Error'}

        # Get reviews for this place from database with replies and nested replies
        reviews = []
        if place_id:
            from django.db.models import Prefetch
            reviews = Review.objects.filter(
                place_id=place_id, 
                is_active=True
            ).prefetch_related(
                Prefetch(
                    'replies', 
                    queryset=ReviewReply.objects.filter(
                        is_active=True, 
                        parent_reply__isnull=True
                    ).prefetch_related(
                        Prefetch(
                            'child_replies',
                            queryset=ReviewReply.objects.filter(is_active=True).order_by('created_at')
                        )
                    ).order_by('created_at')
                )
            ).order_by('-created_at')

        context['place'] = place
        context['lat'] = lat if lat else 0
        context['lng'] = lng if lng else 0
        context['GOOGLE_MAPS_API_KEY'] = api_key
        context['reviews'] = reviews
        context['place_id'] = place_id
        
        # Debug info
        if place.get('photos'):
            print(f"Place has {len(place['photos'])} photos")
            if place['photos']:
                print(f"First photo ref: {place['photos'][0].get('photo_reference', 'NO REF')}")
        
        return context


class SearchResultsView(TemplateView):
    """
    Search results page showing locations based on search criteria
    """
    template_name = 'listing_half_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Get search parameters
        location_name = self.request.GET.get('location', '').strip()
        category_name = self.request.GET.get('category', '').strip()
        keywords = self.request.GET.get('keywords', '').strip()
        amenity = self.request.GET.get('amenity', '').strip()
        
        # Get all categories from database
        categories = Category.objects.all().order_by('name')
        
        context['location_name'] = location_name
        context['category_name'] = category_name
        context['keywords'] = keywords
        context['amenity'] = amenity
        context['categories'] = categories
        context['GOOGLE_MAPS_API_KEY'] = api_key
        context['results'] = []  # Will be populated by JavaScript
        
        return context


class ListingsView(TemplateView):
    """
    Listings page with filter options and location cards
    Uses only Google Places API for dynamic results
    """
    template_name = 'listings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        category_value = self.request.GET.get('category', '').strip()
        city = self.request.GET.get('city', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        amenity_name = self.request.GET.get('amenity', '').strip()
        sort_order = self.request.GET.get('sort', '').strip()
        selected_features = self.request.GET.getlist('feature')
        
        # Get all categories for filters
        categories = Category.objects.all().order_by('name')
        
        # Map category values to names
        category_map = {
            'accommodation': 'Accommodation',
            'entertainment': 'Entertainment',
            'food': 'Food & Drink',
            'shopping': 'Shopping',
            'sport': 'Sports & Recreational',
            'transport': 'Transport',
            'travel': 'Flight & Travel',
            'education': 'Education'
        }
        
        selected_category = category_map.get(category_value, '')
        
        # All results from Google Places API - loaded by JavaScript
        context['locations'] = []
        context['categories'] = categories
        context['selected_amenity'] = amenity_name if amenity_name else None
        context['selected_category'] = selected_category
        context['selected_category_value'] = category_value
        context['selected_features'] = selected_features
        context['sort_order'] = sort_order
        context['use_google_places'] = True  # Always use Google Places
        context['GOOGLE_MAPS_API_KEY'] = api_key
        context['keywords'] = keywords
        context['city'] = city
        context['location_search'] = location_search
        
        return context


class BrowseView(TemplateView):
    """
    Browse page - uses Google Places API for results
    """
    template_name = 'browse.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Get all categories for filters
        categories = Category.objects.all().order_by('name')
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        category_value = self.request.GET.get('category', '').strip()
        city = self.request.GET.get('city', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        selected_features = self.request.GET.getlist('feature')
        sort_order = self.request.GET.get('sort', '').strip()
        user_lat = self.request.GET.get('lat', '').strip()
        user_lng = self.request.GET.get('lng', '').strip()
        radius = self.request.GET.get('radius', '25').strip()
        
        # All results from Google Places API
        context['locations'] = []
        context['categories'] = categories
        context['GOOGLE_MAPS_API_KEY'] = api_key
        context['selected_category'] = category_value
        context['selected_features'] = selected_features
        context['keywords'] = keywords
        context['city'] = city
        context['sort_order'] = sort_order
        context['location_search'] = location_search
        context['user_lat'] = user_lat
        context['user_lng'] = user_lng
        context['radius'] = radius
        
        return context


@method_decorator(csrf_exempt, name='dispatch')
class SubmitReviewView(APIView):
    """API endpoint to submit a review"""
    
    def post(self, request):
        try:
            # Use request.data instead of json.loads(request.body) to avoid "cannot access body" error
            data = request.data
            
            # Validate required fields
            place_id = data.get('place_id')
            
            # If user is logged in, use their information automatically
            if request.user.is_authenticated:
                author_name = request.user.username
                author_email = request.user.email
            else:
                # For anonymous users, require name and email
                author_name = data.get('author_name', '').strip()
                author_email = data.get('author_email', '').strip()
            
            review_text = data.get('review_text', '').strip()
            
            if not place_id:
                return Response(
                    {'error': 'Place ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_name:
                return Response(
                    {'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_email and not request.user.is_authenticated:
                return Response(
                    {'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not review_text:
                return Response(
                    {'error': 'Review text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get ratings (default to 5 if not provided)
            quality_rating = int(data.get('quality_rating', 5))
            location_rating = int(data.get('location_rating', 5))
            service_rating = int(data.get('service_rating', 5))
            price_rating = int(data.get('price_rating', 5))
            
            # Validate ratings are between 1-5
            for rating in [quality_rating, location_rating, service_rating, price_rating]:
                if rating < 1 or rating > 5:
                    return Response(
                        {'error': 'Ratings must be between 1 and 5'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get place name from Google Places API if available
            place_name = data.get('place_name', '')
            if not place_name and place_id:
                api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
                if api_key:
                    try:
                        params = {
                            'place_id': place_id,
                            'key': api_key,
                            'fields': 'name',
                        }
                        resp = requests.get(
                            'https://maps.googleapis.com/maps/api/place/details/json',
                            params=params,
                            timeout=5,
                        )
                        data_resp = resp.json()
                        if data_resp.get('status') == 'OK':
                            place_name = data_resp.get('result', {}).get('name', '')
                    except:
                        pass
            
            # Create review
            review = Review.objects.create(
                place_id=place_id,
                place_name=place_name,
                user=request.user if request.user.is_authenticated else None,
                author_name=author_name,
                author_email=author_email,
                quality_rating=quality_rating,
                location_rating=location_rating,
                service_rating=service_rating,
                price_rating=price_rating,
                review_text=review_text,
                save_info=data.get('save_info', False),
            )
            
            return Response({
                'success': True,
                'message': 'Review submitted successfully',
                'review_id': review.id,
                'review': {
                    'id': review.id,
                    'author_name': review.author_name,
                    'review_text': review.review_text,
                    'quality_rating': review.quality_rating,
                    'location_rating': review.location_rating,
                    'service_rating': review.service_rating,
                    'price_rating': review.price_rating,
                    'average_rating': review.get_average_rating(),
                    'created_at': review.created_at.isoformat(),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print('Error in SubmitReviewView:', str(e))
            print(traceback.format_exc())
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class SubmitReplyView(APIView):
    """API endpoint to submit a reply to a review"""
    
    def post(self, request):
        try:
            # Use request.data instead of json.loads(request.body)
            data = request.data
            
            review_id = data.get('review_id')
            parent_reply_id = data.get('parent_reply_id')  # For nested replies
            
            # If user is logged in, use their information automatically
            if request.user.is_authenticated:
                author_name = request.user.username
                author_email = request.user.email
            else:
                # For anonymous users, require name and email
                author_name = data.get('author_name', '').strip()
                author_email = data.get('author_email', '').strip()
            
            reply_text = data.get('reply_text', '').strip()
            
            if not review_id:
                return Response(
                    {'success': False, 'error': 'Review ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_name:
                return Response(
                    {'success': False, 'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_email and not request.user.is_authenticated:
                return Response(
                    {'success': False, 'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not reply_text:
                return Response(
                    {'success': False, 'error': 'Reply text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                review = Review.objects.get(id=review_id, is_active=True)
            except Review.DoesNotExist:
                return Response(
                    {'success': False, 'error': 'Review not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if this is a nested reply (reply to a reply)
            parent_reply = None
            if parent_reply_id:
                try:
                    parent_reply = ReviewReply.objects.get(id=parent_reply_id, is_active=True, review=review)
                except ReviewReply.DoesNotExist:
                    return Response(
                        {'success': False, 'error': 'Parent reply not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Create reply
            reply = ReviewReply.objects.create(
                review=review,
                parent_reply=parent_reply,
                author_name=author_name,
                author_email=author_email,
                reply_text=reply_text,
            )
            
            return Response({
                'success': True,
                'message': 'Reply submitted successfully',
                'reply': {
                    'id': reply.id,
                    'author_name': reply.author_name,
                    'reply_text': reply.reply_text,
                    'created_at': reply.created_at.isoformat(),
                    'likes': reply.likes,
                    'dislikes': reply.dislikes,
                    'hearts': reply.hearts,
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            import traceback
            print('Error in SubmitReplyView:', str(e))
            print(traceback.format_exc())
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class UpdateReviewEngagementView(APIView):
    """API endpoint to update review/reply engagement (like, dislike, heart) with toggle functionality"""
    
    def post(self, request):
        try:
            # Use request.data instead of json.loads(request.body)
            data = request.data
            
            review_id = data.get('review_id')
            reply_id = data.get('reply_id')
            action_type = data.get('action')  # 'like', 'dislike', 'heart'
            is_toggle = data.get('toggle', True)  # Whether to toggle (like/unlike) or just increment
            
            if not review_id and not reply_id:
                return Response(
                    {'error': 'Review ID or Reply ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action_type not in ['like', 'dislike', 'heart']:
                return Response(
                    {'error': 'Invalid action type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Handle reply engagement
            if reply_id:
                try:
                    reply = ReviewReply.objects.get(id=reply_id, is_active=True)
                except ReviewReply.DoesNotExist:
                    return Response(
                        {'error': 'Reply not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                if action_type == 'like':
                    if is_toggle:
                        reply.likes = max(0, reply.likes - 1)
                        is_active = False
                    else:
                        reply.likes += 1
                        is_active = True
                elif action_type == 'dislike':
                    if is_toggle:
                        reply.dislikes = max(0, reply.dislikes - 1)
                        is_active = False
                    else:
                        reply.dislikes += 1
                        is_active = True
                elif action_type == 'heart':
                    if is_toggle:
                        reply.hearts = max(0, reply.hearts - 1)
                        is_active = False
                    else:
                        reply.hearts += 1
                        is_active = True
                
                reply.save()
                
                return Response({
                    'success': True,
                    'likes': reply.likes,
                    'dislikes': reply.dislikes,
                    'hearts': reply.hearts,
                    'is_active': is_active,
                }, status=status.HTTP_200_OK)
            
            # Handle review engagement
            try:
                review = Review.objects.get(id=review_id, is_active=True)
            except Review.DoesNotExist:
                return Response(
                    {'error': 'Review not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Toggle functionality: frontend tracks user state, backend just increments/decrements
            # Frontend sends 'is_toggle' = true if user wants to unlike (decrement)
            # Frontend sends 'is_toggle' = false if user wants to like (increment)
            
            if action_type == 'like':
                if is_toggle:
                    # User wants to unlike (decrement)
                    review.likes = max(0, review.likes - 1)
                    is_active = False
                else:
                    # User wants to like (increment)
                    review.likes += 1
                    is_active = True
            elif action_type == 'dislike':
                if is_toggle:
                    # User wants to undislike (decrement)
                    review.dislikes = max(0, review.dislikes - 1)
                    is_active = False
                else:
                    # User wants to dislike (increment)
                    review.dislikes += 1
                    is_active = True
            elif action_type == 'heart':
                if is_toggle:
                    # User wants to unheart (decrement)
                    review.hearts = max(0, review.hearts - 1)
                    is_active = False
                else:
                    # User wants to heart (increment)
                    review.hearts += 1
                    is_active = True
            
            review.save()
            
            return Response({
                'success': True,
                'likes': review.likes,
                'dislikes': review.dislikes,
                'hearts': review.hearts,
                'is_active': is_active,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print('Error in UpdateReviewEngagementView:', str(e))
            print(traceback.format_exc())
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class UpdateReviewView(APIView):
    """API endpoint to update/edit a review or reply"""
    
    def post(self, request):
        try:
            data = request.data
            
            review_id = data.get('review_id')
            reply_id = data.get('reply_id')
            new_text = data.get('text', '').strip()
            
            if not new_text:
                return Response(
                    {'success': False, 'error': 'Text cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update reply
            if reply_id:
                try:
                    reply = ReviewReply.objects.get(id=reply_id, is_active=True)
                    reply.reply_text = new_text
                    reply.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Reply updated successfully',
                        'reply': {
                            'id': reply.id,
                            'text': reply.reply_text,
                            'updated_at': reply.created_at.isoformat(),
                        }
                    }, status=status.HTTP_200_OK)
                except ReviewReply.DoesNotExist:
                    return Response(
                        {'success': False, 'error': 'Reply not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Update review
            elif review_id:
                try:
                    review = Review.objects.get(id=review_id, is_active=True)
                    review.review_text = new_text
                    review.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Review updated successfully',
                        'review': {
                            'id': review.id,
                            'text': review.review_text,
                            'updated_at': review.created_at.isoformat(),
                        }
                    }, status=status.HTTP_200_OK)
                except Review.DoesNotExist:
                    return Response(
                        {'success': False, 'error': 'Review not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {'success': False, 'error': 'Review ID or Reply ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            import traceback
            print('Error in UpdateReviewView:', str(e))
            print(traceback.format_exc())
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
