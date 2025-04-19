from rest_framework import serializers
from bidding.models import Bid, BidDocument, BidEvaluation

class BidDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BidDocument
        fields = ['id', 'bid', 'document', 'title', 'description', 'uploaded_at']

class BidEvaluationSerializer(serializers.ModelSerializer):
    evaluated_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = BidEvaluation
        fields = [
            'id', 'bid', 'technical_score', 'financial_score', 'total_score',
            'comments', 'evaluated_by', 'evaluated_at'
        ]
        read_only_fields = ['evaluated_by', 'evaluated_at']

class BidSerializer(serializers.ModelSerializer):
    supplier = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Bid
        fields = [
            'id', 'tender', 'supplier', 'bid_amount', 'technical_description',
            'delivery_timeframe', 'created_at', 'updated_at', 'status'
        ]
        read_only_fields = ['created_at', 'updated_at']