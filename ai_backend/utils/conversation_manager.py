"""
Conversation Manager for maintaining context and session management
"""

import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation context and user sessions"""
    
    def __init__(self, max_context_length=10, session_timeout_hours=24):
        self.conversations = defaultdict(list)
        self.user_sessions = {}
        self.max_context_length = max_context_length
        self.session_timeout = timedelta(hours=session_timeout_hours)
        
    def add_message(self, user_id, message, response, message_type='chat'):
        """Add a message to conversation history"""
        try:
            timestamp = datetime.now()
            
            conversation_entry = {
                'timestamp': timestamp.isoformat(),
                'user_message': message,
                'bot_response': response,
                'message_type': message_type,
                'session_id': self._get_or_create_session(user_id)
            }
            
            self.conversations[user_id].append(conversation_entry)
            
            # Maintain context length limit
            if len(self.conversations[user_id]) > self.max_context_length:
                self.conversations[user_id] = self.conversations[user_id][-self.max_context_length:]
                
            logger.info(f"Added message to conversation for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")
            
    def get_context(self, user_id, num_messages=5):
        """Get recent conversation context for a user"""
        try:
            if user_id not in self.conversations:
                return []
                
            recent_messages = self.conversations[user_id][-num_messages:]
            return recent_messages
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return []
            
    def get_conversation_summary(self, user_id):
        """Get a summary of the conversation"""
        try:
            if user_id not in self.conversations:
                return {
                    'total_messages': 0,
                    'session_id': None,
                    'last_activity': None
                }
                
            conversation = self.conversations[user_id]
            
            return {
                'total_messages': len(conversation),
                'session_id': conversation[-1]['session_id'] if conversation else None,
                'last_activity': conversation[-1]['timestamp'] if conversation else None,
                'message_types': self._count_message_types(conversation)
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return {'error': str(e)}
            
    def clear_conversation(self, user_id):
        """Clear conversation history for a user"""
        try:
            if user_id in self.conversations:
                del self.conversations[user_id]
                
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
                
            logger.info(f"Cleared conversation for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
            return False
            
    def _get_or_create_session(self, user_id):
        """Get existing session or create new one"""
        try:
            current_time = datetime.now()
            
            # Check if user has an active session
            if user_id in self.user_sessions:
                session_data = self.user_sessions[user_id]
                last_activity = datetime.fromisoformat(session_data['last_activity'])
                
                # Check if session is still valid
                if current_time - last_activity < self.session_timeout:
                    # Update last activity
                    session_data['last_activity'] = current_time.isoformat()
                    return session_data['session_id']
                    
            # Create new session
            session_id = str(uuid.uuid4())
            self.user_sessions[user_id] = {
                'session_id': session_id,
                'created_at': current_time.isoformat(),
                'last_activity': current_time.isoformat()
            }
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error managing session: {str(e)}")
            return str(uuid.uuid4())
            
    def _count_message_types(self, conversation):
        """Count different types of messages in conversation"""
        type_counts = defaultdict(int)
        for entry in conversation:
            type_counts[entry.get('message_type', 'chat')] += 1
        return dict(type_counts)
        
    def get_active_sessions(self):
        """Get all active sessions"""
        try:
            current_time = datetime.now()
            active_sessions = {}
            
            for user_id, session_data in self.user_sessions.items():
                last_activity = datetime.fromisoformat(session_data['last_activity'])
                
                if current_time - last_activity < self.session_timeout:
                    active_sessions[user_id] = session_data
                    
            return active_sessions
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return {}
            
    def cleanup_expired_sessions(self):
        """Remove expired sessions and conversations"""
        try:
            current_time = datetime.now()
            expired_users = []
            
            for user_id, session_data in self.user_sessions.items():
                last_activity = datetime.fromisoformat(session_data['last_activity'])
                
                if current_time - last_activity >= self.session_timeout:
                    expired_users.append(user_id)
                    
            # Remove expired sessions
            for user_id in expired_users:
                del self.user_sessions[user_id]
                if user_id in self.conversations:
                    del self.conversations[user_id]
                    
            logger.info(f"Cleaned up {len(expired_users)} expired sessions")
            return len(expired_users)
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            return 0
            
    def export_conversation(self, user_id):
        """Export conversation history for a user"""
        try:
            if user_id not in self.conversations:
                return None
                
            conversation_data = {
                'user_id': user_id,
                'conversation': self.conversations[user_id],
                'session_info': self.user_sessions.get(user_id, {}),
                'exported_at': datetime.now().isoformat()
            }
            
            return conversation_data
            
        except Exception as e:
            logger.error(f"Error exporting conversation: {str(e)}")
            return None
            
    def import_conversation(self, conversation_data):
        """Import conversation history"""
        try:
            user_id = conversation_data['user_id']
            self.conversations[user_id] = conversation_data['conversation']
            
            if 'session_info' in conversation_data:
                self.user_sessions[user_id] = conversation_data['session_info']
                
            logger.info(f"Imported conversation for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing conversation: {str(e)}")
            return False
            
    def get_statistics(self):
        """Get conversation statistics"""
        try:
            total_users = len(self.conversations)
            total_messages = sum(len(conv) for conv in self.conversations.values())
            active_sessions = len(self.get_active_sessions())
            
            # Message type distribution
            all_message_types = defaultdict(int)
            for conversation in self.conversations.values():
                type_counts = self._count_message_types(conversation)
                for msg_type, count in type_counts.items():
                    all_message_types[msg_type] += count
                    
            return {
                'total_users': total_users,
                'total_messages': total_messages,
                'active_sessions': active_sessions,
                'message_type_distribution': dict(all_message_types),
                'average_messages_per_user': total_messages / max(1, total_users)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {'error': str(e)}
