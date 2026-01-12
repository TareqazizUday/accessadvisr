// Google Places Search Functions

// Search database
async function searchDatabase(url) {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            console.warn('Database search failed:', response.status);
            return [];
        }
        
        const data = await response.json();
        let locations = [];
        if (Array.isArray(data)) {
            locations = data;
        } else if (data.results && Array.isArray(data.results)) {
            locations = data.results;
        } else if (data.data && Array.isArray(data.data)) {
            locations = data.data;
        }
        
        console.log('Database results:', locations.length);
        return locations;
    } catch (error) {
        console.error('Database search error:', error);
        return [];
    }
}

// Search Google Places
function searchGooglePlaces(locationName, categoryName, keywords) {
    return new Promise((resolve) => {
        if (!placesSearchService || (!locationName && !categoryName && !keywords)) {
            resolve([]);
            return;
        }
        
        // Build search query
        let query = '';
        if (locationName) {
            query = locationName;
        }
        if (categoryName) {
            query = query ? `${query} ${categoryName}` : categoryName;
        }
        if (keywords) {
            query = query ? `${query} ${keywords}` : keywords;
        }
        
        if (!query.trim()) {
            resolve([]);
            return;
        }
        
        console.log('Searching Google Places for:', query);
        
        // Create search request
        const request = {
            query: query,
            fields: ['name', 'geometry', 'formatted_address', 'place_id', 'types', 'rating', 'user_ratings_total'],
        };
        
        placesSearchService.textSearch(request, (results, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && results) {
                console.log('Google Places results:', results.length);
                
                // Convert Places results to our location format
                const locations = results.map(place => ({
                    id: 'places_' + place.place_id,
                    name: place.name,
                    category_name: categoryName || place.types?.[0] || 'Place',
                    latitude: place.geometry.location.lat(),
                    longitude: place.geometry.location.lng(),
                    address: place.formatted_address,
                    rating: place.rating,
                    user_ratings_total: place.user_ratings_total,
                    place_id: place.place_id,
                    is_google_place: true
                }));
                
                resolve(locations);
            } else {
                console.log('Google Places search status:', status);
                resolve([]);
            }
        });
    });
}


