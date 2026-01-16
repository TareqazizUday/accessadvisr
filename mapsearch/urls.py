"""
URL configuration for mapsearch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from locations.sitemaps import StaticViewSitemap, BlogSitemap, PartnerSitemap, AboutPostSitemap, LocationSitemap
from locations.views import HomeView, GooglePlaceDetailView, SearchResultsView, SubmitReviewView, UpdateReviewEngagementView, SubmitReplyView, UpdateReviewView, ListingsView, BrowseView
from locations.views_partner_comments import SubmitPartnerCommentView, SubmitPartnerCommentReplyView
from locations.views_blog_comments import SubmitBlogCommentView, SubmitBlogCommentReplyView
from locations.views_about_comments import SubmitAboutCommentView, SubmitAboutCommentReplyView
from locations.views_donations import SubmitDonationView
from locations.views_frontend import AccessAdvisrIndexView, AboutView, AboutPostDetailView, BlogsView, BlogDetailView, ContactView, DonateView, PackagesView, PartnersView, AllContributionsView, AccommodationView, EntertainmentView, FoodDrinkView, ShoppingView, SportsRecreationalView, TransportView, FlightTravelView, EducationView, PartnerDetailView, PartnerListView, SponsorDetailView, SponsorListView, SubmitListingView
from locations.views_auth import RegisterView, LoginView, LogoutView
from locations.views_profile import profile_view, profile_edit, my_reviews, my_favorites, profile_settings, delete_review
from locations.views_seo import RobotsView

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'blogs': BlogSitemap,
    'partners': PartnerSitemap,
    'about': AboutPostSitemap,
    'locations': LocationSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('locations.urls')),
    
    # Submit Listing - SEO optimized
    path('submit-listing/', SubmitListingView.as_view(), name='submit-listing'),
    
    # Authentication URLs - SEO optimized
    path('api/auth/register/', RegisterView.as_view(), name='auth-register'),
    path('api/auth/login/', LoginView.as_view(), name='auth-login'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth-logout'),
    
    # Profile URLs - Specific paths MUST come before generic <username> pattern - SEO optimized
    path('profile/edit/', profile_edit, name='profile-edit'),
    path('profile/reviews/', my_reviews, name='my-reviews'),
    path('profile/favorites/', my_favorites, name='my-favorites'),
    path('profile/settings/', profile_settings, name='profile-settings'),
    path('api/profile/review/<int:review_id>/delete/', delete_review, name='delete-review'),
    path('profile/', profile_view, name='my-profile'),
    path('profile/<str:username>/', profile_view, name='profile'),
    
    # Review and Comment URLs - SEO optimized with hyphens
    path('api/reviews/submit/', SubmitReviewView.as_view(), name='submit-review'),
    path('api/reviews/update/', UpdateReviewView.as_view(), name='update-review'),
    path('api/reviews/engagement/', UpdateReviewEngagementView.as_view(), name='update-review-engagement'),
    path('api/reviews/reply/', SubmitReplyView.as_view(), name='submit-reply'),
    path('api/partner-comments/submit/', SubmitPartnerCommentView.as_view(), name='submit-partner-comment'),
    path('api/partner-comments/reply/', SubmitPartnerCommentReplyView.as_view(), name='submit-partner-comment-reply'),
    # Keep old URLs for backward compatibility
    path('api/sponsor-comments/submit/', SubmitPartnerCommentView.as_view(), name='submit-sponsor-comment'),
    path('api/sponsor-comments/reply/', SubmitPartnerCommentReplyView.as_view(), name='submit-sponsor-comment-reply'),
    path('api/blog-comments/submit/', SubmitBlogCommentView.as_view(), name='submit-blog-comment'),
    path('api/blog-comments/reply/', SubmitBlogCommentReplyView.as_view(), name='submit-blog-comment-reply'),
    path('api/about-comments/submit/', SubmitAboutCommentView.as_view(), name='submit-about-comment'),
    path('api/about-comments/reply/', SubmitAboutCommentReplyView.as_view(), name='submit-about-comment-reply'),
    path('api/donations/submit/', SubmitDonationView.as_view(), name='submit-donation'),
    path('place/google/<str:place_id>/', GooglePlaceDetailView.as_view(), name='google-place-detail'),
    path('place/<str:place_id>/', GooglePlaceDetailView.as_view(), name='place-detail'),
    # Redirect old /search/ URL to new /listing-half-map/
    path('search/', RedirectView.as_view(url='/listing-half-map/', permanent=False, query_string=True), name='search-redirect'),
    path('listing-half-map/', SearchResultsView.as_view(), name='search-results'),
    path('listings/', ListingsView.as_view(), name='listings'),
    path('browse/', BrowseView.as_view(), name='browse'),
    
    # AccessAdvisrFrontend Pages - SEO optimized
    path('about/', AboutView.as_view(), name='about'),
    path('about/<slug:slug>/', AboutPostDetailView.as_view(), name='about-post-detail'),
    path('blogs/', BlogsView.as_view(), name='blogs'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog-detail'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('donate/', DonateView.as_view(), name='donate'),
    path('packages/', PackagesView.as_view(), name='packages'),
    path('partners/', PartnersView.as_view(), name='partners'),
    path('partners-list/', PartnerListView.as_view(), name='partners-list'),
    path('partner/<slug:slug>/', PartnerDetailView.as_view(), name='partner-detail'),
    # Keep old URLs for backward compatibility
    path('sponsors/', SponsorListView.as_view(), name='sponsors-list'),
    path('sponsor/<slug:slug>/', SponsorDetailView.as_view(), name='sponsor-detail'),
    path('contributions/', RedirectView.as_view(url='/all-contributions/', permanent=False), name='contributions-redirect'),
    path('all-contributions/', AllContributionsView.as_view(), name='all-contributions'),
    path('accommodation/', AccommodationView.as_view(), name='accommodation'),
    path('entertainment/', EntertainmentView.as_view(), name='entertainment'),
    path('food-drink/', FoodDrinkView.as_view(), name='food-drink'),
    path('shopping/', ShoppingView.as_view(), name='shopping'),
    path('sports-recreational/', SportsRecreationalView.as_view(), name='sports-recreational'),
    path('transport/', TransportView.as_view(), name='transport'),
    path('flight-travel/', FlightTravelView.as_view(), name='flight-travel'),
    path('education/', EducationView.as_view(), name='education'),

    # Sitemap URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # SEO URLs
    path('robots.txt', RobotsView.as_view(), name='robots_txt'),

        # Keep the original home as default, or change to accessadvisr_index
        path('', AccessAdvisrIndexView.as_view(), name='home'),
    path('', AccessAdvisrIndexView.as_view(), name='index'),
    # Uncomment below if you want to keep original index as separate page
    # path('old-index/', HomeView.as_view(), name='old_home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
