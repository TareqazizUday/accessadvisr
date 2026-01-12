from rest_framework import serializers
from .models import Location, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']


class LocationSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'category', 'category_id',
            'latitude', 'longitude', 'keywords',
            'status', 'created_at', 'updated_at', 'distance'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_distance(self, obj):
        """Calculate distance if lat/lng provided in context"""
        request = self.context.get('request')
        if request and hasattr(request, 'query_params'):
            lat = request.query_params.get('lat')
            lng = request.query_params.get('lng')
            if lat and lng:
                from .utils import haversine_distance
                try:
                    return round(haversine_distance(
                        float(lat), float(lng),
                        float(obj.latitude), float(obj.longitude)
                    ), 2)
                except (ValueError, TypeError):
                    pass
        return None


class LocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    distance = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = [
            'id', 'name', 'category_name',
            'latitude', 'longitude', 'distance'
        ]
    
    def get_distance(self, obj):
        """Calculate distance if lat/lng provided in context"""
        request = self.context.get('request')
        if request and hasattr(request, 'query_params'):
            lat = request.query_params.get('lat')
            lng = request.query_params.get('lng')
            if lat and lng:
                from .utils import haversine_distance
                try:
                    return round(haversine_distance(
                        float(lat), float(lng),
                        float(obj.latitude), float(obj.longitude)
                    ), 2)
                except (ValueError, TypeError):
                    pass
        return None


