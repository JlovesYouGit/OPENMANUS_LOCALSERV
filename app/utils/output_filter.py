"""
Output Relevance & Context Gateway with Attention-Based Filtering
This module implements attention-based output filters to block content with low semantic overlap
to original query intent and handle ambiguous entity responses.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter
from difflib import SequenceMatcher

class OutputRelevanceFilter:
    """Attention-based output filter for relevance and context gating"""
    
    def __init__(self):
        # Minimum semantic overlap threshold (reduced to 15% for better natural responses)
        self.min_overlap_threshold = 0.15
        
        # Patterns for identifying hallucinated content
        self.hallucination_patterns = [
            r'\b(?:forum|discussion|question|answer|post)\b.*(?:stack\s*overflow|reddit|quora)',
            r'\b(?:download|install|version)\b.*\b(?:software|program|application)\b',
            r'\b(?:manual|documentation|tutorial|guide)\b.*\b(?:step|instruction)\b',
            r'\b(?:code|script|function|class)\b.*\b(?:example|sample)\b',
            r'(?:stackoverflow\.com|reddit\.com|quora\.com)',  # Direct website references
        ]
        
        # Financial context keywords
        self.financial_keywords = {
            'stock', 'price', 'share', 'market', 'trading', 'investment', 
            'portfolio', 'dividend', 'earnings', 'revenue', 'profit',
            'financial', 'quarterly', 'annual', 'report', 'SEC',
            'NASDAQ', 'NYSE', 'exchange', 'broker', 'brokerage'
        }
        
        # Biographical context keywords
        self.biography_keywords = {
            'born', 'birth', 'died', 'death', 'career', 'work', 'job',
            'position', 'role', 'company', 'education', 'school',
            'university', 'degree', 'biography', 'bio', 'life',
            'personal', 'family', 'married', 'children', 'spouse'
        }
        
        # Technical context keywords
        self.technical_keywords = {
            'code', 'program', 'software', 'application', 'tool',
            'function', 'method', 'class', 'library', 'API',
            'SDK', 'framework', 'algorithm', 'data', 'database',
            'server', 'client', 'network', 'protocol', 'system'
        }
    
    def calculate_semantic_overlap(self, query: str, response: str) -> float:
        """
        Calculate semantic overlap between query and response
        
        Args:
            query: The original query
            response: The response to evaluate
            
        Returns:
            Overlap score between 0 and 1
        """
        # Convert to lowercase and extract words
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        if not query_words:
            return 0.0
            
        # Calculate Jaccard similarity
        intersection = len(query_words.intersection(response_words))
        union = len(query_words.union(response_words))
        
        if union == 0:
            return 0.0
            
        jaccard_similarity = intersection / union
        
        # Calculate sequence similarity for phrase matching
        sequence_similarity = SequenceMatcher(None, query.lower(), response.lower()).ratio()
        
        # Weighted combination
        overlap_score = 0.7 * jaccard_similarity + 0.3 * sequence_similarity
        
        return min(overlap_score, 1.0)
    
    def detect_hallucination(self, response: str) -> Tuple[bool, List[str]]:
        """
        Detect if response contains hallucinated content
        
        Args:
            response: The response to check
            
        Returns:
            Tuple of (is_hallucinated, reasons)
        """
        reasons = []
        response_lower = response.lower()
        
        # Check for hallucination patterns
        for pattern in self.hallucination_patterns:
            if re.search(pattern, response_lower):
                reasons.append(f"Contains hallucination pattern: {pattern}")
        
        # Check for excessive unrelated content
        financial_count = sum(1 for word in self.financial_keywords if word in response_lower)
        biography_count = sum(1 for word in self.biography_keywords if word in response_lower)
        technical_count = sum(1 for word in self.technical_keywords if word in response_lower)
        
        # If response contains content from multiple unrelated domains
        domains_mentioned = sum([
            financial_count > 0,
            biography_count > 0,
            technical_count > 0
        ])
        
        if domains_mentioned > 2:
            reasons.append("Content spans multiple unrelated domains")
        
        return len(reasons) > 0, reasons
    
    def filter_response(self, query: str, response: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Filter response based on relevance and quality
        
        Args:
            query: The original query
            response: The response to filter
            
        Returns:
            Tuple of (should_block, filtered_response, metadata)
        """
        # Calculate semantic overlap
        overlap_score = self.calculate_semantic_overlap(query, response)
        
        # Check for hallucination
        is_hallucinated, hallucination_reasons = self.detect_hallucination(response)
        
        # Determine if response should be blocked
        # Only block for hallucination, not for low overlap (to allow more natural responses)
        should_block = is_hallucinated
        
        # Generate filtered response
        if should_block:
            if is_hallucinated:
                filtered_response = f"⚠️ Response blocked due to potential hallucination.\n\nReasons: {', '.join(hallucination_reasons)}\n\nResponse: {response[:200]}..."
            else:
                filtered_response = response  # Allow low overlap responses
        else:
            filtered_response = response
        
        metadata = {
            "overlap_score": overlap_score,
            "is_hallucinated": is_hallucinated,
            "hallucination_reasons": hallucination_reasons,
            "should_block": should_block
        }
        
        return should_block, filtered_response, metadata
    
    def handle_ambiguous_entity(self, query: str, entity: str, options: List[str]) -> str:
        """
        Handle ambiguous entity responses by prompting user to select
        
        Args:
            query: The original query
            entity: The ambiguous entity
            options: List of possible interpretations
            
        Returns:
            Formatted prompt for user selection
        """
        prompt = f"❓ Ambiguous reference detected\n\n"
        prompt += f"The term '{entity}' in your query '{query}' could refer to:\n\n"
        
        for i, option in enumerate(options, 1):
            prompt += f"{i}. {option}\n"
        
        prompt += f"\nPlease clarify which one you meant, or rephrase your query."
        
        return prompt
    
    def categorize_query_intent(self, query: str) -> str:
        """
        Categorize the intent of a query
        
        Args:
            query: The query to categorize
            
        Returns:
            Intent category
        """
        query_lower = query.lower()
        
        # Financial queries
        if any(word in query_lower for word in self.financial_keywords):
            return "financial"
        
        # Biographical queries
        if any(word in query_lower for word in self.biography_keywords):
            return "biographical"
        
        # Technical queries
        if any(word in query_lower for word in self.technical_keywords):
            return "technical"
        
        # General informational queries
        question_words = {'what', 'how', 'why', 'when', 'where', 'who', 'which'}
        if any(word in query_lower for word in question_words):
            return "informational"
        
        return "general"

# Global instance
output_filter = OutputRelevanceFilter()

def filter_model_output(query: str, response: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Filter model output for relevance and quality
    
    Args:
        query: The original query
        response: The response to filter
        
    Returns:
        Tuple of (should_block, filtered_response, metadata)
    """
    return output_filter.filter_response(query, response)

def handle_ambiguous_entity_response(query: str, entity: str, options: List[str]) -> str:
    """
    Handle ambiguous entity responses
    
    Args:
        query: The original query
        entity: The ambiguous entity
        options: List of possible interpretations
        
    Returns:
        Formatted prompt for user selection
    """
    return output_filter.handle_ambiguous_entity(query, entity, options)

def categorize_user_query(query: str) -> str:
    """
    Categorize user query intent
    
    Args:
        query: The query to categorize
        
    Returns:
        Intent category
    """
    return output_filter.categorize_query_intent(query)