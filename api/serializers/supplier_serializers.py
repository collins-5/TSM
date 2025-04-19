from rest_framework import serializers
from api.serializers.user_serializers import UserSerializer
from suppliers.models import SupplierProfile, SupplierCategory, SupplierRating, SupplierDocument

class SupplierCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierCategory
        fields = ['id', 'name', 'description']

class SupplierDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierDocument
        fields = ['id', 'supplier', 'document', 'title', 'description', 'uploaded_at']

class SupplierRatingSerializer(serializers.ModelSerializer):
    rated_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = SupplierRating
        fields = [
            'id', 'supplier', 'rating', 'review', 'rated_by', 'rated_at'
        ]
        read_only_fields = ['rated_by', 'rated_at']

class SupplierProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=SupplierCategory.objects.all(), many=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = SupplierProfile
        fields = [
            'id', 'user', 'company_name', 'description', 'website',
            'address', 'category', 'verification_status', 'average_rating'
        ]
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return None
        return sum(rating.rating for rating in ratings) / len(ratings)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = SupplierCategorySerializer(instance.category, many=True).data
        return representation