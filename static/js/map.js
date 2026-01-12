// Global variables
let map;
let markers = [];
let currentLocation = null;
let searchTimeout = null;
const API_BASE = '/api';
let placesService = null;
let placesSearchService = null;

// Initialize map - Make sure it's in global scope for Google Maps callback
window.initMap = function initMap() {
    console.log('🗺️ Initializing map...');
    
    // Check if map element exists
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error('❌ Map element not found!');
        return;
    }
    
    // Check if Google Maps API is loaded
    if (typeof google === 'undefined' || !google.maps) {
        console.error('❌ Google Maps API not loaded!');
        mapElement.innerHTML = '<div style="padding: 2rem; text-align: center; color: red;"><h3>⚠️ Google Maps API Error</h3><p>Google Maps API could not be loaded. Please check your API key.</p></div>';
        return;
    }
    
    // Default center (can be changed)
    const defaultCenter = { lat: 23.8103, lng: 90.4125 }; // Dhaka, Bangladesh
    
    try {
        map = new google.maps.Map(mapElement, {
            zoom: 12,
            center: defaultCenter,
            mapId: 'DEMO_MAP_ID', // Required for Advanced Markers
            mapTypeControl: true,
            streetViewControl: true,
            fullscreenControl: true,
        });
        console.log('✅ Map initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing map:', error);
        mapElement.innerHTML = '<div style="padding: 2rem; text-align: center; color: red;"><h3>⚠️ Map Initialization Error</h3><p>' + error.message + '</p></div>';
        return;
    }

    // Initialize Google Places services (required for searchGooglePlaces)
    try {
        placesService = new google.maps.places.PlacesService(map);
        placesSearchService = new google.maps.places.PlacesService(map);
        console.log('Google Places services initialized');
    } catch (e) {
        console.error('Failed to initialize Google Places services:', e);
    }
    
    // Load initial data
    loadCategories();
    
    // First, get user's current location, then load nearby places
    getCurrentLocationAndLoadPlaces();
    
    // Setup event listeners
    setupEventListeners();
}

