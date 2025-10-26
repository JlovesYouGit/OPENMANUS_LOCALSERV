"""
Enhanced Attention Mechanism for OpenManus
This module implements improved attention mechanisms to better interpret user responses
and eliminate irrelevant token generation.
"""

import re
from typing import List, Dict, Any, Tuple
from collections import Counter

class EnhancedAttentionMechanism:
    """Enhanced attention mechanism for better context understanding"""
    
    def __init__(self):
        # Common question patterns to identify user intent
        self.question_patterns = [
            (r'\b(what|how|why|when|where|who|which)\b', 'informational'),
            (r'\b(calculate|compute|solve|find)\b', 'computational'),
            (r'\b(create|make|build|develop)\b', 'creative'),
            (r'\b(compare|contrast|difference)\b', 'comparison'),
            (r'\b(explain|describe|tell me about)\b', 'explanatory'),
            (r'\b(help|assist|support)\b', 'assistance'),
        ]
        
        # Irrelevant token patterns to filter out (reduced for more natural responses)
        self.irrelevant_patterns = [
            r'\b(um|uh|like|you know|basically|actually|literally)\b',
            r'[^\w\s]{3,}',  # Multiple punctuation marks (increased threshold)
            r'\s{5,}',  # Multiple spaces (increased threshold)
        ]
        
    def identify_user_intent(self, user_input: str) -> str:
        """Identify the user's intent from their input"""
        user_input_lower = user_input.lower()
        
        # Check for question patterns
        for pattern, intent_type in self.question_patterns:
            if re.search(pattern, user_input_lower):
                return intent_type
                
        # Default to conversational if no specific pattern is found
        return "conversational"
    
    def extract_key_entities(self, text: str) -> List[str]:
        """Extract key entities from text"""
        # Simple entity extraction (in a real implementation, this would use NER)
        # Extract capitalized words (likely proper nouns)
        words = text.split()
        entities = []
        
        for i, word in enumerate(words):
            # Remove punctuation
            clean_word = re.sub(r'[^\w]', '', word)
            # Check if it's capitalized and not at the beginning of a sentence
            if (len(clean_word) > 2 and 
                clean_word[0].isupper() and 
                (i > 0 or clean_word.lower() not in ['i', 'i\'m', 'i\'ll', 'i\'ve'])):
                entities.append(clean_word)
                
        return entities
    
    def filter_irrelevant_content(self, text: str) -> str:
        """Filter out irrelevant content and filler words"""
        # Remove irrelevant patterns
        for pattern in self.irrelevant_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_user_preferences(self, history: List[Dict[str, Any]]) -> List[str]:
        """Extract user preferences from conversation history"""
        preferences = []
        
        # Look for preference indicators in user messages
        preference_indicators = [
            'prefer', 'like', 'want', 'need', 'please', 'i want', 'i prefer',
            'i like', 'i need', 'i would like', 'could you', 'can you'
        ]
        
        # Check recent user messages for preferences
        user_messages = [msg for msg in history[-6:] if msg.get('isUser', False)]
        
        for msg in user_messages:
            content = msg.get('content', '').lower()
            for indicator in preference_indicators:
                if indicator in content:
                    # Extract the preference (simplified approach)
                    words = content.split()
                    indicator_index = content.find(indicator)
                    if indicator_index != -1:
                        # Get words after the indicator
                        start_word = len(content[:indicator_index].split())
                        preference_phrase = ' '.join(words[start_word:start_word+5])  # Get next 5 words
                        if preference_phrase not in preferences:
                            preferences.append(preference_phrase)
        
        return preferences[:3]  # Return top 3 preferences
    
    def generate_context_prompt(self, user_input: str, history: List[Dict[str, Any]]) -> str:
        """Generate an enhanced context prompt based on user input and history"""
        intent = self.identify_user_intent(user_input)
        entities = self.extract_key_entities(user_input)
        
        # Build context based on intent
        context_parts = []
        
        if intent == "informational":
            context_parts.append("Provide a clear and concise answer to the question.")
        elif intent == "computational":
            context_parts.append("Perform the requested calculation or solve the problem step by step.")
        elif intent == "creative":
            context_parts.append("Be creative and provide innovative ideas or solutions.")
        elif intent == "comparison":
            context_parts.append("Compare the requested items and highlight key differences and similarities.")
        elif intent == "explanatory":
            context_parts.append("Provide a detailed explanation in an easy-to-understand manner.")
        elif intent == "assistance":
            context_parts.append("Offer helpful assistance and guidance.")
        else:
            context_parts.append("Engage in a natural conversation while being helpful and informative.")
        
        # Add entity context if entities were found
        if entities:
            context_parts.append(f"Key topics mentioned: {', '.join(entities)}")
        
        # Add recent history context with importance weighting
        if history:
            # Take more history items for better context
            recent_history = history[-8:]  # Last 4 user-agent exchanges
            
            # Include importance information if available
            history_lines = []
            for msg in recent_history:
                role = 'User' if msg.get('isUser') else 'Assistant'
                content = msg.get('content', '')
                importance = msg.get('importance', 0.5)  # Default importance
                
                # For high importance messages, add emphasis
                if importance > 0.7:
                    history_lines.append(f"{role} (important): {content}")
                else:
                    history_lines.append(f"{role}: {content}")
            
            history_text = "\n".join(history_lines)
            context_parts.append(f"Recent conversation context:\n{history_text}")
            
            # Add user preferences if detectable from history
            user_preferences = self._extract_user_preferences(history)
            if user_preferences:
                context_parts.append(f"User preferences detected: {', '.join(user_preferences)}")
        
        return "\n".join(context_parts)
    
    def optimize_attention_weights(self, user_input: str, response: str) -> Dict[str, float]:
        """Optimize attention weights to focus on relevant parts"""
        # Simple attention weight calculation based on content overlap
        user_words = set(re.findall(r'\b\w+\b', user_input.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        # Calculate relevance score
        if user_words:
            relevance_score = len(user_words.intersection(response_words)) / len(user_words)
        else:
            relevance_score = 0.5
            
        # Calculate coherence (based on sentence structure)
        sentences = re.split(r'[.!?]+', response)
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        coherence_score = min(avg_sentence_length / 20.0, 1.0)  # Normalize to 0-1
        
        return {
            "relevance": relevance_score,
            "coherence": coherence_score,
            "overall": (relevance_score + coherence_score) / 2.0
        }
    
    def refine_response(self, response: str, user_input: str) -> str:
        """Refine response to eliminate irrelevant content"""
        # Filter out irrelevant content
        refined_response = self.filter_irrelevant_content(response)
        
        # Ensure response addresses the user's question
        user_words = set(re.findall(r'\b\w+\b', user_input.lower()))
        response_words = set(re.findall(r'\b\w+\b', refined_response.lower()))
        
        # Only add clarification if response is very short or empty
        if len(refined_response.strip()) < 10 and not user_words.intersection(response_words) and len(user_words) > 0:
            key_terms = list(user_words)[:3]  # Take first 3 terms
            refined_response = f"Regarding {' and '.join(key_terms)}: {refined_response}"
            
        return refined_response.strip()

# Global instance
attention_mechanism = EnhancedAttentionMechanism()

def identify_user_intent(user_input: str) -> str:
    """Identify user intent from input"""
    return attention_mechanism.identify_user_intent(user_input)

def generate_enhanced_context(user_input: str, history: List[Dict[str, Any]]) -> str:
    """Generate enhanced context for the model"""
    return attention_mechanism.generate_context_prompt(user_input, history)

def refine_model_response(response: str, user_input: str) -> str:
    """Refine model response to improve quality"""
    return attention_mechanism.refine_response(response, user_input)

def evaluate_response_quality(response: str, user_input: str) -> Dict[str, float]:
    """Evaluate the quality of a response"""
    return attention_mechanism.optimize_attention_weights(user_input, response)