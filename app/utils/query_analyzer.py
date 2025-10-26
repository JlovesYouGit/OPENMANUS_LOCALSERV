"""
Query Analysis and Intent Detection for OpenManus
This module provides deep query analysis and intent detection to improve the agent's understanding of user requests.
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

class QueryType(Enum):
    """Enumeration of query types for better categorization"""
    GREETING = "greeting"
    PERSONAL_QUESTION = "personal_question"
    CORRECTION = "correction"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    ANALYTICAL = "analytical"
    OPERATIONAL = "operational"
    CURRENT_INFO = "current_info"
    SYSTEM_DIAGNOSTIC = "system_diagnostic"
    GENERAL = "general"

@dataclass
class QueryAnalysis:
    """Structured analysis of a user query"""
    query_type: QueryType
    confidence: float
    intent_keywords: List[str]
    entities: List[str]
    requires_current_info: bool
    requires_tools: List[str]
    complexity: int  # 1-5 scale

class QueryAnalyzer:
    """Advanced query analyzer for intent detection and classification"""
    
    def __init__(self):
        # Define patterns for different query types with weights
        self.patterns = {
            QueryType.GREETING: [
                (r'\b(hi|hello|hey|greetings|howdy|what\'?s up)\b', 0.9),
                (r'\b(good morning|good afternoon|good evening)\b', 0.8),
                (r'\b(how are you|how\'?s it going)\b', 0.7)
            ],
            QueryType.PERSONAL_QUESTION: [
                (r'\b(who is|what is|tell me about|biography|life of)\b', 0.9),
                (r'\b(born in|died in|career of|history of)\b', 0.8)
            ],
            QueryType.CORRECTION: [
                (r'\b(that\'?s not what i said|not what i meant|i meant)\b', 0.9),
                (r'\b(correction|wrong|incorrect|that\'?s not right)\b', 0.8)
            ],
            QueryType.FINANCIAL: [
                (r'\b(stock|price|share|market|trading|investment|portfolio)\b', 0.9),
                (r'\b(dividend|earnings|revenue|profit|financial)\b', 0.8),
                (r'\b(NASDAQ|NYSE|exchange|broker)\b', 0.95)
            ],
            QueryType.TECHNICAL: [
                (r'\b(code|program|software|application|function|class)\b', 0.9),
                (r'\b(API|SDK|framework|algorithm|data|database)\b', 0.8),
                (r'\b(server|client|network|protocol|system)\b', 0.7)
            ],
            QueryType.ANALYTICAL: [
                (r'\b(analyze|compare|contrast|evaluate|assess)\b', 0.9),
                (r'\b(trend|pattern|correlation|statistic)\b', 0.8),
                (r'\b(data|report|metric|KPI)\b', 0.7)
            ],
            QueryType.OPERATIONAL: [
                (r'\b(run|execute|deploy|configure|setup)\b', 0.9),
                (r'\b(command|script|tool|utility)\b', 0.8),
                (r'\b(workflow|process|pipeline)\b', 0.7)
            ],
            QueryType.CURRENT_INFO: [
                (r'\b(current|today|now|latest|recent|up-to-date)\b', 0.8),
                (r'\b(weather|temperature|news|breaking)\b', 0.9),
                (r'\b(time|date|moment|presently)\b', 0.7)
            ],
            QueryType.SYSTEM_DIAGNOSTIC: [
                (r'\b(debug|diagnose|troubleshoot|error|issue)\b', 0.9),
                (r'\b(log|trace|warning|exception)\b', 0.8),
                (r'\b(performance|memory|cpu|resource)\b', 0.7)
            ]
        }
        
        # Keywords that indicate complexity
        self.complexity_indicators = {
            1: ['what', 'how', 'tell'],
            2: ['explain', 'describe', 'compare'],
            3: ['analyze', 'evaluate', 'assess'],
            4: ['implement', 'develop', 'create'],
            5: ['optimize', 'troubleshoot', 'debug']
        }
        
        # Tool requirements mapping
        self.tool_requirements = {
            QueryType.FINANCIAL: ['web_search'],
            QueryType.CURRENT_INFO: ['web_search'],
            QueryType.TECHNICAL: ['python_execute', 'str_replace_editor'],
            QueryType.ANALYTICAL: ['web_search', 'python_execute'],
            QueryType.OPERATIONAL: ['browser_use_tool'],
            QueryType.SYSTEM_DIAGNOSTIC: ['python_execute']
        }
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze a query to determine its type, intent, and requirements
        
        Args:
            query: The user's query string
            
        Returns:
            QueryAnalysis object with detailed analysis
        """
        query_lower = query.lower()
        scores = {}
        
        # Score each query type based on pattern matching
        for query_type, patterns in self.patterns.items():
            score = 0.0
            matched_keywords = []
            
            for pattern, weight in patterns:
                matches = re.findall(pattern, query_lower)
                if matches:
                    score += weight * len(matches)
                    matched_keywords.extend(matches)
            
            scores[query_type] = (score, matched_keywords)
        
        # Determine the best matching query type
        best_type = max(scores.keys(), key=lambda x: scores[x][0])
        confidence = scores[best_type][0]
        intent_keywords = scores[best_type][1]
        
        # Extract entities (named entities, company names, etc.)
        entities = self._extract_entities(query)
        
        # Determine if current information is required
        requires_current_info = self._requires_current_information(query_lower)
        
        # Determine required tools
        required_tools = self.tool_requirements.get(best_type, [])
        
        # Calculate complexity
        complexity = self._calculate_complexity(query_lower)
        
        # If confidence is very low, default to general query but still allow natural responses
        if confidence < 0.2:
            best_type = QueryType.GENERAL
            confidence = 0.3  # Lower confidence to allow more natural model responses
            intent_keywords = []
            required_tools = []
        
        return QueryAnalysis(
            query_type=best_type,
            confidence=min(confidence, 1.0),
            intent_keywords=intent_keywords,
            entities=entities,
            requires_current_info=requires_current_info,
            requires_tools=required_tools,
            complexity=complexity
        )
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract named entities from query"""
        # Simple entity extraction - in a real implementation, this would use NER
        words = query.split()
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
    
    def _requires_current_information(self, query_lower: str) -> bool:
        """Determine if query requires current information"""
        current_keywords = [
            "stock", "price", "current", "today", "now", "latest", 
            "recent", "up-to-date", "real-time", "live", "market",
            "weather", "temperature", "news", "breaking", "time",
            "date", "moment", "presently", "currently", "right now"
        ]
        
        return any(keyword in query_lower for keyword in current_keywords)
    
    def _calculate_complexity(self, query_lower: str) -> int:
        """Calculate query complexity on a 1-5 scale"""
        complexity = 1
        
        for level, keywords in self.complexity_indicators.items():
            if any(keyword in query_lower for keyword in keywords):
                complexity = max(complexity, level)
                
        return complexity

# Global instance
query_analyzer = QueryAnalyzer()

def analyze_user_query(query: str) -> QueryAnalysis:
    """
    Analyze a user query for intent and requirements
    
    Args:
        query: The user's query string
        
    Returns:
        QueryAnalysis object with detailed analysis
    """
    return query_analyzer.analyze_query(query)

def get_query_type_description(query_type: QueryType) -> str:
    """Get a human-readable description of a query type"""
    descriptions = {
        QueryType.GREETING: "Greeting or casual conversation starter",
        QueryType.PERSONAL_QUESTION: "Question about a person or entity",
        QueryType.CORRECTION: "User correction or clarification request",
        QueryType.FINANCIAL: "Financial information request (stocks, prices, etc.)",
        QueryType.TECHNICAL: "Technical request (code, software, systems)",
        QueryType.ANALYTICAL: "Analytical request (data analysis, comparisons)",
        QueryType.OPERATIONAL: "Operational request (execution, deployment)",
        QueryType.CURRENT_INFO: "Request for current/up-to-date information",
        QueryType.SYSTEM_DIAGNOSTIC: "System diagnostic or troubleshooting request",
        QueryType.GENERAL: "General information request"
    }
    
    return descriptions.get(query_type, "Unknown query type")