// Get user's current location and then load nearby places
function getCurrentLocationAndLoadPlaces() {
    showLoading();
    
    // Update loading message
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        const loadingText = loadingEl.querySelector('p');
        if (loadingText) {
            loadingText.textContent = 'Finding your current location...';
        }
    }
    
    // Check if geolocation is supported
    if (!navigator.geolocation) {
        console.log('Geolocation is not supported by this browser');
        // Use default center and load places
        currentLocation = { lat: 23.8103, lng: 90.4125 };
        map.setCenter(currentLocation);
        loadAllNearbyPlaces();
        return;
    }
    
    // Request current location with timeout
    const locationTimeout = setTimeout(() => {
        // If location takes too long, use default
        console.log('Location request timeout, using default center');
        currentLocation = { lat: 23.8103, lng: 90.4125 };
        map.setCenter(currentLocation);
        if (loadingEl) {
            const loadingText = loadingEl.querySelector('p');
            if (loadingText) {
                loadingText.textContent = 'Using default location...';
            }
        }
        loadAllNearbyPlaces();
    }, 12000); // 12 second timeout
    
    // Try to get current position
    let watchId = null;
    
    navigator.geolocation.getCurrentPosition(
        async (position) => {
            clearTimeout(locationTimeout);
            if (watchId !== null) {
                navigator.geolocation.clearWatch(watchId);
            }
            
            // Success: Get current location
            currentLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            
            console.log('✅ Current location found:', currentLocation);
            console.log('📍 Latitude:', currentLocation.lat);
            console.log('📍 Longitude:', currentLocation.lng);
            console.log('🎯 Accuracy:', Math.round(position.coords.accuracy), 'meters');
            
            // Verify location is set before loading places
            if (!currentLocation.lat || !currentLocation.lng) {
                console.error('❌ Current location not properly set!');
                return;
            }
            
            // Update loading message
            if (loadingEl) {
                const loadingText = loadingEl.querySelector('p');
                if (loadingText) {
                    loadingText.textContent = 'Searching nearby places...';
                }
            }
            
            // Update map center to current location
            map.setCenter(currentLocation);
            map.setZoom(14); // Zoom in a bit for current location
            
            // Add a marker for current location using helper function (async)
            const currentLocationMarker = await createMarker(
                currentLocation,
                'Your Current Location',
                {
                    url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                    scaledSize: new google.maps.Size(40, 40)
                },
                map
            );
            
            // Add info window for current location (but don't auto-open)
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div style="padding: 8px;">
                        <strong>📍 Your Current Location</strong><br/>
                        <small>Lat: ${currentLocation.lat.toFixed(6)}, Lng: ${currentLocation.lng.toFixed(6)}</small><br/>
                        <small>Accuracy: ${Math.round(position.coords.accuracy)}m</small>
                    </div>
                `
            });
            
            // Store info window for click event
            currentLocationMarker.infoWindow = infoWindow;
            
            // Add click listener to show info window when marker is clicked
            const currentLocationClickHandler = () => {
                // Close all other info windows
                markers.forEach(m => {
                    if (m.infoWindow && m !== currentLocationMarker) {
                        m.infoWindow.close();
                    }
                });
                // For AdvancedMarkerElement, use anchor property
                if (currentLocationMarker.addEventListener) {
                    infoWindow.open({
                        anchor: currentLocationMarker,
                        map: map
                    });
                } else {
                    infoWindow.open(map, currentLocationMarker);
                }
            };
            
            if (currentLocationMarker.addEventListener) {
                currentLocationMarker.addEventListener('click', currentLocationClickHandler);
            } else {
                currentLocationMarker.addListener('click', currentLocationClickHandler);
            }
            
            // Store current location marker
            markers.push(currentLocationMarker);
            
            // Now load all nearby places around current location
            loadAllNearbyPlaces();
        },
        (error) => {
            clearTimeout(locationTimeout);
            
            // Error handling with specific messages
            let errorMessage = 'Current location could not be found.';
            
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    console.log('User denied geolocation permission');
                    errorMessage = 'Location access permission denied. Please enable location access in your browser settings.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    console.log('Location information unavailable');
                    errorMessage = 'Location information unavailable.';
                    break;
                case error.TIMEOUT:
                    console.log('Location request timeout');
                    errorMessage = 'Location request timeout.';
                    // Try watchPosition as fallback
                    console.log('Trying watchPosition as fallback...');
                    watchId = navigator.geolocation.watchPosition(
                        (position) => {
                            if (watchId !== null) {
                                navigator.geolocation.clearWatch(watchId);
                            }
                            currentLocation = {
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            };
                            console.log('Location found via watchPosition:', currentLocation);
                            map.setCenter(currentLocation);
                            map.setZoom(14);
                            loadAllNearbyPlaces();
                        },
                        (err) => {
                            console.log('watchPosition also failed:', err.message);
                            useDefaultLocation();
                        },
                        {
                            enableHighAccuracy: false,
                            timeout: 5000,
                            maximumAge: 30000
                        }
                    );
                    return; // Don't proceed to useDefaultLocation yet
                default:
                    console.log('Unknown error:', error.message);
            }
            
            useDefaultLocation();
            
            function useDefaultLocation() {
                console.log('Using default center (Dhaka)');
                currentLocation = { lat: 23.8103, lng: 90.4125 };
                map.setCenter(currentLocation);
                
                // Update loading message
                if (loadingEl) {
                    const loadingText = loadingEl.querySelector('p');
                    if (loadingText) {
                        loadingText.textContent = 'Using default location...';
                    }
                }
                
                // Show message to user (but don't show error if user denied)
                if (error.code !== error.PERMISSION_DENIED) {
                    showError(errorMessage);
                } else {
                    // Show permission message
                    showError(errorMessage);
                }
                
                // Load places with default center
                loadAllNearbyPlaces();
            }
        },
        {
            enableHighAccuracy: true,
            timeout: 15000, // Increased timeout to 15 seconds
            maximumAge: 60000 // Accept cached location if less than 1 minute old
        }
    );
}

// Setup event listeners
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    const locationNameInput = document.getElementById('locationNameInput');
    const categoryNameInput = document.getElementById('categoryNameInput');
    const clearSearch = document.getElementById('clearSearch');
    const clearLocationName = document.getElementById('clearLocationName');
    const clearCategoryName = document.getElementById('clearCategoryName');
    const searchBtn = document.getElementById('searchBtn');
    
    // Search button click (main trigger) - navigate to search results page
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            navigateToSearchResults();
        });
    }
    
    // No real-time search on input change
    // Search will only trigger on Enter key press or Search button click
    
    // Enter key on any input field - navigate to search results page
    [searchInput, locationNameInput, categoryNameInput].forEach(input => {
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    clearTimeout(searchTimeout);
                    navigateToSearchResults();
                }
            });
        }
    });
    
    // Clear buttons - only clear the value, won't trigger search automatically
    if (clearSearch && searchInput) {
        clearSearch.addEventListener('click', () => {
            searchInput.value = '';
            clearTimeout(searchTimeout);
        });
    }
    
    if (clearLocationName && locationNameInput) {
        clearLocationName.addEventListener('click', () => {
            locationNameInput.value = '';
            clearTimeout(searchTimeout);
        });
    }
    
    if (clearCategoryName && categoryNameInput) {
        clearCategoryName.addEventListener('click', () => {
            categoryNameInput.value = '';
            clearTimeout(searchTimeout);
        });
    }
    
    // Details close button
    const detailsCloseBtn = document.getElementById('detailsCloseBtn');
    if (detailsCloseBtn) {
        detailsCloseBtn.addEventListener('click', () => {
            hideLocationDetails();
        });
    }

    // Setup modal listeners
    setupModalListeners();
}

// Load categories from API (for autocomplete suggestions - optional)
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories/active/`);
        const data = await response.json();
        
        // Store categories for potential autocomplete feature
        window.availableCategories = data.map(cat => cat.name);
        console.log('Available categories:', window.availableCategories);
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load all nearby places automatically on map load
// This function is called automatically when page loads to show places near current location
async function loadAllNearbyPlaces() {
    try {
        if (!placesSearchService || !map) {
            console.log('Places service or map not ready');
            hideLoading();
            return;
        }

        showLoading();
        
        // Clear existing markers (current location marker will be preserved automatically)
        clearMarkers();

        // ALWAYS use current location if available - this ensures we show places near user's location
        let center;
        let searchLocation;
        if (currentLocation && currentLocation.lat && currentLocation.lng) {
            center = new google.maps.LatLng(currentLocation.lat, currentLocation.lng);
            searchLocation = center; // Use exact current location for search
            console.log('✅ Using CURRENT LOCATION for search:', currentLocation);
            console.log('📍 Search will be around:', currentLocation.lat, currentLocation.lng);
            console.log('🗺️ Showing places near your current location automatically');
        } else {
            // If current location not available yet, wait a bit and try again
            console.log('⏳ Current location not available yet, waiting 2 seconds...');
            setTimeout(() => {
                if (currentLocation && currentLocation.lat && currentLocation.lng) {
                    console.log('✅ Current location now available, loading places...');
                    loadAllNearbyPlaces();
                } else {
                    // Use map center as fallback after waiting
                    console.log('⚠️ Current location still not available, using map center');
                    center = map.getCenter();
                    searchLocation = center;
                    console.log('📍 Using map center for search:', center.lat(), center.lng());
                    // Continue with loading using map center
                    continueWithSearch();
                }
            }, 2000);
            return; // Wait for current location before continuing
        }
        
        // Continue with search using current location or map center
        continueWithSearch();
        
        async function continueWithSearch() {
        const categories = ['hotels', 'hospitals', 'schools', 'universities', 'restaurants', 'cafes', 'shopping malls', 'parks'];
        const allResults = [];

        console.log('Loading all nearby places for categories:', categories);
        console.log('Search center location:', searchLocation.lat(), searchLocation.lng());

        // Update loading message
        const loadingEl = document.getElementById('loading');
        if (loadingEl) {
            const loadingText = loadingEl.querySelector('p');
            if (loadingText) {
                loadingText.textContent = 'Searching nearby places...';
            }
        }

        // Search for each category with timeout
        for (let i = 0; i < categories.length; i++) {
            const category = categories[i];
            
            // Update progress
            if (loadingEl) {
                const loadingText = loadingEl.querySelector('p');
                if (loadingText) {
                    loadingText.textContent = `Searching: ${category} (${i + 1}/${categories.length})`;
                }
            }
            
            // Add delay between searches to avoid rate limiting
            if (i > 0) {
                await new Promise(resolve => setTimeout(resolve, 300));
            }
            
            try {
                // Map category names to Google Places API types for nearbySearch
                const categoryTypeMap = {
                    'hotels': 'lodging',
                    'hospitals': 'hospital',
                    'schools': 'school',
                    'universities': 'university',
                    'restaurants': 'restaurant',
                    'cafes': 'cafe',
                    'shopping malls': 'shopping_mall',
                    'parks': 'park'
                };
                
                const placeType = categoryTypeMap[category] || category;
                
                console.log(`Searching ${category} (type: ${placeType}) near:`, searchLocation.lat(), searchLocation.lng());
                
                // Use nearbySearch for exact location-based search
                const nearbyRequest = {
                    location: searchLocation, // Exact current location
                    radius: 3000, // 3km radius from current location
                    type: placeType
                };
                
                // Also try textSearch as fallback with location bias
                const textRequest = {
                    query: category,
                    location: searchLocation, // Use exact current location as bias
                    radius: 3000
                };

                // Add timeout to prevent hanging
                const results = await Promise.race([
                    new Promise((resolve) => {
                        const pageResults = [];
                        let isResolved = false;
                        let timeoutId = null;
                        
                        // Try nearbySearch first (more accurate for location)
                        const handleNearbySearch = (results, status) => {
                            if (isResolved) return;
                            
                            if (status === google.maps.places.PlacesServiceStatus.OK && results && results.length > 0) {
                                console.log(`✅ nearbySearch found ${results.length} ${category} places`);
                                pageResults.push(...results);
                                if (timeoutId) clearTimeout(timeoutId);
                                isResolved = true;
                                resolve(pageResults);
                            } else {
                                // Fallback to textSearch if nearbySearch fails or returns no results
                                console.log(`⚠️ nearbySearch ${status}, trying textSearch for ${category}`);
                                placesSearchService.textSearch(textRequest, handleTextSearch);
                            }
                        };
                        
                        const handleTextSearch = (results, status, pagination) => {
                            if (isResolved) return;
                            
                            if (status === google.maps.places.PlacesServiceStatus.OK && results) {
                                pageResults.push(...results);
                                if (pagination && pagination.hasNextPage) {
                                    // Clear previous timeout
                                    if (timeoutId) clearTimeout(timeoutId);
                                    // Set timeout for next page
                                    timeoutId = setTimeout(() => {
                                        if (!isResolved) {
                                            pagination.nextPage();
                                        }
                                    }, 1500);
                                } else {
                                    if (timeoutId) clearTimeout(timeoutId);
                                    isResolved = true;
                                    resolve(pageResults);
                                }
                            } else {
                                if (timeoutId) clearTimeout(timeoutId);
                                isResolved = true;
                                // Don't treat errors as failures, just return empty
                                resolve(pageResults);
                            }
                        };
                        
                        // Start with nearbySearch for exact location
                        placesSearchService.nearbySearch(nearbyRequest, handleNearbySearch);
                        
                        // Overall timeout for this category (12 seconds to allow both searches)
                        setTimeout(() => {
                            if (!isResolved) {
                                if (timeoutId) clearTimeout(timeoutId);
                                isResolved = true;
                                console.log(`⏱️ Timeout for category: ${category}, returning ${pageResults.length} results`);
                                resolve(pageResults); // Return what we have so far
                            }
                        }, 12000);
                    }),
                    // Timeout fallback
                    new Promise(resolve => setTimeout(() => resolve([]), 12000))
                ]);

                // Convert to location format
                const locations = results.map(place => ({
                    id: 'places_' + place.place_id,
                    name: place.name,
                    category_name: category,
                    latitude: place.geometry.location.lat(),
                    longitude: place.geometry.location.lng(),
                    address: place.formatted_address,
                    rating: place.rating,
                    user_ratings_total: place.user_ratings_total,
                    place_id: place.place_id,
                    is_google_place: true,
                    types: place.types || []
                }));

                allResults.push(...locations);
                console.log(`Found ${locations.length} places for ${category}`);
            } catch (error) {
                console.error(`Error loading places for ${category}:`, error);
                // Continue with next category even if one fails
            }
        }

        // Remove duplicates based on place_id
        const uniqueResults = [];
        const seenIds = new Set();
        for (const result of allResults) {
            if (!seenIds.has(result.place_id)) {
                seenIds.add(result.place_id);
                uniqueResults.push(result);
            }
        }

        console.log(`Total unique places loaded: ${uniqueResults.length}`);

        // Add markers to map
        if (uniqueResults.length > 0) {
            uniqueResults.forEach(location => {
                addMarker(location);
            });
            fitMapToMarkers();
            
            // Show success message
            showSuccess(`${uniqueResults.length} places found`);
        } else {
            // Show message if no results
            showError('No places found. Please try again.');
        }

        // Always hide loading, even if there's an error
        hideLoading();
        } // End of continueWithSearch function
    } catch (error) {
        console.error('Error in loadAllNearbyPlaces:', error);
        hideLoading();
        showError('Error loading places. Please try again.');
    }
}

// Navigate to search results page
function navigateToSearchResults() {
    const locationNameInput = document.getElementById('locationNameInput');
    const categoryNameInput = document.getElementById('categoryNameInput');
    const searchInput = document.getElementById('searchInput');
    
    const locationName = locationNameInput ? locationNameInput.value.trim() : '';
    const categoryName = categoryNameInput ? categoryNameInput.value.trim() : '';
    const keywords = searchInput ? searchInput.value.trim() : '';
    
    // Build query parameters
    const params = new URLSearchParams();
    if (locationName) params.append('location', locationName);
    if (categoryName) params.append('category', categoryName);
    if (keywords) params.append('keywords', keywords);
    
    // Navigate to search results page
    window.location.href = `/search/?${params.toString()}`;
}

// Load locations from API
async function loadLocations() {
    showLoading();
    clearMarkers();
    
    try {
        const searchInput = document.getElementById('searchInput');
        const locationNameInput = document.getElementById('locationNameInput');
        const categoryNameInput = document.getElementById('categoryNameInput');
        
        // Build query parameters
        const params = new URLSearchParams();
        
        // Get search values
        const locationName = locationNameInput ? locationNameInput.value.trim() : '';
        const categoryName = categoryNameInput ? categoryNameInput.value.trim() : '';
        const keywords = searchInput ? searchInput.value.trim() : '';
        
        // If no search criteria, load all locations
        if (!locationName && !categoryName && !keywords) {
            const url = `${API_BASE}/locations/`;
            console.log('No search criteria, loading all locations');
            
            try {
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                let locations = [];
                if (Array.isArray(data)) {
                    locations = data;
                } else if (data.results && Array.isArray(data.results)) {
                    locations = data.results;
                }
                
                console.log('All locations loaded:', locations.length);
                
                // Update UI
                const resultCountEl = document.getElementById('resultCount');
                if (resultCountEl) {
                    resultCountEl.textContent = locations.length;
                }
                
                if (locations.length > 0) {
                    for (const location of locations) {
                        await addMarker(location);
                    }
                    updateLocationList(locations);
                    fitMapToMarkers();
                } else {
                    clearMarkers();
                    const locationList = document.getElementById('locationList');
                    if (locationList) {
                        locationList.innerHTML = '<p style="color: #999; padding: 1rem; text-align: center;">No locations in database. Add locations through admin panel.</p>';
                    }
                    // Don't show error message for empty database
                }
                
                hideLoading();
                return;
            } catch (error) {
                console.error('Error loading all locations:', error);
                // Don't show error, just show empty state
                clearMarkers();
                const locationList = document.getElementById('locationList');
                if (locationList) {
                    locationList.innerHTML = '<p style="color: #999; padding: 1rem; text-align: center;">No locations in database. Add locations through admin panel.</p>';
                }
                const resultCountEl = document.getElementById('resultCount');
                if (resultCountEl) {
                    resultCountEl.textContent = '0';
                }
                hideLoading();
                return;
            }
        }
        
        // Build search query parameters
        if (locationName) {
            params.append('q', locationName);
            console.log('Location name search:', locationName);
        }
        
        if (categoryName) {
            params.append('category', categoryName);
            console.log('Category name search:', categoryName);
        }
        
        if (keywords) {
            if (locationName) {
                params.set('q', locationName + ' ' + keywords);
            } else {
                params.append('q', keywords);
            }
            console.log('Keywords search:', keywords);
        }
        
        // Use search endpoint
        const url = `${API_BASE}/locations/search/?${params.toString()}`;
        
        console.log('=== SEARCH REQUEST ===');
        console.log('URL:', url);
        console.log('Location Name:', locationName);
        console.log('Category Name:', categoryName);
        console.log('Keywords:', keywords);
        console.log('Params:', params.toString());
        
        // Search both database and Google Places
        const [dbResults, placesResults] = await Promise.all([
            searchDatabase(url),
            searchGooglePlaces(locationName, categoryName, keywords)
        ]);
        
        // Combine results
        const allLocations = [...dbResults, ...placesResults];
        console.log('Total locations found:', allLocations.length, '(DB:', dbResults.length, ', Places:', placesResults.length, ')');
        
        // Update result count
        const resultCountEl = document.getElementById('resultCount');
        if (resultCountEl) {
            resultCountEl.textContent = allLocations.length;
        }
        
        // Add markers to map
        if (allLocations.length > 0) {
            for (const location of allLocations) {
                await addMarker(location);
            }
            
            // Update location list
            updateLocationList(allLocations);
            
            // Adjust map bounds if there are locations
            fitMapToMarkers();
            
            // Show success message briefly (only if search was performed)
            if (locationName || categoryName || keywords) {
                showSuccess(`Found ${allLocations.length} location(s)`);
            }
        } else {
            // Clear markers
            clearMarkers();
            
            // Clear location list
            const locationList = document.getElementById('locationList');
            if (locationList) {
                if (locationName || categoryName || keywords) {
                    locationList.innerHTML = '<p style="color: #999; padding: 1rem; text-align: center;">No locations found matching your search criteria.</p>';
                } else {
                    locationList.innerHTML = '<p style="color: #999; padding: 1rem; text-align: center;">No locations in database. Add locations through admin panel.</p>';
                }
            }
        }
        
        hideLoading();
    } catch (error) {
        console.error('Error loading locations:', error);
        showError('Error loading locations: ' + error.message);
        hideLoading();
    }
}

// Helper function to create marker using AdvancedMarkerElement
async function createMarker(position, title, icon, map) {
    // Check if AdvancedMarkerElement is available
    if (typeof google.maps.marker === 'undefined' || !google.maps.marker.AdvancedMarkerElement) {
        console.warn('AdvancedMarkerElement not available, falling back to traditional Marker');
        // Fallback to traditional Marker if AdvancedMarkerElement is not available
        const markerOptions = {
            position: position,
            map: map,
            title: title,
            animation: google.maps.Animation.DROP
        };
        if (icon) {
            markerOptions.icon = icon;
        }
        return new google.maps.Marker(markerOptions);
    }

    // Use AdvancedMarkerElement with PinElement for custom icons
    let pinElement = null;
    
    if (icon && icon.url) {
        // Create PinElement with custom icon
        pinElement = new google.maps.marker.PinElement({
            background: '#4285F4',
            borderColor: '#ffffff',
            glyphColor: '#ffffff',
            scale: 1.0
        });
        
        // If custom icon URL provided, use it
        if (icon.url) {
            // For AdvancedMarkerElement, we need to use content with an image
            const img = document.createElement('img');
            img.src = icon.url;
            img.style.width = icon.scaledSize ? icon.scaledSize.width + 'px' : '32px';
            img.style.height = icon.scaledSize ? icon.scaledSize.height + 'px' : '32px';
            img.style.objectFit = 'contain';
            pinElement = img;
        }
    } else {
        // Default pin
        pinElement = new google.maps.marker.PinElement({
            background: '#4285F4',
            borderColor: '#ffffff',
            glyphColor: '#ffffff',
            scale: 1.0
        });
    }

    const marker = new google.maps.marker.AdvancedMarkerElement({
        map: map,
        position: position,
        title: title,
        content: pinElement
    });

    return marker;
}

// Add marker to map (async for AdvancedMarkerElement)
async function addMarker(location) {
    const position = {
        lat: parseFloat(location.latitude),
        lng: parseFloat(location.longitude)
    };

    // Pick icon based on category / type
    const icon = getMarkerIcon(location);

    // Create marker using helper function (async)
    const marker = await createMarker(position, location.name, icon, map);

    // Info window (content will be set on click, so we can show full details)
    const infoWindow = new google.maps.InfoWindow();

    // Use addEventListener for AdvancedMarkerElement, addListener for traditional Marker
    const clickHandler = () => {
        // Close all other info windows
        markers.forEach(m => {
            if (m.infoWindow) {
                m.infoWindow.close();
            }
        });

        // Highlight in list (even if hidden in UI, harmless)
        highlightLocationInList(location.id);

        // If Google Place, fetch rich details first
        if (location.is_google_place && location.place_id && placesService) {
            const request = {
                placeId: location.place_id,
                fields: [
                    'name',
                    'formatted_address',
                    'rating',
                    'user_ratings_total',
                    'photos',
                    'types',
                    'website',
                    'international_phone_number',
                    'opening_hours',
                    'reviews'
                ]
            };
            placesService.getDetails(request, (place, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && place) {
                    const html = buildInfoWindowContent(location, place);
                    infoWindow.setContent(html);
                } else {
                    console.warn('Places details status (for infoWindow):', status);
                    const html = buildInfoWindowContent(location, null);
                    infoWindow.setContent(html);
                }
                infoWindow.open(map, marker);
                marker.infoWindow = infoWindow;
            });
        } else {
            const html = buildInfoWindowContent(location, null);
            infoWindow.setContent(html);
            // For AdvancedMarkerElement, use marker as anchor
            infoWindow.open({
                anchor: marker,
                map: map
            });
            marker.infoWindow = infoWindow;
        }
    };
    
    // Add event listener (works for both AdvancedMarkerElement and traditional Marker)
    if (marker.addEventListener) {
        marker.addEventListener('click', clickHandler);
    } else {
        marker.addListener('click', clickHandler);
    }

    marker.infoWindow = infoWindow;
    markers.push(marker);
}

