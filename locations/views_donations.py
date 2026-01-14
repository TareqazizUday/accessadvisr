from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import json
from .models import Donation, DonationCampaign


@method_decorator(csrf_exempt, name='dispatch')
class SubmitDonationView(APIView):
    """API endpoint to submit a donation"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            name = data.get('name', '').strip()
            phone = data.get('phone', '').strip()
            donation_amount = data.get('donation_amount', '').strip()
            payment_method = data.get('payment_method', '').strip()
            consent_given = data.get('consent_given', False)
            campaign_id = data.get('campaign_id')
            
            # Validation
            if not name:
                return Response(
                    {'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not phone:
                return Response(
                    {'error': 'Phone is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not donation_amount:
                return Response(
                    {'error': 'Donation amount is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if donation_amount not in ['5', '10', 'other']:
                return Response(
                    {'error': 'Invalid donation amount option'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if donation_amount == 'other':
                custom_amount = data.get('custom_amount')
                if not custom_amount or float(custom_amount) <= 0:
                    return Response(
                        {'error': 'Custom amount is required and must be greater than 0'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if not payment_method or payment_method not in ['stripe', 'paypal']:
                return Response(
                    {'error': 'Payment method is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not consent_given:
                return Response(
                    {'error': 'Consent is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get campaign if provided
            campaign = None
            if campaign_id:
                try:
                    campaign = DonationCampaign.objects.get(id=campaign_id, is_active=True)
                except DonationCampaign.DoesNotExist:
                    pass
            
            # Create donation record
            donation = Donation.objects.create(
                campaign=campaign,
                name=name,
                email=data.get('email', '').strip(),
                phone=phone,
                street_address=data.get('street_address', '').strip(),
                apartment_suite=data.get('apartment_suite', '').strip(),
                city=data.get('city', '').strip(),
                state_province=data.get('state_province', '').strip(),
                zip_postal_code=data.get('zip_postal_code', '').strip(),
                country=data.get('country', '').strip(),
                donation_amount=donation_amount,
                custom_amount=data.get('custom_amount') if donation_amount == 'other' else None,
                payment_method=payment_method,
                consent_given=consent_given,
                status='pending'
            )
            
            # Update campaign raised amount if campaign exists
            if campaign:
                campaign.raised_amount += donation.get_final_amount()
                campaign.save()
            
            return Response({
                'success': True,
                'message': 'Donation submitted successfully',
                'donation_id': donation.id,
                'amount': float(donation.get_final_amount()),
                'payment_method': payment_method,
                'next_step': f'Redirect to {payment_method} payment page'
            }, status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                {'error': f'Invalid amount: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

