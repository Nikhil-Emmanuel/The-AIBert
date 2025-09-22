"""
AIML Manager for handling AIML brain operations
"""

import aiml
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AIMLManager:
    def __init__(self):
        self.kernel = aiml.Kernel()
        self.brain_file = "ai_backend/aiml_data/brain.brn"
        self.aiml_files_dir = "ai_backend/aiml_data/aiml_files"
        self.loaded = False
        
    def load_brain(self):
        """Load AIML brain from file or create new one"""
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(self.brain_file), exist_ok=True)
            os.makedirs(self.aiml_files_dir, exist_ok=True)
            
            # Try to load existing brain
            if os.path.exists(self.brain_file):
                logger.info("Loading existing AIML brain...")
                self.kernel.bootstrap(brainFile=self.brain_file)
            else:
                logger.info("Creating new AIML brain...")
                self._create_initial_brain()
                
            self.loaded = True
            logger.info("AIML brain loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading AIML brain: {str(e)}")
            self.loaded = False
            
    def _create_initial_brain(self):
        """Create initial AIML brain with basic patterns"""
        try:
            # Load all AIML files
            aiml_files = list(Path(self.aiml_files_dir).glob("*.aiml"))
            
            if not aiml_files:
                # Create basic AIML file if none exist
                self._create_basic_aiml_files()
                aiml_files = list(Path(self.aiml_files_dir).glob("*.aiml"))
            
            # Learn from AIML files
            for aiml_file in aiml_files:
                logger.info(f"Learning from {aiml_file}")
                self.kernel.learn(str(aiml_file))
            
            # Save brain
            self.kernel.saveBrain(self.brain_file)
            logger.info("AIML brain created and saved")
            
        except Exception as e:
            logger.error(f"Error creating AIML brain: {str(e)}")
            raise
            
    def _create_basic_aiml_files(self):
        """Create basic AIML files for educational assistant"""
        
        # Basic greetings and responses
        basic_aiml = '''<?xml version="1.0" encoding="UTF-8"?>
<aiml version="1.0">

<category>
    <pattern>HELLO</pattern>
    <template>Hello! I'm AIBert, your educational AI assistant. How can I help you today?</template>
</category>

<category>
    <pattern>HI</pattern>
    <template>Hi there! I'm here to help with your educational needs. What would you like to learn about?</template>
</category>

<category>
    <pattern>HOW ARE YOU</pattern>
    <template>I'm doing great! Ready to help you learn and explore new topics. What can I assist you with?</template>
</category>

<category>
    <pattern>WHAT IS YOUR NAME</pattern>
    <template>I'm AIBert, an AI-powered educational assistant designed to help teachers and students.</template>
</category>

<category>
    <pattern>HELP</pattern>
    <template>I can help you with:
    - Generating educational quizzes
    - Explaining complex topics
    - Creating lesson plans
    - Grading and feedback
    - Educational content creation
    What specific help do you need?</template>
</category>

<category>
    <pattern>BYE</pattern>
    <template>Goodbye! Feel free to come back anytime you need educational assistance.</template>
</category>

<category>
    <pattern>GOODBYE</pattern>
    <template>Goodbye! Have a great day learning and teaching!</template>
</category>

</aiml>'''

        # Educational queries
        educational_aiml = '''<?xml version="1.0" encoding="UTF-8"?>
<aiml version="1.0">

<category>
    <pattern>EXPLAIN *</pattern>
    <template>I'd be happy to explain <star/>. Let me provide you with a comprehensive explanation of this topic.</template>
</category>

<category>
    <pattern>WHAT IS *</pattern>
    <template>Let me explain what <star/> is. This is an important concept that I can break down for you.</template>
</category>

<category>
    <pattern>CREATE QUIZ ABOUT *</pattern>
    <template>I'll create a quiz about <star/>. Let me generate some relevant questions for this topic.</template>
</category>

<category>
    <pattern>GENERATE QUESTIONS ON *</pattern>
    <template>I'll generate educational questions on <star/>. These will be suitable for testing knowledge on this subject.</template>
</category>

<category>
    <pattern>HELP ME UNDERSTAND *</pattern>
    <template>I'll help you understand <star/>. Let me break this down into simpler concepts for better comprehension.</template>
</category>

<category>
    <pattern>TEACH ME *</pattern>
    <template>I'd love to teach you about <star/>! Let's start with the fundamentals and build up your understanding.</template>
</category>

</aiml>'''

        # Save AIML files
        with open(f"{self.aiml_files_dir}/basic.aiml", "w", encoding="utf-8") as f:
            f.write(basic_aiml)
            
        with open(f"{self.aiml_files_dir}/educational.aiml", "w", encoding="utf-8") as f:
            f.write(educational_aiml)
            
        logger.info("Basic AIML files created")
        
    def respond(self, message, user_id="default"):
        """Get response from AIML brain"""
        try:
            if not self.loaded:
                return "I'm sorry, my brain is not loaded yet. Please try again later."
                
            # Set user session
            self.kernel.setPredicate("name", user_id)
            
            # Get response
            response = self.kernel.respond(message.upper())
            
            if not response:
                response = "I'm not sure how to respond to that. Can you rephrase your question?"
                
            return response
            
        except Exception as e:
            logger.error(f"Error getting AIML response: {str(e)}")
            return "I encountered an error processing your message. Please try again."
            
    def reload_brain(self):
        """Reload AIML brain"""
        try:
            self.kernel = aiml.Kernel()
            self.load_brain()
            logger.info("AIML brain reloaded successfully")
            
        except Exception as e:
            logger.error(f"Error reloading AIML brain: {str(e)}")
            raise
            
    def is_loaded(self):
        """Check if AIML brain is loaded"""
        return self.loaded
        
    def add_pattern(self, pattern, template, category_name=None):
        """Add new AIML pattern dynamically"""
        try:
            # This would require extending AIML functionality
            # For now, we'll log the request
            logger.info(f"Request to add pattern: {pattern} -> {template}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding AIML pattern: {str(e)}")
            return False
