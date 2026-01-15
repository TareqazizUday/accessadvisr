from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.conf import settings
from locations.models import Review, Partner, Blog, AboutPost, AboutComment, AboutCommentReply, DonationCampaign


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
        blogs = Blog.objects.filter(status='published').order_by('-created_at')
        
        # Pagination - show 9 blogs initially
        page_size = 9
        context['blogs'] = blogs[:page_size]
        context['total_blogs'] = blogs.count()
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


class ContactView(TemplateView):
    template_name = 'contact.html'


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
        context['sponsors'] = Partner.objects.filter(status__in=['active', 'published']).order_by('order', 'title')
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
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find entertainment category
        entertainment_categories = Category.objects.filter(
            Q(name__icontains='entertainment') |
            Q(name__icontains='cinema') |
            Q(name__icontains='theater') |
            Q(name__icontains='movie') |
            Q(name__icontains='concert')
        )
        
        # Get locations in entertainment categories
        if entertainment_categories.exists():
            locations = Location.objects.filter(
                category__in=entertainment_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific entertainment category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        return context


class FoodDrinkView(TemplateView):
    template_name = 'food_drink.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find food & drink category
        food_drink_categories = Category.objects.filter(
            Q(name__icontains='food') |
            Q(name__icontains='drink') |
            Q(name__icontains='restaurant') |
            Q(name__icontains='cafe') |
            Q(name__icontains='bar')
        )
        
        # Get locations in food & drink categories
        if food_drink_categories.exists():
            locations = Location.objects.filter(
                category__in=food_drink_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific food & drink category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        
        return context


class ShoppingView(TemplateView):
    template_name = 'shopping.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find shopping category
        shopping_categories = Category.objects.filter(
            Q(name__icontains='shopping') |
            Q(name__icontains='shop') |
            Q(name__icontains='store') |
            Q(name__icontains='mall') |
            Q(name__icontains='market')
        )
        
        # Get locations in shopping categories
        if shopping_categories.exists():
            locations = Location.objects.filter(
                category__in=shopping_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific shopping category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        
        return context


class SportsRecreationalView(TemplateView):
    template_name = 'sports_recreational.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find sports & recreational category
        sports_categories = Category.objects.filter(
            Q(name__icontains='sport') |
            Q(name__icontains='recreational') |
            Q(name__icontains='gym') |
            Q(name__icontains='fitness') |
            Q(name__icontains='park')
        )
        
        # Get locations in sports & recreational categories
        if sports_categories.exists():
            locations = Location.objects.filter(
                category__in=sports_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific sports category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        
        return context


class TransportView(TemplateView):
    template_name = 'transport.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find transport category
        transport_categories = Category.objects.filter(
            Q(name__icontains='transport') |
            Q(name__icontains='station') |
            Q(name__icontains='terminal') |
            Q(name__icontains='airport') |
            Q(name__icontains='taxi')
        )
        
        # Get locations in transport categories
        if transport_categories.exists():
            locations = Location.objects.filter(
                category__in=transport_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific transport category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        
        return context


class FlightTravelView(TemplateView):
    template_name = 'flight_travel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find flight & travel category
        flight_travel_categories = Category.objects.filter(
            Q(name__icontains='flight') |
            Q(name__icontains='travel') |
            Q(name__icontains='airport') |
            Q(name__icontains='airline') |
            Q(name__icontains='tourism')
        )
        
        # Get locations in flight & travel categories
        if flight_travel_categories.exists():
            locations = Location.objects.filter(
                category__in=flight_travel_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific flight & travel category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        
        return context


class EducationView(TemplateView):
    template_name = 'education.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find education category
        education_categories = Category.objects.filter(
            Q(name__icontains='education') |
            Q(name__icontains='school') |
            Q(name__icontains='university') |
            Q(name__icontains='college') |
            Q(name__icontains='library')
        )
        
        # Get locations in education categories
        if education_categories.exists():
            locations = Location.objects.filter(
                category__in=education_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific education category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        
        return context


class AccommodationView(TemplateView):
    template_name = 'accommodation.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        
        # Import Location and Category models
        from locations.models import Location, Category
        from django.db.models import Q
        
        # Get filter parameters
        keywords = self.request.GET.get('keywords', '').strip()
        location_search = self.request.GET.get('location', '').strip()
        
        # Try to find accommodation category
        # Check for various possible names
        accommodation_categories = Category.objects.filter(
            Q(name__icontains='accommodation') |
            Q(name__icontains='hotel') |
            Q(name__icontains='lodging') |
            Q(name__icontains='travel') |
            Q(name__icontains='tour')
        )
        
        # Get locations in accommodation categories
        if accommodation_categories.exists():
            locations = Location.objects.filter(
                category__in=accommodation_categories,
                status='active'
            ).select_related('category').prefetch_related('amenities')
            
            # Apply keyword filter
            if keywords:
                locations = locations.filter(
                    Q(name__icontains=keywords) |
                    Q(description__icontains=keywords) |
                    Q(keywords__icontains=keywords)
                )
            
            # Apply location filter
            if location_search:
                locations = locations.filter(
                    Q(name__icontains=location_search)
                )
            
            # Order by rating (highest first), then by name
            locations = locations.order_by('-rating', 'name')
        else:
            # If no specific accommodation category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities').order_by('-rating', 'name')
        
        context['locations'] = locations
        context['category_name'] = 'Accommodation'
        
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