// Show rich details panel (image, rating, etc.)
function showLocationDetails(location) {
    const panel = document.getElementById('detailsPanel');
    const contentEl = document.getElementById('detailsContent');
    if (!panel || !contentEl) return;

    // If it's a Google Place and we have place_id, try to fetch more details
    if (location.is_google_place && location.place_id && placesService) {
        const request = {
            placeId: location.place_id,
            fields: [
                'name',
                'formatted_address',
                'rating',
                'user_ratings_total',
                'photos',
                'types',
                'url',
                'website',
                'international_phone_number',
                'opening_hours',
                'reviews'
            ]
        };

        placesService.getDetails(request, (place, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && place) {
                renderLocationDetails(location, place);
            } else {
                console.warn('Places details status:', status);
                renderLocationDetails(location, null);
            }
        });
    } else {
        renderLocationDetails(location, null);
    }

    panel.classList.remove('hidden');
}

function hideLocationDetails() {
    const panel = document.getElementById('detailsPanel');
    if (panel) {
        panel.classList.add('hidden');
    }
}

function renderLocationDetails(location, placeDetails) {
    const contentEl = document.getElementById('detailsContent');
    if (!contentEl) return;

    let photoUrl = '';
    if (placeDetails && placeDetails.photos && placeDetails.photos.length > 0) {
        // Get a medium sized photo
        photoUrl = placeDetails.photos[0].getUrl({ maxWidth: 400, maxHeight: 250 });
    }

    const name = placeDetails?.name || location.name;
    const address = placeDetails?.formatted_address || location.address || '';
    const rating = placeDetails?.rating || location.rating;
    const userRatings = placeDetails?.user_ratings_total ?? location.user_ratings_total;
    const website = placeDetails?.website || '';
    const phone = placeDetails?.international_phone_number || '';
    const openingHours = placeDetails?.opening_hours;
    const reviews = Array.isArray(placeDetails?.reviews) ? placeDetails.reviews.slice(0, 3) : [];

    const category = location.category_name || (Array.isArray(location.types) ? location.types[0] : '');

    const hoursText = openingHours && Array.isArray(openingHours.weekday_text)
        ? openingHours.weekday_text[new Date().getDay() - 1 >= 0 ? new Date().getDay() - 1 : 6]
        : '';

    const reviewsHtml = reviews.length
        ? `<div class="details-reviews">
                <strong style="font-size:0.9rem;">Top reviews</strong>
                <ul style="list-style:none; padding-left:0; margin:0.25rem 0 0 0;">
                    ${reviews
                        .map(
                            (r) => `
                            <li style="margin-bottom:0.35rem; font-size:0.8rem; color:#555;">
                                <span style="color:#ff9800;">⭐ ${r.rating}</span>
                                <span style="color:#777;"> ${r.author_name || ''}</span><br/>
                                ${r.text ? r.text.substring(0, 140) + (r.text.length > 140 ? '…' : '') : ''}
                            </li>
                        `
                        )
                        .join('')}
                </ul>
           </div>`
        : '';

    contentEl.innerHTML = `
        ${photoUrl ? `<img src="${photoUrl}" alt="${name}" class="details-image" />` : ''}
        <h2>${name}</h2>
        ${category ? `<div class="details-meta">${category}</div>` : ''}
        ${address ? `<div class="details-address">${address}</div>` : ''}
        ${rating ? `<div class="details-rating">⭐ ${rating} (${userRatings || 0} reviews)</div>` : ''}
        ${hoursText ? `<div class="details-meta">${hoursText}</div>` : ''}
        ${phone ? `<div class="details-meta">📞 ${phone}</div>` : ''}
        ${
            website
                ? `<div class="details-links"><a href="${website}" target="_blank" rel="noopener">🌐 Website</a></div>`
                : ''
        }
        ${reviewsHtml}
    `;
}

