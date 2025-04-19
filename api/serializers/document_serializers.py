from rest_framework import serializers
from accounts.authentication import User
from accounts.models import User
from documents.models import Document, DocumentCategory

class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'description']

class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=DocumentCategory.objects.all())
    authorized_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'category', 'description', 'uploaded_by',
            'created_at', 'updated_at', 'visibility', 'authorized_users'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = DocumentCategorySerializer(instance.category).data
        # Don't expose authorized users to everyone
        if 'authorized_users' in representation:
            representation.pop('authorized_users')
        return representation