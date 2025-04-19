from rest_framework import serializers
from tenders.models import Tender, TenderCategory, TenderStage, TenderDocument

class TenderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderCategory
        fields = ['id', 'name', 'description']

class TenderStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderStage
        fields = ['id', 'name', 'description', 'order']

class TenderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderDocument
        fields = ['id', 'tender', 'document', 'title', 'description', 'uploaded_at']

class TenderSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=TenderCategory.objects.all())
    stage = serializers.PrimaryKeyRelatedField(queryset=TenderStage.objects.all())
    
    class Meta:
        model = Tender
        fields = [
            'id', 'title', 'description', 'category', 'budget', 'deadline',
            'created_by', 'created_at', 'updated_at', 'stage', 'requirements'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = TenderCategorySerializer(instance.category).data
        representation['stage'] = TenderStageSerializer(instance.stage).data
        return representation