// Build HTML string for map popup (infoWindow) with rich details
function buildInfoWindowContent(location, placeDetails) {
    let photoUrl = '';
    if (placeDetails && placeDetails.photos && placeDetails.photos.length > 0) {
        photoUrl = placeDetails.photos[0].getUrl({ maxWidth: 400, maxHeight: 200 });
    }

    const name = placeDetails?.name || location.name;
    const address = placeDetails?.formatted_address || location.address || '';
    const rating = placeDetails?.rating || location.rating;
    const userRatings = placeDetails?.user_ratings_total ?? location.user_ratings_total;
    const openingHours = placeDetails?.opening_hours;
    const website = placeDetails?.website || '';
    const phone = placeDetails?.international_phone_number || '';
    const reviews = Array.isArray(placeDetails?.reviews) ? placeDetails.reviews.slice(0, 1) : [];
    const category = location.category_name || (Array.isArray(location.types) ? location.types[0] : '');
    const placeUrl = location.is_google_place && location.place_id ? `/place/google/${location.place_id}/` : null;

    const hoursText = openingHours && Array.isArray(openingHours.weekday_text)
        ? openingHours.weekday_text[new Date().getDay() - 1 >= 0 ? new Date().getDay() - 1 : 6]
        : '';

    const reviewHtml = reviews.length
        ? `<div style="margin-top:4px; font-size:0.8rem; color:#555;">
               <strong style="color:#444;">Latest review:</strong><br/>
               <span style="color:#ff9800;">⭐ ${reviews[0].rating}</span>
               <span style="color:#777;"> ${reviews[0].author_name || ''}</span><br/>
               ${reviews[0].text ? reviews[0].text.substring(0, 120) + (reviews[0].text.length > 120 ? '…' : '') : ''}
           </div>`
        : '';

    const titleHtml = placeUrl
        ? `<h3 style="margin: 0 0 6px 0; font-size: 1rem;">
               <a href="${placeUrl}" style="color:#1976d2; text-decoration:none;">
                   ${name}
               </a>
           </h3>`
        : `<h3 style="margin: 0 0 6px 0; color: #1976d2; font-size: 1rem;">${name}</h3>`;

    const detailsLink = placeUrl
        ? `<div style="margin-top:6px; font-size:0.8rem;">
               <a href="${placeUrl}" style="color:#1976d2; text-decoration:none;">
                   View full details
               </a>
           </div>`
        : '';

    return `
        <div style="padding: 10px; min-width: 260px; max-width: 320px;">
            ${photoUrl ? `<img src="${photoUrl}" alt="${name}" style="width:100%; border-radius:8px; margin-bottom:8px; object-fit:cover; max-height:160px;" />` : ''}
            ${titleHtml}
            ${category ? `<div style="margin: 0 0 4px 0; color: #666; font-size:0.85rem;">${category}</div>` : ''}
            ${address ? `<div style="margin: 0 0 4px 0; color: #666; font-size:0.8rem;">${address}</div>` : ''}
            ${rating ? `<div style="margin: 0 0 4px 0; color: #444; font-size:0.85rem;">⭐ ${rating} (${userRatings || 0} reviews)</div>` : ''}
            ${hoursText ? `<div style="margin: 0 0 4px 0; color:#555; font-size:0.8rem;">${hoursText}</div>` : ''}
            ${phone ? `<div style="margin: 0 0 4px 0; color:#555; font-size:0.8rem;">📞 <a href="tel:${phone.replace(/\\s+/g,'')}" style="color:#555; text-decoration:none;">${phone}</a></div>` : ''}
            ${website ? `<div style="margin: 0 0 4px 0; font-size:0.8rem;">🌐 <a href="${website}" target="_blank" rel="noopener" style="color:#1976d2; text-decoration:none;">Website</a></div>` : ''}
            ${reviewHtml}
            ${detailsLink}
        </div>
    `;
}

