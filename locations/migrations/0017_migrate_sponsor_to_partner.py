# Generated migration to migrate Sponsor data to Partner

from django.db import migrations

def migrate_sponsors_to_partners(apps, schema_editor):
    """Migrate all Sponsor records to Partner records"""
    Sponsor = apps.get_model('locations', 'Sponsor')
    Partner = apps.get_model('locations', 'Partner')
    
    for sponsor in Sponsor.objects.all():
        # Map sponsor fields to partner fields
        partner, created = Partner.objects.get_or_create(
            slug=sponsor.slug,
            defaults={
                'title': sponsor.name,
                'author': 'AccessAdvisr',
                'image': sponsor.image,
                'short_description': sponsor.short_description,
                'video_url': sponsor.video_url,
                'partner_spotlight_title': sponsor.sponsor_spotlight_title,
                'partner_spotlight_description': sponsor.sponsor_spotlight_description,
                'why_partner_title': sponsor.why_partner_title,
                'why_partner_description': sponsor.why_partner_description,
                'services_title': sponsor.services_title,
                'services_description': sponsor.services_description,
                'why_supports_title': sponsor.why_sponsor_title,
                'why_supports_description': sponsor.why_sponsor_description,
                'connect_title': sponsor.connect_title,
                'connect_description': sponsor.connect_description,
                'website_url': sponsor.website_url,
                'status': 'active' if sponsor.status == 'active' else 'inactive',
                'order': sponsor.order,
                'created_at': sponsor.created_at,
                'updated_at': sponsor.updated_at,
            }
        )
        if not created:
            # Update existing partner
            partner.title = sponsor.name
            partner.image = sponsor.image
            partner.short_description = sponsor.short_description
            partner.video_url = sponsor.video_url
            partner.partner_spotlight_title = sponsor.sponsor_spotlight_title
            partner.partner_spotlight_description = sponsor.sponsor_spotlight_description
            partner.why_partner_title = sponsor.why_partner_title
            partner.why_partner_description = sponsor.why_partner_description
            partner.services_title = sponsor.services_title
            partner.services_description = sponsor.services_description
            partner.why_supports_title = sponsor.why_sponsor_title
            partner.why_supports_description = sponsor.why_sponsor_description
            partner.connect_title = sponsor.connect_title
            partner.connect_description = sponsor.connect_description
            partner.website_url = sponsor.website_url
            partner.status = 'active' if sponsor.status == 'active' else 'inactive'
            partner.order = sponsor.order
            partner.save()


def reverse_migration(apps, schema_editor):
    """Reverse migration - not implemented as we're replacing Sponsor"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0016_alter_partner_options_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_sponsors_to_partners, reverse_migration),
    ]

