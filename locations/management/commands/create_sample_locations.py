from django.core.management.base import BaseCommand
from locations.models import Location, Category, Amenity
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample locations for testing'

    def handle(self, *args, **options):
        # Create Categories
        categories_data = [
            {'name': 'Education', 'icon': '🎓'},
            {'name': 'Food & Restaurants', 'icon': '🍽️'},
            {'name': 'Entertainment', 'icon': '🎭'},
            {'name': 'Shopping', 'icon': '🛍️'},
            {'name': 'Sport', 'icon': '⚽'},
            {'name': 'Travel & Tour', 'icon': '✈️'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon']}
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {cat.name}'))
        
        # Create Amenities
        amenities_data = [
            'Accepts Credit Cards', 'Elevator', 'Wheelchair Accessible',
            'Parking', 'Wi-Fi', 'Outdoor Seating', 'Air Conditioning',
            'Pet Friendly', 'Reservations', 'Delivery Available',
            'Bike Parking', 'Smoking Allowed'
        ]
        
        amenities = []
        for amenity_name in amenities_data:
            amenity, created = Amenity.objects.get_or_create(name=amenity_name)
            amenities.append(amenity)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created amenity: {amenity.name}'))
        
        # Create Sample Locations
        locations_data = [
            {
                'name': 'Esbury Gardens & Steam Railway',
                'category': 'Entertainment',
                'latitude': Decimal('23.7644'),
                'longitude': Decimal('90.3716'),
                'description': 'Beautiful gardens with steam railway tours',
                'email': 'info@esburygardens.com',
                'website': 'https://esburygardens.com',
                'status': 'active',
            },
            {
                'name': 'Hotel Sercorial La Borofia',
                'category': 'Travel & Tour',
                'latitude': Decimal('23.7550'),
                'longitude': Decimal('90.3820'),
                'description': 'Luxury hotel with modern amenities',
                'email': 'reservations@sercorial.com',
                'website': 'https://hotelsercorial.com',
                'status': 'active',
            },
            {
                'name': 'Enamossa.com Stadium',
                'category': 'Sport',
                'latitude': Decimal('23.7460'),
                'longitude': Decimal('90.3920'),
                'description': 'Modern sports stadium',
                'email': 'info@enamossa.com',
                'website': 'https://enamossa.com',
                'status': 'active',
            },
            {
                'name': 'W Barcelona',
                'category': 'Travel & Tour',
                'latitude': Decimal('23.7380'),
                'longitude': Decimal('90.4020'),
                'description': 'Iconic waterfront hotel',
                'email': 'info@wbarcelona.com',
                'website': 'https://wbarcelona.com',
                'status': 'active',
            },
            {
                'name': 'Titanic Belfast',
                'category': 'Entertainment',
                'latitude': Decimal('23.7300'),
                'longitude': Decimal('90.4120'),
                'description': 'Historical museum and exhibition center',
                'email': 'visit@titanicbelfast.com',
                'website': 'https://titanicbelfast.com',
                'status': 'active',
            },
            {
                'name': 'Yoga & Meditation Center',
                'category': 'Sport',
                'latitude': Decimal('23.7680'),
                'longitude': Decimal('90.3650'),
                'description': 'Peaceful yoga and meditation center',
                'email': 'hello@yogacenter.com',
                'website': 'https://yogacenter.com',
                'status': 'active',
            },
            {
                'name': 'Bar Business - Inclusive Service & Hospitality',
                'category': 'Food & Restaurants',
                'latitude': Decimal('23.7600'),
                'longitude': Decimal('90.3750'),
                'description': 'Premium bar and restaurant services',
                'email': 'contact@barbusiness.com',
                'website': 'https://barbusiness.com',
                'status': 'active',
            },
            {
                'name': 'Spotlight Club',
                'category': 'Entertainment',
                'latitude': Decimal('23.7520'),
                'longitude': Decimal('90.3850'),
                'description': 'Entertainment club with live performances',
                'email': 'events@spotlightclub.com',
                'website': 'https://spotlightclub.com',
                'status': 'active',
            },
            {
                'name': 'Deem Restaurant - Dining Without Barriers',
                'category': 'Food & Restaurants',
                'latitude': Decimal('23.7440'),
                'longitude': Decimal('90.3950'),
                'description': 'Accessible dining experience for all',
                'email': 'info@deemrestaurant.com',
                'website': 'https://deemrestaurant.com',
                'status': 'active',
            },
            {
                'name': 'Tech University',
                'category': 'Education',
                'latitude': Decimal('23.7720'),
                'longitude': Decimal('90.3600'),
                'description': 'Modern technical university',
                'email': 'admissions@techuni.edu',
                'website': 'https://techuni.edu',
                'status': 'active',
            },
            {
                'name': 'City Shopping Mall',
                'category': 'Shopping',
                'latitude': Decimal('23.7580'),
                'longitude': Decimal('90.3780'),
                'description': 'Large shopping complex',
                'email': 'info@citymall.com',
                'website': 'https://citymall.com',
                'status': 'active',
            },
            {
                'name': 'Global Market',
                'category': 'Shopping',
                'latitude': Decimal('23.7500'),
                'longitude': Decimal('90.3880'),
                'description': 'International shopping center',
                'email': 'contact@globalmarket.com',
                'website': 'https://globalmarket.com',
                'status': 'active',
            },
            {
                'name': 'Riverside Cafe',
                'category': 'Food & Restaurants',
                'latitude': Decimal('23.7420'),
                'longitude': Decimal('90.3980'),
                'description': 'Scenic riverside dining',
                'email': 'reserve@riversidecafe.com',
                'website': 'https://riversidecafe.com',
                'status': 'active',
            },
        ]
        
        created_count = 0
        for loc_data in locations_data:
            category = categories[loc_data.pop('category')]
            
            location, created = Location.objects.get_or_create(
                name=loc_data['name'],
                defaults={
                    **loc_data,
                    'category': category
                }
            )
            
            if created:
                # Add random amenities to each location
                location.amenities.add(*amenities[:5])  # Add first 5 amenities
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created location: {location.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} locations!'))
        self.stdout.write(self.style.SUCCESS(f'Total locations in database: {Location.objects.count()}'))
