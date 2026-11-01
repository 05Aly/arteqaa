from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment
from courses.models import Course, Enrollment
from rest_framework import serializers

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        course_id = request.data.get('course_id')
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        # Mock creating a payment
        payment = Payment.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            status='COMPLETED', # Automatically complete in mock
            transaction_id='MOCK_TXN_' + str(Payment.objects.count() + 1)
        )

        # Create enrollment upon successful payment
        Enrollment.objects.get_or_create(student=request.user, course=course)

        return Response({
            'message': 'Payment successful and enrolled',
            'payment_id': payment.id,
            'transaction_id': payment.transaction_id
        })