// Clear all markers (but preserve current location marker)
function clearMarkers() {
    // Preserve current location marker
    const currentLocationMarker = markers.find(m => m.title === 'Your Current Location');
    
    markers.forEach(marker => {
        // Don't remove current location marker
        if (marker.title === 'Your Current Location') {
            return;
        }
        marker.setMap(null);
        if (marker.infoWindow) {
            marker.infoWindow.close();
        }
    });
    
    // Keep only current location marker if it exists
    markers = currentLocationMarker ? [currentLocationMarker] : [];
}

// Fit map to show all markers
function fitMapToMarkers() {
    if (markers.length === 0) return;
    
    const bounds = new google.maps.LatLngBounds();
    markers.forEach(marker => {
        let pos;
        // AdvancedMarkerElement uses position property, traditional Marker uses getPosition()
        if (marker.position) {
            pos = marker.position;
        } else if (marker.getPosition) {
            pos = marker.getPosition();
        } else {
            return;
        }
        
        // Handle both LatLng object and position object
        if (typeof pos.lat === 'function') {
            bounds.extend(pos);
        } else {
            bounds.extend({ lat: pos.lat, lng: pos.lng });
        }
    });
    
    map.fitBounds(bounds);
    
    // Don't zoom in too much if only one marker
    if (markers.length === 1) {
        map.setZoom(14);
    }
}

