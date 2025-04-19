from rest_framework import serializers
from contracts.models import Contract, ContractDocument, ContractStatus

class ContractStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractStatus
        fields = ['id', 'name', 'description']

class ContractDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractDocument
        fields = ['id', 'contract', 'document', 'title', 'description', 'uploaded_at']

class ContractSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    status = serializers.PrimaryKeyRelatedField(queryset=ContractStatus.objects.all())
    
    class Meta:
        model = Contract
        fields = [
            'id', 'tender', 'supplier', 'title', 'description', 'start_date',
            'end_date', 'value', 'created_by', 'created_at', 'updated_at', 'status'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['status'] = ContractStatusSerializer(instance.status).data
        return representation