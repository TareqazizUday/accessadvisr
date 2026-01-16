# AccessAdvisr - Accessible Places Platform

Django-based accessible places directory with Google Maps integration.

## Installation & Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Google Maps API key**
   - Get your API key from [Google Cloud Console](https://console.cloud.google.com/google/maps-apis)
   - Add to `mapsearch/settings.py`:
     ```python
     GOOGLE_MAPS_API_KEY = 'your_api_key_here'
     ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser**
   ```bash
   python make_superuser.py
   ```
   Or manually:
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Frontend: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin
   - Sitemap: http://127.0.0.1:8000/sitemap.xml
   - Robots.txt: http://127.0.0.1:8000/robots.txt

## Default Admin Credentials

- Username: `Tareq`
- Password: `admin123`

## SEO Features

- ✅ SEO-friendly URLs with hyphens
- ✅ XML Sitemap for Google indexing
- ✅ Robots.txt configuration
- ✅ Open Graph & Twitter Cards meta tags
- ✅ Schema.org structured data

## Tech Stack

- Django 4.2.7
- Python 3.14
- Google Maps JavaScript API
- Bootstrap 5.3.8
- Django REST Framework