// Update location list in info panel
function updateLocationList(locations) {
    const locationList = document.getElementById('locationList');
    locationList.innerHTML = '';
    
    if (locations.length === 0) {
        locationList.innerHTML = '<p style="color: #999;">No locations found</p>';
        return;
    }
    
    locations.forEach(location => {
        const item = document.createElement('div');
        item.className = 'location-item';
        item.dataset.locationId = location.id;

        const emoji = getCategoryEmoji(location);

        let content = `${emoji} <strong>${location.name}</strong>`;
        if (location.category_name) {
            content += ` <span style="color: #666;">(${location.category_name})</span>`;
        }
        if (location.is_google_place) {
            content += ` <span style="color: #1976d2; font-size: 0.85em;">Google</span>`;
        }
        if (location.rating) {
            content += ` <span style="color: #ff9800;">⭐ ${location.rating}</span>`;
        }
        if (location.distance !== null && location.distance !== undefined) {
            content += ` <span style="color: #1976d2;">${location.distance} km</span>`;
        }

        item.innerHTML = content;
        
        item.addEventListener('click', () => {
            // Find and click the corresponding marker
            const marker = markers.find(m => {
                let pos;
                // AdvancedMarkerElement uses position property, traditional Marker uses getPosition()
                if (m.position) {
                    pos = m.position;
                } else if (m.getPosition) {
                    pos = m.getPosition();
                } else {
                    return false;
                }
                const lat = typeof pos.lat === 'function' ? pos.lat() : pos.lat;
                const lng = typeof pos.lng === 'function' ? pos.lng() : pos.lng;
                return Math.abs(lat - parseFloat(location.latitude)) < 0.0001 &&
                       Math.abs(lng - parseFloat(location.longitude)) < 0.0001;
            });
            
            if (marker) {
                // Trigger click event
                if (marker.addEventListener) {
                    // For AdvancedMarkerElement, dispatch click event
                    const clickEvent = new Event('click');
                    marker.dispatchEvent(clickEvent);
                } else {
                    google.maps.event.trigger(marker, 'click');
                }
                
                // Center map on marker
                let markerPos;
                if (marker.position) {
                    markerPos = marker.position;
                } else if (marker.getPosition) {
                    markerPos = marker.getPosition();
                }
                if (markerPos) {
                    const lat = typeof markerPos.lat === 'function' ? markerPos.lat() : markerPos.lat;
                    const lng = typeof markerPos.lng === 'function' ? markerPos.lng() : markerPos.lng;
                    map.setCenter({ lat, lng });
                    map.setZoom(15);
                }
            }
        });
        
        locationList.appendChild(item);
    });
}

// Highlight location in list
function highlightLocationInList(locationId) {
    document.querySelectorAll('.location-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.locationId == locationId) {
            item.classList.add('active');
        }
    });
}

// Show loading indicator
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

// Hide loading indicator
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Show error message
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

