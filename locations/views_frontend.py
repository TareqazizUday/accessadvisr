from django.views.generic import TemplateView, DetailView, ListView
from django.views import View
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from locations.models import Review, Partner, Blog, AboutPost, AboutComment, AboutCommentReply, DonationCampaign, Category
import json
import requests


class SubmitListingView(LoginRequiredMixin, View):
    """View for submitting a new listing"""
    template_name = 'submit_listing.html'
    login_url = '/api/auth/login/'
    
    def get(self, request):
        context = {
            'categories': Category.objects.all().order_by('name'),
            'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Handle listing submission - creates a review for the place"""
        try:
            # Get form data
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            country = request.POST.get('country', '').strip()
            other_country = request.POST.get('other_country', '').strip()
            city = request.POST.get('city', '').strip()
            region = request.POST.get('region', '').strip()
            category_name = request.POST.get('category', '').strip()
            friendly_location = request.POST.get('friendly_location', '').strip()
            latitude = request.POST.get('latitude', '').strip()
            longitude = request.POST.get('longitude', '').strip()
            staff_rating = request.POST.get('staff_rating', '0')
            access_rating = request.POST.get('access_rating', '0')
            features = request.POST.getlist('features')
            
            # Validate required fields
            if not title or not description or not category_name:
                return JsonResponse({
                    'success': False,
                    'error': 'Title, description, and category are required.'
                }, status=400)
            
            if not latitude or not longitude:
                return JsonResponse({
                    'success': False,
                    'error': 'Please select a location on the map.'
                }, status=400)
            
            # Use other_country if country is "OTHER"
            final_country = other_country if country == 'OTHER' else country
            
            # Calculate ratings (convert 1-5 scale for staff/access to review ratings)
            try:
                staff_rating_val = int(staff_rating) if staff_rating else 3
                access_rating_val = int(access_rating) if access_rating else 3
                
                # Ensure ratings are between 1-5
                staff_rating_val = max(1, min(5, staff_rating_val))
                access_rating_val = max(1, min(5, access_rating_val))
            except (ValueError, TypeError):
                staff_rating_val = 3
                access_rating_val = 3
            
            # Build address and place name
            address_parts = [friendly_location, city, final_country]
            full_address = ', '.join([part for part in address_parts if part])
            place_name = f"{title} - {full_address}"
            
            # Try to find existing place via Google Places API
            api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
            place_id = None
            
            if api_key:
                try:
                    # Search for place using name and location
                    search_params = {
                        'input': title,
                        'inputtype': 'textquery',
                        'fields': 'place_id,name,geometry',
                        'locationbias': f'circle:500@{latitude},{longitude}',
                        'key': api_key,
                    }
                    search_resp = requests.get(
                        'https://maps.googleapis.com/maps/api/place/findplacefromtext/json',
                        params=search_params,
                        timeout=5,
                    )
                    search_data = search_resp.json()
                    
                    if search_data.get('status') == 'OK' and search_data.get('candidates'):
                        place_id = search_data['candidates'][0].get('place_id')
                except:
                    pass
            
            # If no Google place_id found, create a custom one based on coordinates
            if not place_id:
                # Create unique place_id from coordinates
                lat_str = str(latitude).replace('.', '').replace('-', 'n')[:8]
                lng_str = str(longitude).replace('.', '').replace('-', 'n')[:8]
                place_id = f"custom_{lat_str}_{lng_str}"
            
            # Build review text with location details
            review_text_parts = [description]
            if features:
                feature_names = {
                    'accessible_parking': 'Accessible parking available',
                    'accessible_toilets': 'Accessible toilets available',
                    'personal_assistance': 'Personal assistance available',
                    'step_free_access': 'Step free access',
                    'help_points': 'Help points available',
                    'lifts': 'Lifts available',
                    'changing_places': 'Changing Places available',
                }
                feature_list = [feature_names.get(f, f.replace('_', ' ').title()) for f in features]
                review_text_parts.append("\n\nAccessible Features:\n" + "\n".join([f"✓ {f}" for f in feature_list]))
            
            review_text = "\n".join(review_text_parts)
            
            # Create review
            review = Review.objects.create(
                place_id=place_id,
                place_name=place_name,
                user=request.user,
                author_name=request.user.get_full_name() or request.user.username,
                author_email=request.user.email,
                quality_rating=staff_rating_val,
                location_rating=access_rating_val,
                service_rating=staff_rating_val,
                price_rating=3,  # Default neutral rating
                review_text=review_text,
                is_active=True,
                save_info=False
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Your review has been submitted successfully! Thank you for contributing.',
                'review_id': review.id,
                'place_id': place_id
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid data format: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred while submitting your listing: {str(e)}'
            }, status=500)


