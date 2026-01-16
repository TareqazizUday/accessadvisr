from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

def partner_image_upload_path(instance, filename):
    """Generate upload path for partner images - uses slug to prevent duplicates"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Use partner slug as filename to prevent duplicates
    # If slug exists, use it; otherwise Django will handle it after save
    if instance.slug:
        filename = f"{instance.slug}.{ext}"
    elif instance.pk:
        # If we have a pk but no slug, use pk temporarily
        filename = f"partner_{instance.pk}.{ext}"
    else:
        # For new instances, use original filename (will be renamed on save)
        base_name = os.path.splitext(filename)[0]
        filename = f"{base_name}.{ext}"
    return f"images/partner_card/{filename}"


def blog_image_upload_path(instance, filename):
    """Generate upload path for blog images - uses slug to prevent duplicates"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Use blog slug as filename to prevent duplicates
    if instance.slug:
        filename = f"{instance.slug}.{ext}"
    elif instance.pk:
        filename = f"blog_{instance.pk}.{ext}"
    else:
        base_name = os.path.splitext(filename)[0]
        filename = f"{base_name}.{ext}"
    return f"images/blogs/{filename}"


def profile_picture_upload_path(instance, filename):
    """Generate upload path for user profile pictures"""
    ext = filename.split('.')[-1]
    filename = f"user_{instance.user.id}.{ext}"
    return f"profile_pictures/{filename}"


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()