// Modal Functions
function setupModalListeners() {
    // Location modal
    const locationModal = document.getElementById('addLocationModal');
    const locationForm = document.getElementById('locationForm');
    const cancelLocationBtn = document.getElementById('cancelLocationForm');
    const addCategoryBtn = document.getElementById('addCategoryBtn');
    const getMapLocationBtn = document.getElementById('getMapLocation');
    
    // Category modal
    const categoryModal = document.getElementById('addCategoryModal');
    const categoryForm = document.getElementById('categoryForm');
    const cancelCategoryBtn = document.getElementById('cancelCategoryForm');
    
    // Close modals on X click
    document.querySelectorAll('.close-modal').forEach(closeBtn => {
        closeBtn.addEventListener('click', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) {
                modal.classList.add('hidden');
            }
        });
    });
    
    // Close modals on outside click
    [locationModal, categoryModal].forEach(modal => {
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        }
    });
    
    // Cancel buttons
    if (cancelLocationBtn) {
        cancelLocationBtn.addEventListener('click', () => {
            locationModal.classList.add('hidden');
            locationForm.reset();
        });
    }
    
    if (cancelCategoryBtn) {
        cancelCategoryBtn.addEventListener('click', () => {
            categoryModal.classList.add('hidden');
            categoryForm.reset();
        });
    }
    
    // Location form submit
    if (locationForm) {
        locationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveLocation();
        });
    }
    
    // Category form submit
    if (categoryForm) {
        categoryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveCategory();
        });
    }
    
    // Add category button in location form
    if (addCategoryBtn) {
        addCategoryBtn.addEventListener('click', () => {
            locationModal.classList.add('hidden');
            openCategoryModal();
        });
    }
    
    // Get location from map click
    if (getMapLocationBtn) {
        getMapLocationBtn.addEventListener('click', () => {
            enableMapClickForLocation();
        });
    }
}

function openLocationModal() {
    const modal = document.getElementById('addLocationModal');
    const categorySelect = document.getElementById('locationCategory');
    
    // Populate category dropdown
    populateCategoryDropdown(categorySelect);
    
    // Set current map center as default if available
    if (map) {
        const center = map.getCenter();
        document.getElementById('locationLat').value = center.lat().toFixed(6);
        document.getElementById('locationLng').value = center.lng().toFixed(6);
    }
    
    modal.classList.remove('hidden');
}

function openCategoryModal() {
    const modal = document.getElementById('addCategoryModal');
    modal.classList.remove('hidden');
}

async function saveCategory() {
    const name = document.getElementById('categoryName').value.trim();
    const icon = document.getElementById('categoryIcon').value.trim();
    
    if (!name) {
        showError('Category name is required');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE}/categories/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                icon: icon || ''
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.name || 'Failed to save category');
        }
        
        const category = await response.json();
        
        // Close modal
        document.getElementById('addCategoryModal').classList.add('hidden');
        document.getElementById('categoryForm').reset();
        
        // Reload categories
        await loadCategories();
        
        // If location modal was open, update its category dropdown
        const locationCategorySelect = document.getElementById('locationCategory');
        if (locationCategorySelect) {
            populateCategoryDropdown(locationCategorySelect);
            locationCategorySelect.value = category.id;
        }
        
        // Reopen location modal if it was open before
        const locationModal = document.getElementById('addLocationModal');
        if (!locationModal.classList.contains('hidden')) {
            locationModal.classList.remove('hidden');
        }
        
        showSuccess('Category added successfully!');
        hideLoading();
    } catch (error) {
        showError('Error saving category: ' + error.message);
        hideLoading();
    }
}