class AccessAdvisrIndexView(TemplateView):
    template_name = 'accessadvisr_index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Fetch 6 most recent active reviews
        context['recent_contributions'] = Review.objects.filter(
            is_active=True
        ).order_by('-created_at')[:6]
        
        return context


class AboutView(ListView):
    """List view for all about posts"""
    model = AboutPost
    template_name = 'about.html'
    context_object_name = 'about_posts'
    paginate_by = 9
    
    def get_queryset(self):
        """Only show published about posts"""
        return AboutPost.objects.filter(status='published').order_by('order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all published posts for the cards section
        context['all_about_posts'] = AboutPost.objects.filter(status='published').order_by('order', '-created_at')
        return context


class AboutPostDetailView(DetailView):
    """Detail view for an about post"""
    model = AboutPost
    template_name = 'about_post_detail.html'
    context_object_name = 'about_post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Only show published about posts"""
        return AboutPost.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent about posts (excluding current one) for sidebar
        context['recent_about_posts'] = AboutPost.objects.filter(
            status='published'
        ).exclude(id=self.object.id).order_by('order', '-created_at')[:4]
        
        # Get all approved comments with nested replies
        from django.db.models import Prefetch
        
        replies_prefetch = Prefetch(
            'replies',
            queryset=AboutCommentReply.objects.filter(
                is_active=True,
                is_approved=True,
                parent_reply__isnull=True
            ).prefetch_related(
                Prefetch(
                    'child_replies',
                    queryset=AboutCommentReply.objects.filter(
                        is_active=True,
                        is_approved=True
                    ).order_by('created_at')
                )
            ).order_by('created_at')
        )
        
        context['comments'] = AboutComment.objects.filter(
            about_post=self.object,
            is_active=True,
            is_approved=True
        ).select_related('about_post').prefetch_related(replies_prefetch).order_by('-created_at')
        
        # Count all approved comments
        context['total_comments_count'] = AboutComment.objects.filter(
            about_post=self.object,
            is_active=True,
            is_approved=True
        ).count()
        
        return context


class BlogsView(TemplateView):
    template_name = 'blogs.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all published blogs, ordered by most recent first
        all_blogs = Blog.objects.filter(status='published').order_by('-created_at')
        
        # Pagination - show 9 blogs initially
        page_size = 9
        context['blogs'] = all_blogs[:page_size]
        context['remaining_blogs'] = all_blogs[page_size:]
        context['total_blogs'] = all_blogs.count()
        context['showing_count'] = min(page_size, context['total_blogs'])
        context['has_more'] = context['total_blogs'] > page_size
        
        return context


class BlogDetailView(DetailView):
    """Detail view for a blog post"""
    model = Blog
    template_name = 'blog_detail.html'
    context_object_name = 'blog'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Only show published blogs"""
        return Blog.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent blogs (excluding current one) for sidebar
        context['recent_blogs'] = Blog.objects.filter(
            status='published'
        ).exclude(id=self.object.id).order_by('-created_at')[:4]
        
        # Get popular blogs (excluding current one, ordered by most recent)
        context['popular_blogs'] = Blog.objects.filter(
            status='published'
        ).exclude(id=self.object.id).order_by('-created_at')[:2]
        
        # Get all approved comments with nested replies
        from locations.models import BlogComment, BlogCommentReply
        from django.db.models import Prefetch
        
        # Prefetch replies with nested replies properly
        replies_prefetch = Prefetch(
            'replies',
            queryset=BlogCommentReply.objects.filter(
                is_active=True,
                is_approved=True,
                parent_reply__isnull=True  # Only top-level replies
            ).prefetch_related(
                Prefetch(
                    'child_replies',
                    queryset=BlogCommentReply.objects.filter(
                        is_active=True,
                        is_approved=True
                    ).order_by('created_at')
                )
            ).order_by('created_at')
        )
        
        context['comments'] = BlogComment.objects.filter(
            blog=self.object,
            is_active=True,
            is_approved=True
        ).select_related('blog').prefetch_related(replies_prefetch).order_by('-created_at')
        
        # Count all approved comments
        context['total_comments_count'] = BlogComment.objects.filter(
            blog=self.object,
            is_active=True,
            is_approved=True
        ).count()
        
        return context


class ContactView(View):
    template_name = 'contact.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        from .models import ContactMessage
        
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Basic validation
        if not name or not email or not message:
            return JsonResponse({
                'success': False,
                'error': 'All fields are required.'
            }, status=400)
        
        # Email validation
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return JsonResponse({
                'success': False,
                'error': 'Please provide a valid email address.'
            }, status=400)
        
        try:
            # Save contact message
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                message=message,
                status='new'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for contacting us! We will get back to you soon.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)


class DonateView(TemplateView):
    template_name = 'donate.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all active donation campaigns
        context['donation_campaigns'] = DonationCampaign.objects.filter(is_active=True).order_by('order', '-created_at')
        return context


class PackagesView(TemplateView):
    template_name = 'packages.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all active partners
        all_partners = Partner.objects.filter(status__in=['active', 'published']).order_by('order', 'title')
        # Get first 3 active partners
        context['partners'] = all_partners[:3]
        # Get remaining partners
        context['remaining_partners'] = all_partners[3:]
        context['total_partners'] = all_partners.count()
        return context


class PartnersView(TemplateView):
    template_name = 'partners.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all active partners
        all_partners = Partner.objects.filter(status__in=['active', 'published']).order_by('order', 'title')
        
        # First section: Show only first 3 partners
        context['partners'] = all_partners[:3]
        # Keep old variable name for backward compatibility
        context['sponsors'] = context['partners']
        
        # Second section: Remaining partners (skip first 3)
        remaining_partners = list(all_partners[3:])
        context['remaining_partners'] = remaining_partners[:6]  # Show 6 initially
        context['remaining_partners_all'] = remaining_partners  # All remaining for load more
        context['remaining_partners_count'] = len(remaining_partners)
        context['remaining_partners_showing'] = len(context['remaining_partners'])
        # Keep old variable names for backward compatibility
        context['remaining_sponsors'] = context['remaining_partners']
        context['remaining_sponsors_all'] = context['remaining_partners_all']
        context['remaining_sponsors_count'] = context['remaining_partners_count']
        context['remaining_sponsors_showing'] = context['remaining_partners_showing']
        
        return context


class AllContributionsView(TemplateView):
    template_name = 'all_contributions.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Fetch all active reviews, ordered by most recent first
        context['all_contributions'] = Review.objects.filter(
            is_active=True
        ).order_by('-created_at')
        
        return context


class EntertainmentView(TemplateView):
    template_name = 'entertainment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class FoodDrinkView(TemplateView):
    template_name = 'food_drink.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class ShoppingView(TemplateView):
    template_name = 'shopping.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class SportsRecreationalView(TemplateView):
    template_name = 'sports_recreational.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class TransportView(TemplateView):
    template_name = 'transport.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class FlightTravelView(TemplateView):
    template_name = 'flight_travel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class EducationView(TemplateView):
    template_name = 'education.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class AccommodationView(TemplateView):
    template_name = 'accommodation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context


class PartnerDetailView(DetailView):
    """Detail view for a partner"""
    model = Partner
    template_name = 'partner_detail.html'
    context_object_name = 'partner'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Only show active/published partners"""
        return Partner.objects.filter(status__in=['active', 'published'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get other active partners for sidebar (excluding current one)
        context['recent_partners'] = Partner.objects.filter(
            status__in=['active', 'published']
        ).exclude(id=self.object.id).order_by('-created_at')[:4]
        # Get all active comments (approved and unapproved - so users can see their own pending comments)
        from locations.models import PartnerComment, PartnerCommentReply
        from django.db.models import Prefetch
        
        # Prefetch replies with nested replies properly
        replies_prefetch = Prefetch(
            'replies',
            queryset=PartnerCommentReply.objects.filter(
                is_active=True,
                parent_reply__isnull=True  # Only top-level replies
            ).prefetch_related(
                Prefetch(
                    'child_replies',
                    queryset=PartnerCommentReply.objects.filter(is_active=True).order_by('created_at')
                )
            ).order_by('created_at')
        )
        
        context['comments'] = PartnerComment.objects.filter(
            partner=self.object,
            is_active=True
        ).select_related('partner').prefetch_related(replies_prefetch).order_by('-created_at')
        # Count all comments (both approved and unapproved) for display
        context['total_comments_count'] = PartnerComment.objects.filter(
            partner=self.object,
            is_active=True
        ).count()
        return context


class PartnerListView(ListView):
    """List view for all partners"""
    model = Partner
    template_name = 'partners_list.html'
    context_object_name = 'partners'
    paginate_by = 12
    
    def get_queryset(self):
        """Only show active/published partners"""
        return Partner.objects.filter(status__in=['active', 'published']).order_by('order', 'title')


# Keep old class names for backward compatibility
SponsorDetailView = PartnerDetailView
SponsorListView = PartnerListView
