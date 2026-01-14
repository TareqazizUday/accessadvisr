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
from locations.views import HomeView, GooglePlaceDetailView, SearchResultsView, SubmitReviewView, UpdateReviewEngagementView, SubmitReplyView, ListingsView, BrowseView
from locations.views_partner_comments import SubmitPartnerCommentView, SubmitPartnerCommentReplyView
from locations.views_blog_comments import SubmitBlogCommentView, SubmitBlogCommentReplyView
from locations.views_about_comments import SubmitAboutCommentView, SubmitAboutCommentReplyView
from locations.views_donations import SubmitDonationView
from locations.views_frontend import AccessAdvisrIndexView, AboutView, AboutPostDetailView, BlogsView, BlogDetailView, ContactView, DonateView, PackagesView, PartnersView, AllContributionsView, AccommodationView, PartnerDetailView, PartnerListView, SponsorDetailView, SponsorListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('locations.urls')),
    path('api/reviews/submit/', SubmitReviewView.as_view(), name='submit_review'),
    path('api/reviews/engagement/', UpdateReviewEngagementView.as_view(), name='update_review_engagement'),
    path('api/reviews/reply/', SubmitReplyView.as_view(), name='submit_reply'),
    path('api/partner-comments/submit/', SubmitPartnerCommentView.as_view(), name='submit_partner_comment'),
    path('api/partner-comments/reply/', SubmitPartnerCommentReplyView.as_view(), name='submit_partner_comment_reply'),
    # Keep old URLs for backward compatibility
    path('api/sponsor-comments/submit/', SubmitPartnerCommentView.as_view(), name='submit_sponsor_comment'),
    path('api/sponsor-comments/reply/', SubmitPartnerCommentReplyView.as_view(), name='submit_sponsor_comment_reply'),
    path('api/blog-comments/submit/', SubmitBlogCommentView.as_view(), name='submit_blog_comment'),
    path('api/blog-comments/reply/', SubmitBlogCommentReplyView.as_view(), name='submit_blog_comment_reply'),
    path('api/about-comments/submit/', SubmitAboutCommentView.as_view(), name='submit_about_comment'),
    path('api/about-comments/reply/', SubmitAboutCommentReplyView.as_view(), name='submit_about_comment_reply'),
    path('api/donations/submit/', SubmitDonationView.as_view(), name='submit_donation'),
    path('place/google/<str:place_id>/', GooglePlaceDetailView.as_view(), name='google_place_detail'),
    path('place/<str:place_id>/', GooglePlaceDetailView.as_view(), name='place_detail'),
    # Redirect old /search/ URL to new /listing-half-map/
    path('search/', RedirectView.as_view(url='/listing-half-map/', permanent=False, query_string=True), name='search_redirect'),
    path('listing-half-map/', SearchResultsView.as_view(), name='search_results'),
    path('listings/', ListingsView.as_view(), name='listings'),
    path('browse/', BrowseView.as_view(), name='browse'),
    
    # AccessAdvisrFrontend Pages
    path('about/', AboutView.as_view(), name='about'),
    path('about/<slug:slug>/', AboutPostDetailView.as_view(), name='about_post_detail'),
    path('blogs/', BlogsView.as_view(), name='blogs'),
    path('blog/<slug:slug>/', BlogDetailView.as_view(), name='blog_detail'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('donate/', DonateView.as_view(), name='donate'),
    path('packages/', PackagesView.as_view(), name='packages'),
    path('partners/', PartnersView.as_view(), name='partners'),
    path('partners-list/', PartnerListView.as_view(), name='partner_list'),
    path('partner/<slug:slug>/', PartnerDetailView.as_view(), name='partner_detail'),
    # Keep old URLs for backward compatibility
    path('sponsors/', SponsorListView.as_view(), name='sponsor_list'),
    path('sponsor/<slug:slug>/', SponsorDetailView.as_view(), name='sponsor_detail'),
    path('contributions/', RedirectView.as_view(url='/all-contributions/', permanent=False), name='contributions_redirect'),
    path('all-contributions/', AllContributionsView.as_view(), name='all_contributions'),
    path('accommodation/', AccommodationView.as_view(), name='accommodation'),

        # Keep the original home as default, or change to accessadvisr_index
        path('', AccessAdvisrIndexView.as_view(), name='home'),
    path('', AccessAdvisrIndexView.as_view(), name='index'),
    # Uncomment below if you want to keep original index as separate page
    # path('old-index/', HomeView.as_view(), name='old_home'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
