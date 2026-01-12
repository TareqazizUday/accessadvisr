# Django + Google Maps Location Search

A Django-based location search application with Google Maps integration. Search, filter, and explore locations on an interactive map.

## Features

- 🗺️ Interactive Google Maps with markers
- 🔍 Keyword-based search (name and keywords)
- 📂 Category filtering
- 📍 Radius-based location search
- 📱 Responsive design
- 🎯 Real-time filtering with debounced search
- 👤 Admin panel for managing locations
- 📊 RESTful API endpoints

## Requirements

- Python 3.10+
- Django 4.2+
- Google Maps JavaScript API key

## Installation

1. **Clone or navigate to the project directory**

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your Google Maps API key:
     ```
     GOOGLE_MAPS_API_KEY=your_api_key_here
     ```
   - Get your API key from [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Frontend: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Getting Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Maps JavaScript API**
4. Go to **Credentials** and create an API key
5. (Recommended) Restrict the API key to your domain
6. Copy the API key to your `.env` file

## Usage

### Admin Panel

1. Log in to the admin panel at `/admin`
2. Create **Categories** first (e.g., Restaurant, Hotel, Park)
3. Add **Locations** with:
   - Name
   - Category
   - Latitude and Longitude
   - Keywords (comma-separated)
   - Status (active/inactive)

### Frontend

- **Search**: Type in the search box to find locations by name or keywords
- **Category Filter**: Select a category to filter locations
- **Radius Search**: Enter your location and set a radius (in km) to find nearby places
- **Use My Location**: Click to use your current location as the center point
- **Markers**: Click on map markers to see location details

## API Endpoints

### Search Locations
```
GET /api/locations/search/
Query Parameters:
  - q: keyword search
  - category: category ID or name
  - lat: latitude (for radius search)
  - lng: longitude (for radius search)
  - radius: radius in kilometers
```

### List All Locations
```
GET /api/locations/
```

### Get Location Detail
```
GET /api/locations/{id}/
```

### List Categories
```
GET /api/categories/
```

### Get Active Categories
```
GET /api/categories/active/
```

## Project Structure

```
mapsearch/
├── locations/          # Main app
│   ├── models.py      # Location and Category models
│   ├── admin.py       # Admin configuration
│   ├── views.py       # API views
│   ├── serializers.py # DRF serializers
│   ├── urls.py        # API routes
│   └── utils.py       # Utility functions (Haversine distance)
├── mapsearch/         # Project settings
│   ├── settings.py    # Django settings
│   └── urls.py        # Root URL configuration
├── templates/         # HTML templates
│   └── index.html     # Main frontend page
├── static/            # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── map.js
└── manage.py
```

## Development

### Adding Sample Data

You can add locations through the admin panel or use Django shell:

```python
python manage.py shell

from locations.models import Category, Location

# Create categories
restaurant = Category.objects.create(name="Restaurant", icon="🍽️")
hotel = Category.objects.create(name="Hotel", icon="🏨")

# Create locations
Location.objects.create(
    name="Example Restaurant",
    category=restaurant,
    latitude=23.8103,
    longitude=90.4125,
    keywords="food, dining, lunch",
    status="active"
)
```

## Security Notes

- Never commit your `.env` file
- Restrict your Google Maps API key in production
- Use environment variables for sensitive data
- Enable HTTPS in production

## Performance

- Database indexes are added on latitude, longitude, category, and status fields
- API responses are paginated (50 items per page)
- Search queries are optimized with database indexes

## Future Enhancements

- User authentication and saved places
- Reviews and ratings
- Advanced marker clustering
- WebSocket for real-time updates
- Analytics dashboard
- CSV bulk upload for locations

## License

This project is open source and available for educational purposes.


