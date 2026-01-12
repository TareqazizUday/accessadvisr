from django.core.management.base import BaseCommand
from locations.models import Review
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Create 6 sample reviews based on the image'

    def handle(self, *args, **options):
        reviews_data = [
            {
                'place_id': 'ChIJN1t_tDeuEmsRUsoyG83frY4',
                'place_name': 'Premier Inn London Wembley Park hotel, 151 Wembley Park Dr, Wembley Park',
                'author_name': 'Matt',
                'author_email': 'matt@example.com',
                'quality_rating': 5,
                'location_rating': 4,
                'service_rating': 4,
                'price_rating': 3,
                'review_text': 'Great hotel with good accessibility features. The location is convenient and the staff are helpful.',
            },
            {
                'place_id': 'ChIJ1234567890ABCDEF',
                'place_name': 'Vaillant Live, 2 Colyear St, Derby DE1 1LA',
                'author_name': 'ecologisttobe',
                'author_email': 'ecologisttobe@example.com',
                'quality_rating': 4,
                'location_rating': 4,
                'service_rating': 4,
                'price_rating': 4,
                'review_text': 'Nice venue with good accessibility. The staff were accommodating and the facilities are well-maintained.',
            },
            {
                'place_id': 'ChIJ0987654321FEDCBA',
                'place_name': 'Boathouse Swanwick, Swanwick Marina, Swanwick Shore Rd',
                'author_name': 'Rob Trent',
                'author_email': 'robtrent@example.com',
                'quality_rating': 4,
                'location_rating': 5,
                'service_rating': 3,
                'price_rating': 4,
                'review_text': 'Beautiful location by the marina. Good accessibility features and friendly staff.',
            },
            {
                'place_id': 'ChIJ1111111111111111',
                'place_name': 'London Eye, Westminster Bridge Road, London',
                'author_name': 'Sarah Johnson',
                'author_email': 'sarah@example.com',
                'quality_rating': 5,
                'location_rating': 5,
                'service_rating': 4,
                'price_rating': 3,
                'review_text': 'Amazing experience with excellent accessibility. Wheelchair accessible and staff were very helpful.',
            },
            {
                'place_id': 'ChIJ2222222222222222',
                'place_name': 'Tate Modern, Bankside, London SE1 9TG',
                'author_name': 'David Chen',
                'author_email': 'david@example.com',
                'quality_rating': 5,
                'location_rating': 4,
                'service_rating': 5,
                'price_rating': 5,
                'review_text': 'Fantastic museum with great accessibility. Free entry and excellent facilities for disabled visitors.',
            },
            {
                'place_id': 'ChIJ3333333333333333',
                'place_name': 'Covent Garden Market, London WC2E 8RF',
                'author_name': 'Emily Williams',
                'author_email': 'emily@example.com',
                'quality_rating': 4,
                'location_rating': 4,
                'service_rating': 4,
                'price_rating': 4,
                'review_text': 'Lovely market area with good accessibility. Lots of shops and restaurants with accessible entrances.',
            },
        ]

        base_time = datetime.now()
        created_count = 0

        for i, review_data in enumerate(reviews_data):
            # Check if review already exists
            existing = Review.objects.filter(
                author_name=review_data['author_name'],
                place_name=review_data['place_name']
            ).first()
            
            if existing:
                self.stdout.write(
                    self.style.WARNING(
                        f"Review by {review_data['author_name']} for {review_data['place_name'][:50]}... already exists. Skipping..."
                    )
                )
                continue
            
            # Create review
            created_at = base_time - timedelta(minutes=i*10)
            review = Review.objects.create(
                place_id=review_data['place_id'],
                place_name=review_data['place_name'],
                author_name=review_data['author_name'],
                author_email=review_data['author_email'],
                quality_rating=review_data['quality_rating'],
                location_rating=review_data['location_rating'],
                service_rating=review_data['service_rating'],
                price_rating=review_data['price_rating'],
                review_text=review_data['review_text'],
                is_active=True,
            )
            
            # Update created_at timestamp
            Review.objects.filter(id=review.id).update(created_at=created_at)
            
            created_count += 1
            avg_rating = review.get_average_rating()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created review #{i+1}: {review_data['author_name']} - {review_data['place_name'][:50]}... (Rating: {avg_rating})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTotal reviews created: {created_count}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Total active reviews in database: {Review.objects.filter(is_active=True).count()}'
            )
        )

