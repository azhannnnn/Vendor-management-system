from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Vendor, PurchaseOrder
from .serializers import VendorSerializer, PurchaseOrderSerializer

class VendorListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class VendorRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class PurchaseOrderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class VendorPerformanceView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'on_time_delivery_rate': serializer.data['on_time_delivery_rate'],
            'quality_rating_avg': serializer.data['quality_rating_avg'],
            'average_response_time': serializer.data['average_response_time'],
            'fulfillment_rate': serializer.data['fulfillment_rate']
        })

class AcknowledgePurchaseOrderView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.acknowledgment_date = request.data.get('acknowledgment_date') 
        instance.save()
        response_times = PurchaseOrder.objects.filter(
            vendor=instance.vendor, 
            acknowledgment_date__isnull=False
        ).values_list('acknowledgment_date', 'issue_date')
        total_seconds = sum(
            abs((ack_date - issue_date).total_seconds()) 
            for ack_date, issue_date in response_times
        )
        average_response_time = total_seconds / len(response_times) if response_times else 0
        instance.vendor.average_response_time = average_response_time
        instance.vendor.save()
        return Response({'acknowledgment_date': instance.acknowledgment_date})
