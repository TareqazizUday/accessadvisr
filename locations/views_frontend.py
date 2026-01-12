from django.views.generic import TemplateView
from django.conf import settings
from locations.models import Review


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


class AboutView(TemplateView):
    template_name = 'about.html'


class BlogsView(TemplateView):
    template_name = 'blogs.html'


class ContactView(TemplateView):
    template_name = 'contact.html'


class DonateView(TemplateView):
    template_name = 'donate.html'


class PackagesView(TemplateView):
    template_name = 'packages.html'


class PartnersView(TemplateView):
    template_name = 'partners.html'


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
            
            locations = locations.order_by('name')
        else:
            # If no specific accommodation category, show all active locations
            locations = Location.objects.filter(status='active').select_related('category').prefetch_related('amenities')
        
        context['locations'] = locations
        context['category_name'] = 'Accommodation'
        
        return context
