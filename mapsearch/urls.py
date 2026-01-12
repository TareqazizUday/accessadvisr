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
from locations.views import HomeView, GooglePlaceDetailView, SearchResultsView, SubmitReviewView, UpdateReviewEngagementView, SubmitReplyView, ListingsView, BrowseView
from locations.views_frontend import AccessAdvisrIndexView, AboutView, BlogsView, ContactView, DonateView, PackagesView, PartnersView, AllContributionsView, AccommodationView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('locations.urls')),
    path('api/reviews/submit/', SubmitReviewView.as_view(), name='submit_review'),
    path('api/reviews/engagement/', UpdateReviewEngagementView.as_view(), name='update_review_engagement'),
    path('api/reviews/reply/', SubmitReplyView.as_view(), name='submit_reply'),
    path('place/google/<str:place_id>/', GooglePlaceDetailView.as_view(), name='google_place_detail'),
    path('place/<str:place_id>/', GooglePlaceDetailView.as_view(), name='place_detail'),
    # Redirect old /search/ URL to new /listing-half-map/
    path('search/', RedirectView.as_view(url='/listing-half-map/', permanent=False, query_string=True), name='search_redirect'),
    path('listing-half-map/', SearchResultsView.as_view(), name='search_results'),
    path('listings/', ListingsView.as_view(), name='listings'),
    path('browse/', BrowseView.as_view(), name='browse'),
    
    # AccessAdvisrFrontend Pages
    path('about/', AboutView.as_view(), name='about'),
    path('blogs/', BlogsView.as_view(), name='blogs'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('donate/', DonateView.as_view(), name='donate'),
    path('packages/', PackagesView.as_view(), name='packages'),
    path('partners/', PartnersView.as_view(), name='partners'),
    path('contributions/', RedirectView.as_view(url='/all-contributions/', permanent=False), name='contributions_redirect'),
    path('all-contributions/', AllContributionsView.as_view(), name='all_contributions'),
    path('accommodation/', AccommodationView.as_view(), name='accommodation'),

        # Keep the original home as default, or change to accessadvisr_index
        path('', AccessAdvisrIndexView.as_view(), name='home'),
    path('', AccessAdvisrIndexView.as_view(), name='index'),
    # Uncomment below if you want to keep original index as separate page
    # path('old-index/', HomeView.as_view(), name='old_home'),
]