async function saveLocation() {
    const name = document.getElementById('locationName').value.trim();
    const categoryId = document.getElementById('locationCategory').value;
    const lat = document.getElementById('locationLat').value;
    const lng = document.getElementById('locationLng').value;
    const keywords = document.getElementById('locationKeywords').value.trim();
    
    if (!name || !lat || !lng) {
        showError('Name, latitude, and longitude are required');
        return;
    }
    
    // Validate coordinates
    const latNum = parseFloat(lat);
    const lngNum = parseFloat(lng);
    
    if (isNaN(latNum) || isNaN(lngNum)) {
        showError('Invalid coordinates');
        return;
    }
    
    if (latNum < -90 || latNum > 90 || lngNum < -180 || lngNum > 180) {
        showError('Coordinates out of range');
        return;
    }
    
    try {
        showLoading();
        const data = {
            name: name,
            latitude: latNum,
            longitude: lngNum,
            keywords: keywords,
            status: 'active'
        };
        
        if (categoryId) {
            data.category_id = parseInt(categoryId);
        }
        
        const response = await fetch(`${API_BASE}/locations/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.name || 'Failed to save location');
        }
        
        const location = await response.json();
        
        // Close modal
        document.getElementById('addLocationModal').classList.add('hidden');
        document.getElementById('locationForm').reset();
        
        // Reload locations
        await loadLocations();
        
        // Center map on new location
        if (map) {
            map.setCenter({ lat: latNum, lng: lngNum });
            map.setZoom(15);
        }
        
        showSuccess('Location added successfully!');
        hideLoading();
    } catch (error) {
        showError('Error saving location: ' + error.message);
        hideLoading();
    }
}

function populateCategoryDropdown(selectElement) {
    // Clear existing options except first one
    selectElement.innerHTML = '<option value="">Select Category</option>';
    
    // Get categories from the filter dropdown
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        Array.from(categoryFilter.options).forEach(option => {
            if (option.value) {
                const newOption = document.createElement('option');
                newOption.value = option.value;
                newOption.textContent = option.textContent;
                selectElement.appendChild(newOption);
            }
        });
    }
}

function enableMapClickForLocation() {
    if (!map) return;
    
    // Change cursor
    map.setOptions({ draggableCursor: 'crosshair' });
    
    // Add click listener
    const clickListener = map.addListener('click', (e) => {
        const lat = e.latLng.lat();
        const lng = e.latLng.lng();
        
        document.getElementById('locationLat').value = lat.toFixed(6);
        document.getElementById('locationLng').value = lng.toFixed(6);
        
        // Remove listener and restore cursor
        google.maps.event.removeListener(clickListener);
        map.setOptions({ draggableCursor: null });
        
        showSuccess('Location coordinates set from map click!');
    });
    
    showSuccess('Click on the map to set location coordinates');
}

function showSuccess(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.style.background = '#4caf50';
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    setTimeout(() => {
        errorDiv.classList.add('hidden');
        errorDiv.style.background = '#f44336';
    }, 3000);
}

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

// Search Google Places (with pagination, up to ~60 results)
function searchGooglePlaces(locationName, categoryName, keywords) {
    return new Promise((resolve) => {
        if (!placesSearchService || (!locationName && !categoryName && !keywords)) {
            resolve([]);
            return;
        }

        // Build search query string
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

        const allResults = [];

        // Helper to process one page and, if available, the next ones
        const handlePage = (results, status, pagination) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && results) {
                console.log('Google Places page results:', results.length);
                allResults.push(...results);

                // If there is a next page, request it after required delay (~2s)
                if (pagination && pagination.hasNextPage) {
                    console.log('Google Places has next page, fetching...');
                    setTimeout(() => {
                        pagination.nextPage();
                    }, 2000);
                    return;
                }
            } else if (status !== google.maps.places.PlacesServiceStatus.ZERO_RESULTS) {
                console.log('Google Places search status:', status);
            }

            // No more pages or zero results – fetch accessibility info and filter
            async function processResults() {
                const locations = allResults.map(place => ({
                    id: 'places_' + place.place_id,
                    name: place.name,
                    category_name: categoryName || place.types?.[0] || 'Place',
                    latitude: place.geometry.location.lat(),
                    longitude: place.geometry.location.lng(),
                    address: place.formatted_address,
                    rating: place.rating,
                    user_ratings_total: place.user_ratings_total,
                    place_id: place.place_id,
                    is_google_place: true,
                    // keep full types array for icon/category detection
                    types: place.types || []
                }));

                // Fetch accessibility info for all places
                if (placesService && locations.length > 0) {
                    const batchSize = 5;
                    for (let i = 0; i < locations.length; i += batchSize) {
                        const batch = locations.slice(i, i + batchSize);
                        await Promise.all(batch.map(location => fetchAccessibilityForPlaceHome(location)));
                        // Small delay between batches
                        if (i + batchSize < locations.length) {
                            await new Promise(resolve => setTimeout(resolve, 500));
                        }
                    }
                }

                // Filter out places that are explicitly restricted (wheelchairAccessibleEntrance === false)
                // Show all places that are accessible (true) or have no restriction info (undefined/null)
                const accessibleLocations = locations.filter(location => {
                    const accessibilityOptions = location.accessibilityOptions;
                    
                    // If no accessibility info is available, include the place (no restriction = show)
                    if (!accessibilityOptions) {
                        return true;
                    }
                    
                    // Only filter out if explicitly marked as NOT accessible (false)
                    // Show if true (accessible) or undefined/null (no restriction info)
                    const isRestricted = accessibilityOptions.wheelchairAccessibleEntrance === false;
                    
                    return !isRestricted; // Show if not restricted
                });

                console.log('Google Places total combined results:', locations.length);
                console.log('Accessible places after filtering:', accessibleLocations.length);
                resolve(accessibleLocations);
            }
            
            processResults();
        };

        // Bias search to current map area (center + radius)
        const request = {
            query: query,
            location: map ? map.getCenter() : undefined,
            radius: 3000 // 3km radius around map center
        };

        placesSearchService.textSearch(request, handlePage);
    });
}

// Fetch accessibility info for a single place (for home page)
function fetchAccessibilityForPlaceHome(locationObject) {
    return new Promise((resolve) => {
        if (!placesService || !locationObject.place_id) {
            resolve();
            return;
        }
        
        // Note: accessibilityOptions field is not supported in all Places API versions
        // Request basic fields and check if accessibilityOptions exists in response
        const request = {
            placeId: locationObject.place_id,
            fields: ['name', 'formatted_address']
        };
        
        placesService.getDetails(request, (place, status) => {
            if (status === google.maps.places.PlacesServiceStatus.OK && place) {
                // Check if accessibilityOptions exists (might not be available)
                const accessibilityOptions = place.accessibilityOptions || null;
                // Attach to location object for filtering
                locationObject.accessibilityOptions = accessibilityOptions;
            } else {
                // If error or no accessibility info available, mark as null (will be included by default)
                locationObject.accessibilityOptions = null;
            }
            resolve();
        });
    });
}

// Helper: determine marker icon by category / types
function getMarkerIcon(location) {
    const types = Array.isArray(location.types) ? location.types : [];
    const cat = (location.category_name || '').toLowerCase();

    const hasType = (t) => types.includes(t);
    const catIncludes = (needle) => cat.includes(needle);

    // Hotels / lodging
    if (catIncludes('hotel') || catIncludes('resort') || hasType('lodging')) {
        return {
            url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        };
    }

    // Restaurants / food / cafes
    if (catIncludes('restaurant') || catIncludes('food') || catIncludes('cafe') ||
        hasType('restaurant') || hasType('cafe') || hasType('food')) {
        return {
            url: 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        };
    }

    // Education: school, college, university
    if (catIncludes('school') || catIncludes('college') || catIncludes('university') ||
        catIncludes('academy') || hasType('school') || hasType('university')) {
        return {
            url: 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        };
    }

    // Parks / outdoor
    if (catIncludes('park') || hasType('park')) {
        return {
            url: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        };
    }

    // Shopping / stores
    if (catIncludes('mall') || catIncludes('market') || catIncludes('shop') ||
        hasType('shopping_mall') || hasType('store')) {
        return {
            url: 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        };
    }

    // Health / hospitals
    if (catIncludes('hospital') || catIncludes('clinic') || hasType('hospital')) {
        return {
            url: 'http://maps.google.com/mapfiles/ms/icons/hospitals.png',
            scaledSize: new google.maps.Size(32, 32)
        };
    }

    // Fallback for Google Places
    if (location.is_google_place) {
        return {
            url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
            scaledSize: new google.maps.Size(32, 32)
        };
    }

    // Default (use Google default pin)
    return null;
}

// Helper: small emoji for category in list
function getCategoryEmoji(location) {
    const types = Array.isArray(location.types) ? location.types : [];
    const cat = (location.category_name || '').toLowerCase();

    const hasType = (t) => types.includes(t);
    const catIncludes = (needle) => cat.includes(needle);

    if (catIncludes('hotel') || catIncludes('resort') || hasType('lodging')) return '🏨';
    if (catIncludes('restaurant') || catIncludes('food') || catIncludes('cafe') ||
        hasType('restaurant') || hasType('cafe')) return '🍽';
    if (catIncludes('school') || catIncludes('college') || catIncludes('university') ||
        catIncludes('academy') || hasType('school') || hasType('university')) return '🎓';
    if (catIncludes('park') || hasType('park')) return '🌳';
    if (catIncludes('mall') || catIncludes('market') || catIncludes('shop') ||
        hasType('shopping_mall') || hasType('store')) return '🛍';
    if (catIncludes('hospital') || catIncludes('clinic') || hasType('hospital')) return '🏥';

    return '📍';
}

