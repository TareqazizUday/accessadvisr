from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from .models import AboutPost, AboutComment, AboutCommentReply


@method_decorator(csrf_exempt, name='dispatch')
class SubmitAboutCommentView(APIView):
    parser_classes = [JSONParser]
    """API endpoint to submit a comment on an about post"""
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else {}
            
            about_post_id = data.get('about_post_id')
            author_name = data.get('author_name', '').strip()
            author_email = data.get('author_email', '').strip()
            comment_text = data.get('comment_text', '').strip()
            save_info = data.get('save_info', False)
            
            if not about_post_id:
                return Response(
                    {'error': 'About Post ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_name:
                return Response(
                    {'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_email:
                return Response(
                    {'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not comment_text:
                return Response(
                    {'error': 'Comment text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                about_post = AboutPost.objects.get(id=about_post_id, status='published')
            except AboutPost.DoesNotExist:
                return Response(
                    {'error': 'About post not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create comment (auto-approved)
            comment = AboutComment.objects.create(
                about_post=about_post,
                author_name=author_name,
                author_email=author_email,
                comment_text=comment_text,
                save_info=save_info,
                is_approved=True,  # Auto-approved
                is_active=True
            )
            
            return Response({
                'success': True,
                'message': 'Comment submitted successfully!',
                'comment_id': comment.id
            }, status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class SubmitAboutCommentReplyView(APIView):
    parser_classes = [JSONParser]
    """API endpoint to submit a reply to an about post comment"""
    
    def post(self, request):
        try:
            data = request.data if hasattr(request, 'data') else {}
            
            comment_id = data.get('comment_id')
            parent_reply_id = data.get('parent_reply_id')
            author_name = data.get('author_name', '').strip()
            author_email = data.get('author_email', '').strip()
            reply_text = data.get('reply_text', '').strip()
            
            if not comment_id:
                return Response(
                    {'error': 'Comment ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_name:
                return Response(
                    {'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_email:
                return Response(
                    {'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not reply_text:
                return Response(
                    {'error': 'Reply text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                comment = AboutComment.objects.get(id=comment_id, is_active=True)
            except AboutComment.DoesNotExist:
                return Response(
                    {'error': 'Comment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            parent_reply = None
            if parent_reply_id:
                try:
                    parent_reply = AboutCommentReply.objects.get(id=parent_reply_id, is_active=True, comment=comment)
                except AboutCommentReply.DoesNotExist:
                    return Response(
                        {'error': 'Parent reply not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            reply = AboutCommentReply.objects.create(
                comment=comment,
                parent_reply=parent_reply,
                author_name=author_name,
                author_email=author_email,
                reply_text=reply_text,
                is_approved=True,  # Auto-approve replies
                is_active=True
            )
            
            return Response({
                'success': True,
                'message': 'Reply submitted successfully!',
                'reply_id': reply.id
            }, status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

