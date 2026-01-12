from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import json

from .models import Location, Category, Amenity, Review, ReviewReply
from .serializers import LocationSerializer, LocationListSerializer, CategorySerializer
from .utils import validate_coordinates, haversine_distance


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
                    timeout=5,
                )
                data = resp.json()
                if data.get('status') == 'OK':
                    place = data.get('result', {}) or {}
                    loc = (place.get('geometry') or {}).get('location') or {}
                    lat = loc.get('lat')
                    lng = loc.get('lng')
                    
                    # Try to find matching Location in our database
                    if lat and lng:
                        try:
                            location_obj = Location.objects.filter(
                                latitude__gte=float(lat) - 0.001,
                                latitude__lte=float(lat) + 0.001,
                                longitude__gte=float(lng) - 0.001,
                                longitude__lte=float(lng) + 0.001,
                                status='active'
                            ).first()
                        except (ValueError, TypeError):
                            pass
                else:
                    place = {'error': data.get('status')}
            except requests.RequestException:
                place = {'error': 'REQUEST_FAILED'}

        # Get all amenities for the template
        all_amenities = Amenity.objects.all().order_by('name')
        
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
        context['location'] = location_obj  # Our database Location if found
        context['lat'] = lat
        context['lng'] = lng
        context['GOOGLE_MAPS_API_KEY'] = api_key
        context['all_amenities'] = all_amenities
        context['reviews'] = reviews
        context['place_id'] = place_id
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
    Uses Google Places API for dynamic results when amenity is selected
    """
    template_name = 'listings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        category_value = self.request.GET.get('category', '').strip()  # Now it's a string like 'education', 'food'
        job_type = self.request.GET.get('job_type', '').strip()
        country = self.request.GET.get('country', '').strip()
        city = self.request.GET.get('city', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        price_range = self.request.GET.get('price_range', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()
        amenity_ids = self.request.GET.getlist('amenities')
        amenity_name = self.request.GET.get('amenity', '').strip()
        sort_order = self.request.GET.get('sort', '').strip()
        
        # Get all categories and amenities for filters
        categories = Category.objects.all().order_by('name')
        amenities = Amenity.objects.all().order_by('name')
        
        # Map category values to names
        category_map = {
            'education': 'Education',
            'food': 'Food & Restaurants',
            'entertainment': 'Entertainment',
            'shopping': 'Shopping',
            'sport': 'Sport',
            'travel': 'Travel & Tour'
        }
        
        # Get selected category name
        selected_category = category_map.get(category_value, '')
        
        # If amenity is selected, use Google Places API (handled by JavaScript)
        # Otherwise, use database locations
        use_google_places = bool(amenity_name)
        
        if not use_google_places:
            # Start with database locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities')
            
            # Apply filters
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) | 
                    Q(description__icontains=keywords)
                )
            
            if selected_category:
                # Filter by category name
                locations = locations.filter(category__name__iexact=selected_category)
            
            if city:
                locations = locations.filter(name__icontains=city)
            
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            if amenity_ids:
                for amenity_id in amenity_ids:
                    locations = locations.filter(amenities__id=amenity_id)
                # Get selected amenity name if filtering by single amenity
                selected_amenity = None
                if len(amenity_ids) == 1:
                    try:
                        selected_amenity = Amenity.objects.get(id=amenity_ids[0]).name
                    except Amenity.DoesNotExist:
                        pass
            else:
                selected_amenity = None
            
            # Order locations based on sort parameter
            locations = locations.distinct()
            if sort_order == 'newest':
                locations = locations.order_by('-created_at', 'name')
            elif sort_order == 'name-asc':
                locations = locations.order_by('name')
            elif sort_order == 'name-desc':
                locations = locations.order_by('-name')
            else:
                # Default order
                locations = locations.order_by('name')
            
            # Pagination information
            total_count = locations.count()
            page_size = 9  # Default showing 9 per page
            showing_to = min(page_size, total_count)
        else:
            # Use Google Places API - results will be loaded by JavaScript
            locations = []
            selected_amenity = amenity_name
            total_count = 0
            showing_to = 0
        
        context['locations'] = locations
        context['categories'] = categories
        context['amenities'] = amenities
        context['selected_amenity'] = selected_amenity
        context['selected_category'] = selected_category
        context['selected_category_value'] = category_value  # Pass the value (education, food, etc.)
        context['selected_amenity_ids'] = [int(aid) for aid in amenity_ids if aid.isdigit()]
        context['sort_order'] = sort_order
        context['use_google_places'] = use_google_places
        context['GOOGLE_MAPS_API_KEY'] = api_key
        context['total_count'] = total_count
        context['showing_from'] = 1 if total_count > 0 else 0
        context['showing_to'] = showing_to
        context['keywords'] = keywords
        context['city'] = city
        context['location_search'] = location_search
        
        return context


class BrowseView(TemplateView):
    """
    Browse page - separate from listings, shows database locations only
    """
    template_name = 'browse.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Get all categories and amenities
        categories = Category.objects.all().order_by('name')
        amenities = Amenity.objects.all().order_by('name')
        
        # Get all active locations
        locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities')
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        category_value = self.request.GET.get('category', '').strip()
        city = self.request.GET.get('city', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        sort_order = self.request.GET.get('sort', '').strip()
        user_lat = self.request.GET.get('lat', '').strip()
        user_lng = self.request.GET.get('lng', '').strip()
        radius = self.request.GET.get('radius', '25').strip()  # Default 25km radius
        
        # Apply filters
        if keywords:
            locations = locations.filter(
                Q(name__icontains=keywords) | 
                Q(description__icontains=keywords)
            )
        
        if category_value:
            category_map = {
                'education': 'Education',
                'food': 'Food & Restaurants',
                'entertainment': 'Entertainment',
                'shopping': 'Shopping',
                'sport': 'Sport',
                'travel': 'Travel & Tour'
            }
            selected_category = category_map.get(category_value, '')
            if selected_category:
                locations = locations.filter(category__name__iexact=selected_category)
        
        if city:
            locations = locations.filter(name__icontains=city)
        
        if location_search:
            locations = locations.filter(
                Q(name__icontains=location_search)
            )
        
        # Filter by distance if user location provided
        locations_list = list(locations.distinct())
        if user_lat and user_lng:
            try:
                user_lat_float = float(user_lat)
                user_lng_float = float(user_lng)
                radius_km = float(radius)
                
                # Calculate distance for each location
                locations_with_distance = []
                for location in locations_list:
                    distance = haversine_distance(
                        user_lat_float, user_lng_float,
                        float(location.latitude), float(location.longitude)
                    )
                    if distance <= radius_km:
                        location.distance = round(distance, 2)
                        locations_with_distance.append(location)
                
                # Sort by distance by default when location is provided
                if not sort_order or sort_order == 'nearest':
                    locations_with_distance.sort(key=lambda x: x.distance)
                elif sort_order == 'newest':
                    locations_with_distance.sort(key=lambda x: x.created_at, reverse=True)
                elif sort_order == 'name-asc':
                    locations_with_distance.sort(key=lambda x: x.name)
                elif sort_order == 'name-desc':
                    locations_with_distance.sort(key=lambda x: x.name, reverse=True)
                
                locations_list = locations_with_distance
            except (ValueError, TypeError):
                pass
        else:
            # Order locations normally if no location provided
            if sort_order == 'newest':
                locations_list.sort(key=lambda x: x.created_at, reverse=True)
            elif sort_order == 'name-asc':
                locations_list.sort(key=lambda x: x.name)
            elif sort_order == 'name-desc':
                locations_list.sort(key=lambda x: x.name, reverse=True)
        
        # Pagination information
        total_count = len(locations_list)
        page_size = 9  # Default showing 9 per page
        showing_to = min(page_size, total_count)
        locations_list = locations_list[:page_size]
        
        context['locations'] = locations_list
        context['categories'] = categories
        context['amenities'] = amenities
        context['GOOGLE_MAPS_API_KEY'] = api_key
        context['selected_category'] = category_value
        context['keywords'] = keywords
        context['city'] = city
        context['sort_order'] = sort_order
        context['total_count'] = total_count
        context['showing_from'] = 1 if total_count > 0 else 0
        context['showing_to'] = showing_to
        context['location_search'] = location_search
        context['user_lat'] = user_lat
        context['user_lng'] = user_lng
        context['radius'] = radius
        
        return context


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating locations.
    Provides search, filter, and detail endpoints.
    """
    queryset = Location.objects.filter(status='active')
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        # For list/search, show only active
        # For detail/update, show all
        if self.action in ['list', 'search']:
            return Location.objects.filter(status='active')
        return Location.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'search':
            return LocationListSerializer
        return LocationSerializer
    
    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search locations with filters:
        - q: keyword search (name or keywords)
        - category: filter by category ID or name
        - lat, lng: center point for radius search
        - radius: radius in kilometers (requires lat/lng)
        """
        queryset = Location.objects.filter(status='active')
        
        # Keyword search
        query = request.query_params.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(keywords__icontains=query)
            )
        
        # Category filter
        category = request.query_params.get('category', '').strip()
        if category:
            try:
                # Try as ID first
                category_id = int(category)
                queryset = queryset.filter(category_id=category_id)
            except ValueError:
                # Try as name
                queryset = queryset.filter(category__name__icontains=category)
        
        # Radius-based search
        lat = request.query_params.get('lat', '').strip()
        lng = request.query_params.get('lng', '').strip()
        radius = request.query_params.get('radius', '').strip()
        
        if lat and lng:
            is_valid, error_msg = validate_coordinates(lat, lng)
            if not is_valid:
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # If radius is provided, filter by distance
            if radius:
                try:
                    radius_km = float(radius)
                    # Calculate distance for each location and filter
                    locations_with_distance = []
                    for location in queryset:
                        distance = haversine_distance(
                            float(lat), float(lng),
                            float(location.latitude), float(location.longitude)
                        )
                        if distance <= radius_km:
                            locations_with_distance.append((location, distance))
                    
                    # Sort by distance and extract locations
                    locations_with_distance.sort(key=lambda x: x[1])
                    queryset = Location.objects.filter(
                        id__in=[loc.id for loc, _ in locations_with_distance]
                    )
                except ValueError:
                    return Response(
                        {'error': 'Invalid radius value'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Order by name
        queryset = queryset.order_by('name')
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def list(self, request):
        """List all active locations"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get categories that have active locations"""
        categories = Category.objects.filter(
            location__status='active'
        ).distinct()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class SubmitReviewView(APIView):
    """API endpoint to submit a review"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            place_id = data.get('place_id')
            author_name = data.get('author_name', '').strip()
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
                author_name=author_name,
                author_email=data.get('author_email', '').strip(),
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
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class SubmitReplyView(APIView):
    """API endpoint to submit a reply to a review"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            review_id = data.get('review_id')
            parent_reply_id = data.get('parent_reply_id')  # For nested replies
            author_name = data.get('author_name', '').strip()
            reply_text = data.get('reply_text', '').strip()
            
            if not review_id:
                return Response(
                    {'error': 'Review ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_name:
                return Response(
                    {'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not reply_text:
                return Response(
                    {'error': 'Reply text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                review = Review.objects.get(id=review_id, is_active=True)
            except Review.DoesNotExist:
                return Response(
                    {'error': 'Review not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if this is a nested reply (reply to a reply)
            parent_reply = None
            if parent_reply_id:
                try:
                    parent_reply = ReviewReply.objects.get(id=parent_reply_id, is_active=True, review=review)
                except ReviewReply.DoesNotExist:
                    return Response(
                        {'error': 'Parent reply not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Create reply
            reply = ReviewReply.objects.create(
                review=review,
                parent_reply=parent_reply,
                author_name=author_name,
                author_email=data.get('author_email', '').strip(),
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
                }
            }, status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class UpdateReviewEngagementView(APIView):
    """API endpoint to update review/reply engagement (like, dislike, heart) with toggle functionality"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
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
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