class Category(models.Model):
    """Category model for organizing locations"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji for the category")
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Amenity(models.Model):
    """Amenity model for location features"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji for the amenity")
    
    class Meta:
        verbose_name_plural = "Amenities"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Location(models.Model):
    """Location model for storing places with coordinates"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_locations', help_text="User who created this location")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords for search")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    # New fields for detailed page
    description = models.TextField(blank=True, help_text="Main description of the location")
    image = models.ImageField(upload_to='locations/', blank=True, null=True, help_text="Location/Business image")
    address = models.CharField(max_length=300, blank=True, help_text="Physical address")
    what_we_looking_for = models.TextField(blank=True, help_text="What we're looking for section")
    why_this_matters = models.TextField(blank=True, help_text="Why this matters section")
    how_to_apply = models.TextField(blank=True, help_text="How to apply section")
    email = models.EmailField(blank=True, help_text="Contact email")
    phone = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Rating out of 5.00")
    website = models.URLField(blank=True, help_text="Website URL")
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    
    # Social media links
    social_facebook = models.URLField(blank=True, help_text="Facebook page URL")
    social_twitter = models.URLField(blank=True, help_text="Twitter/X profile URL")
    social_google_plus = models.URLField(blank=True, help_text="Google+ profile URL")
    social_pinterest = models.URLField(blank=True, help_text="Pinterest profile URL")
    
    # Many-to-many relationship with amenities
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='locations')
    
    # Google Maps integration
    place_id = models.CharField(max_length=255, blank=True, help_text="Google Place ID if linked to Google Maps")
    slug = models.SlugField(max_length=250, unique=True, blank=True, help_text="URL-friendly version of the name")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
            models.Index(fields=['place_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def get_keywords_list(self):
        """Return keywords as a list"""
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',') if k.strip()]
        return []


class Review(models.Model):
    """Review model for storing user reviews of places"""
    place_id = models.CharField(max_length=255, help_text="Google Place ID")
    place_name = models.CharField(max_length=200, blank=True, help_text="Place name for reference")
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField(blank=True)
    
    # Ratings (1-5 scale)
    quality_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    location_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    service_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    price_rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    
    # Review content
    review_text = models.TextField()
    
    # Engagement counts
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    hearts = models.IntegerField(default=0)
    
    # Metadata
    save_info = models.BooleanField(default=False, help_text="User wants to save info for next time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['place_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Review by {self.author_name} for {self.place_name}"
    
    def get_average_rating(self):
        """Calculate average of all ratings"""
        return round((self.quality_rating + self.location_rating + self.service_rating + self.price_rating) / 4, 1)


class ReviewReply(models.Model):
    """Model for storing replies to reviews and nested replies"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', help_text="Parent reply if this is a nested reply")
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField(blank=True)
    reply_text = models.TextField()
    
    # Engagement counts
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    hearts = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Review Replies'
        indexes = [
            models.Index(fields=['review']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author_name} to review {self.review.id}"


class PartnerComment(models.Model):
    """Model for storing comments on partner posts"""
    partner = models.ForeignKey('Partner', on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    comment_text = models.TextField()
    save_info = models.BooleanField(default=False, help_text='Save name, email for next time')
    is_approved = models.BooleanField(default=False, help_text='Comment is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['partner', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.partner.title}"


class PartnerCommentReply(models.Model):
    """Model for storing replies to partner comments"""
    comment = models.ForeignKey(PartnerComment, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', help_text='Parent reply if this is a nested reply')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    reply_text = models.TextField()
    is_approved = models.BooleanField(default=False, help_text='Reply is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['comment', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author_name} to comment {self.comment.id}"


class Blog(models.Model):
    """Blog model for storing blog posts"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=300, help_text="Blog post title")
    slug = models.SlugField(max_length=300, unique=True, blank=True, help_text="URL-friendly name (auto-generated from title if left blank)")
    author = models.CharField(max_length=100, default="AccessAdvisr", help_text="Author name")
    content = models.TextField(help_text="Full blog post content (HTML supported)")
    image = models.ImageField(upload_to=blog_image_upload_path, blank=True, null=True, help_text="Blog featured image")
    video_url = models.URLField(blank=True, help_text="YouTube video URL")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', help_text="Blog status")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided and handle image cleanup"""
        # Store old image path before saving
        old_image_path = None
        if self.pk:
            try:
                old_blog = Blog.objects.get(pk=self.pk)
                old_image_path = old_blog.image.path if old_blog.image else None
            except Blog.DoesNotExist:
                pass
        
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Blog.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Save first to get the slug
        super().save(*args, **kwargs)
        
        # If image was updated/removed, delete old image file
        if old_image_path:
            current_image_path = self.image.path if (self.image and hasattr(self.image, 'path')) else None
            if old_image_path != current_image_path and os.path.isfile(old_image_path):
                try:
                    os.remove(old_image_path)
                except (OSError, FileNotFoundError):
                    pass
    
    def delete(self, *args, **kwargs):
        """Delete image file when blog is deleted"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL for the blog detail page"""
        from django.urls import reverse
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def get_comment_count(self):
        """Get count of approved comments"""
        return self.comments.filter(is_approved=True, is_active=True).count()


class BlogComment(models.Model):
    """Model for storing comments on blog posts"""
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    comment_text = models.TextField()
    save_info = models.BooleanField(default=False, help_text='Save name, email for next time')
    is_approved = models.BooleanField(default=False, help_text='Comment is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blog', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.blog.title}"


class BlogCommentReply(models.Model):
    """Model for storing replies to blog comments"""
    comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', help_text='Parent reply if this is a nested reply')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    reply_text = models.TextField()
    is_approved = models.BooleanField(default=False, help_text='Reply is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['comment', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author_name} to comment {self.comment.id}"


class Partner(models.Model):
    """Partner model for storing partner/friend posts"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=300, help_text="Partner post title")
    slug = models.SlugField(max_length=300, unique=True, blank=True, help_text="URL-friendly name (auto-generated from title if left blank)")
    author = models.CharField(max_length=100, default="AccessAdvisr", help_text="Author name")
    image = models.ImageField(upload_to=partner_image_upload_path, blank=True, null=True, help_text="Partner logo/image for card")
    short_description = models.TextField(blank=True, help_text="Short description for card view")
    
    # Video
    video_url = models.URLField(blank=True, help_text="YouTube or video URL")
    
    # Partner Spotlight Section
    partner_spotlight_title = models.CharField(max_length=300, blank=True, help_text="Partner Spotlight heading")
    partner_spotlight_description = models.TextField(blank=True, help_text="Partner Spotlight description")
    
    # Why AccessAdvisr Partners Section
    why_partner_title = models.CharField(max_length=300, blank=True, help_text="Why AccessAdvisr Partners heading")
    why_partner_description = models.TextField(blank=True, help_text="Why AccessAdvisr Partners description")
    
    # Services Section
    services_title = models.CharField(max_length=300, blank=True, default="Services", help_text="Services section title")
    services_description = models.TextField(blank=True, help_text="Services list (one per line or formatted text)")
    
    # Why Partner Supports AccessAdvisr Section
    why_supports_title = models.CharField(max_length=300, blank=True, help_text="Why Partner Supports AccessAdvisr heading")
    why_supports_description = models.TextField(blank=True, help_text="Why Partner Supports AccessAdvisr description")
    
    # Connect Section
    connect_title = models.CharField(max_length=300, blank=True, help_text="Connect section title")
    connect_description = models.TextField(blank=True, help_text="Connect section description")
    website_url = models.URLField(blank=True, help_text="Official website URL")
    
    # Full Content (for blog-like posts)
    content = models.TextField(blank=True, help_text="Full partner post content (HTML supported)")
    
    # Status and ordering
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', help_text="Partner post status")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'order']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided and handle image cleanup"""
        # Store old image path before saving
        old_image_path = None
        if self.pk:
            try:
                old_partner = Partner.objects.get(pk=self.pk)
                old_image_path = old_partner.image.path if old_partner.image else None
            except Partner.DoesNotExist:
                pass
        
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Partner.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Save first to get the slug
        super().save(*args, **kwargs)
        
        # If image was updated/removed, delete old image file
        if old_image_path:
            current_image_path = self.image.path if (self.image and hasattr(self.image, 'path')) else None
            if old_image_path != current_image_path and os.path.isfile(old_image_path):
                try:
                    os.remove(old_image_path)
                except (OSError, FileNotFoundError):
                    pass
    
    def delete(self, *args, **kwargs):
        """Delete image file when partner is deleted"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL for the partner detail page"""
        from django.urls import reverse
        return reverse('partner_detail', kwargs={'slug': self.slug})


def about_post_image_upload_path(instance, filename):
    """Generate upload path for about post images - uses slug to prevent duplicates"""
    ext = filename.split('.')[-1]
    if instance.slug:
        filename = f"{instance.slug}.{ext}"
    elif instance.pk:
        filename = f"about_{instance.pk}.{ext}"
    else:
        base_name = os.path.splitext(filename)[0]
        filename = f"{base_name}.{ext}"
    return f"images/about/{filename}"


class AboutPost(models.Model):
    """About Post model for storing about page posts"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=300, help_text="About post title")
    slug = models.SlugField(max_length=300, unique=True, blank=True, help_text="URL-friendly name (auto-generated from title if left blank)")
    image = models.ImageField(upload_to=about_post_image_upload_path, blank=True, null=True, help_text="Featured image for the post")
    content = models.TextField(help_text="Full post content (HTML supported)")
    share_this_post = models.BooleanField(default=True, help_text="Show share buttons for this post")
    
    # Custom Share Links (optional - if not provided, will use default share URLs)
    share_facebook_url = models.URLField(blank=True, help_text="Custom Facebook share URL (leave blank to use default)")
    share_twitter_url = models.URLField(blank=True, help_text="Custom Twitter/X share URL (leave blank to use default)")
    share_linkedin_url = models.URLField(blank=True, help_text="Custom LinkedIn share URL (leave blank to use default)")
    share_email_url = models.URLField(blank=True, help_text="Custom Email share URL (leave blank to use default)")
    
    # Ordering
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', help_text="Post status")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'About Post'
        verbose_name_plural = 'About Posts'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided and handle image cleanup"""
        old_image_path = None
        if self.pk:
            try:
                old_post = AboutPost.objects.get(pk=self.pk)
                old_image_path = old_post.image.path if old_post.image else None
            except AboutPost.DoesNotExist:
                pass
        
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while AboutPost.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
        
        # If image was updated/removed, delete old image file
        if old_image_path:
            current_image_path = self.image.path if (self.image and hasattr(self.image, 'path')) else None
            if old_image_path != current_image_path and os.path.isfile(old_image_path):
                try:
                    os.remove(old_image_path)
                except (OSError, FileNotFoundError):
                    pass
    
    def delete(self, *args, **kwargs):
        """Delete image file when post is deleted"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """Return the URL for the about post detail page"""
        from django.urls import reverse
        return reverse('about_post_detail', kwargs={'slug': self.slug})


class AboutComment(models.Model):
    """Model for storing comments on about posts"""
    about_post = models.ForeignKey(AboutPost, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    comment_text = models.TextField()
    save_info = models.BooleanField(default=False, help_text='Save name, email for next time')
    is_approved = models.BooleanField(default=False, help_text='Comment is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['about_post', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.about_post.title}"


class AboutCommentReply(models.Model):
    """Model for storing replies to about post comments"""
    comment = models.ForeignKey(AboutComment, on_delete=models.CASCADE, related_name='replies')
    parent_reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_replies', help_text='Parent reply if this is a nested reply')
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    reply_text = models.TextField()
    is_approved = models.BooleanField(default=False, help_text='Reply is approved and visible')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['comment', 'is_approved']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"Reply by {self.author_name} to comment {self.comment.id}"


class DonationCampaign(models.Model):
    """Model for donation campaigns/cards"""
    title = models.CharField(max_length=300, help_text="Campaign title")
    slug = models.SlugField(max_length=300, unique=True, blank=True, help_text="URL-friendly name")
    image = models.ImageField(upload_to='images/donations/', blank=True, null=True, help_text="Campaign image")
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Target donation amount")
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Amount raised so far")
    description = models.TextField(blank=True, help_text="Campaign description")
    is_active = models.BooleanField(default=True, help_text="Is this campaign active?")
    order = models.IntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Donation Campaign'
        verbose_name_plural = 'Donation Campaigns'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'order']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_percentage_raised(self):
        """Calculate percentage of target amount raised"""
        if self.target_amount > 0:
            return round((self.raised_amount / self.target_amount) * 100, 1)
        return 0


class Donation(models.Model):
    """Model for storing donation records"""
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]
    
    DONATION_AMOUNT_CHOICES = [
        ('5', '£5'),
        ('10', '£10'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Campaign reference
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE, related_name='donations', null=True, blank=True, help_text="Associated campaign (optional)")
    
    # Personal Information
    name = models.CharField(max_length=200, help_text="Donor name")
    email = models.EmailField(help_text="Donor email address")
    phone = models.CharField(max_length=20, help_text="Donor phone number")
    
    # Address Information
    street_address = models.CharField(max_length=300, blank=True, help_text="Street address")
    apartment_suite = models.CharField(max_length=100, blank=True, help_text="Apartment, suite, etc")
    city = models.CharField(max_length=100, blank=True, help_text="City")
    state_province = models.CharField(max_length=100, blank=True, help_text="State/Province")
    zip_postal_code = models.CharField(max_length=20, blank=True, help_text="ZIP / Postal Code")
    country = models.CharField(max_length=100, blank=True, help_text="Country")
    
    # Donation Details
    donation_amount = models.CharField(max_length=10, choices=DONATION_AMOUNT_CHOICES, help_text="Donation amount option")
    custom_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Custom donation amount (if 'Other' selected)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, help_text="Payment method")
    
    # Consent
    consent_given = models.BooleanField(default=False, help_text="Consent that information is accurate")
    
    # Payment Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="Donation status")
    transaction_id = models.CharField(max_length=200, blank=True, help_text="Payment transaction ID")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Donation'
        verbose_name_plural = 'Donations'
        indexes = [
            models.Index(fields=['campaign']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"Donation of £{self.get_final_amount()} by {self.name}"
    
    def get_final_amount(self):
        """Get the final donation amount"""
        if self.donation_amount == 'other' and self.custom_amount:
            return self.custom_amount
        elif self.donation_amount in ['5', '10']:
            return float(self.donation_amount)
        return 0


class ContactMessage(models.Model):
    """Model for storing contact form submissions"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200, help_text="Name of the person contacting")
    email = models.EmailField(help_text="Contact email address")
    message = models.TextField(help_text="Message content")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', help_text="Message status")
    admin_notes = models.TextField(blank=True, help_text="Internal notes (not visible to user)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"Message from {self.name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d')}"