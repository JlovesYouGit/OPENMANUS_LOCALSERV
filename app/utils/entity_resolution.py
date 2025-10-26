"""
Entity Resolution Pipeline for OpenManus
This module implements advanced Named Entity Recognition (NER) with context-aware 
prioritization between financial tickers and product names.
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime

class EntityResolver:
    """Advanced entity resolver with context-aware prioritization"""
    
    def __init__(self):
        # Financial ticker mappings
        self.ticker_mappings = {
            'NVDA': 'NVIDIA Corporation',
            'AAPL': 'Apple Inc.',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc.',
            'AMZN': 'Amazon.com Inc.',
            'TSLA': 'Tesla Inc.',
            'META': 'Meta Platforms Inc.',
            'NFLX': 'Netflix Inc.',
            'IBM': 'International Business Machines Corp.',
            'INTC': 'Intel Corporation',
            'AMD': 'Advanced Micro Devices Inc.',
            'ADBE': 'Adobe Inc.',
            'CRM': 'Salesforce.com Inc.',
            'ORCL': 'Oracle Corporation',
            'SAP': 'SAP SE',
            'CRM': 'Salesforce.com Inc.',
            'NFLX': 'Netflix, Inc.',
            'PYPL': 'PayPal Holdings, Inc.',
            'SQ': 'Block, Inc.',
            'V': 'Visa Inc.',
            'MA': 'Mastercard Incorporated',
            'JPM': 'JPMorgan Chase & Co.',
            'GS': 'The Goldman Sachs Group, Inc.',
            'WFC': 'Wells Fargo & Company',
            'BAC': 'Bank of America Corporation',
            'C': 'Citigroup Inc.',
            'BA': 'The Boeing Company',
            'DIS': 'The Walt Disney Company',
            'NFLX': 'Netflix, Inc.',
            'T': 'AT&T Inc.',
            'VZ': 'Verizon Communications Inc.',
            'TMUS': 'T-Mobile US, Inc.',
        }
        
        # Product/software name mappings
        self.product_mappings = {
            'NVDA': 'NVDA Screen Reader Software',
            'AAPL': 'Apple Products',
            'MSFT': 'Microsoft Products',
            'GOOGL': 'Google Products',
            'AMZN': 'Amazon Products',
        }
        
        # Financial context keywords
        self.financial_context_keywords = {
            'stock', 'price', 'share', 'market', 'trading', 'investment', 
            'portfolio', 'dividend', 'earnings', 'revenue', 'profit',
            'financial', 'quarterly', 'annual', 'report', 'SEC',
            'NASDAQ', 'NYSE', 'exchange', 'broker', 'brokerage',
            'buy', 'sell', 'trade', 'invest', 'investor', 'analyst'
        }
        
        # Product/software context keywords
        self.product_context_keywords = {
            'software', 'application', 'program', 'tool', 'app', 'platform',
            'download', 'install', 'version', 'update', 'release', 'feature',
            'function', 'capability', 'documentation', 'manual', 'tutorial',
            'code', 'programming', 'developer', 'API', 'SDK', 'library',
            'accessibility', 'screen reader', 'reader', 'assistive'
        }
        
        # Ambiguous entities that need context resolution
        self.ambiguous_entities = {
            'NVDA': ['NVIDIA Corporation', 'NVDA Screen Reader Software'],
            'AAPL': ['Apple Inc.', 'Apple Products'],
            'MSFT': ['Microsoft Corporation', 'Microsoft Products'],
        }
    
    def identify_entity_type(self, entity: str, context: str) -> str:
        """
        Identify the type of entity based on context
        
        Args:
            entity: The entity to identify
            context: The context in which the entity appears
            
        Returns:
            'financial', 'product', or 'ambiguous'
        """
        context_lower = context.lower()
        
        # Check for financial context keywords
        financial_score = sum(1 for keyword in self.financial_context_keywords 
                            if keyword in context_lower)
        
        # Check for product context keywords
        product_score = sum(1 for keyword in self.product_context_keywords 
                          if keyword in context_lower)
        
        # If financial keywords significantly outweigh product keywords
        if financial_score > product_score + 2:
            return 'financial'
        # If product keywords significantly outweigh financial keywords
        elif product_score > financial_score + 2:
            return 'product'
        # If both are present or neither is clearly dominant
        else:
            return 'ambiguous'
    
    def resolve_ambiguous_entity(self, entity: str, context: str) -> str:
        """
        Resolve ambiguous entities based on context
        
        Args:
            entity: The ambiguous entity (e.g., 'NVDA')
            context: The context in which the entity appears
            
        Returns:
            The resolved entity name
        """
        if entity not in self.ambiguous_entities:
            return entity
        
        entity_type = self.identify_entity_type(entity, context)
        
        if entity_type == 'financial':
            return self.ticker_mappings.get(entity, entity)
        elif entity_type == 'product':
            return self.product_mappings.get(entity, entity)
        else:
            # For ambiguous cases, provide both options with context
            options = self.ambiguous_entities[entity]
            return f"{entity} (could refer to: {', '.join(options)})"
    
    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract entities from text with context-aware resolution
        
        Args:
            text: The text to extract entities from
            
        Returns:
            List of dictionaries containing entity information
        """
        entities = []
        
        # Extract potential ticker symbols (uppercase 1-5 letters)
        ticker_pattern = r'\b[A-Z]{1,5}\b'
        ticker_matches = re.finditer(ticker_pattern, text)
        
        for match in ticker_matches:
            entity = match.group()
            start, end = match.span()
            
            # Get context around the entity (50 characters before and after)
            context_start = max(0, start - 50)
            context_end = min(len(text), end + 50)
            context = text[context_start:context_end]
            
            # Resolve the entity
            resolved_entity = self.resolve_ambiguous_entity(entity, context)
            
            entities.append({
                'original': entity,
                'resolved': resolved_entity,
                'type': self.identify_entity_type(entity, context),
                'context': context,
                'position': (start, end)
            })
        
        # Extract company names
        company_pattern = r'\b(?:NVIDIA|Apple|Microsoft|Google|Alphabet|Amazon|Tesla|Meta|Netflix|Intel|AMD|Adobe|Salesforce|Oracle|SAP|PayPal|Block|Visa|Mastercard|JPMorgan|Goldman Sachs|Wells Fargo|Bank of America|Citigroup|Boeing|Disney|AT&T|Verizon|T-Mobile)\b(?:\s(?:Inc\.?|Corporation|Corp\.?|Company|Ltd\.?|Limited|LLC|PLC|S\.A\.|AG|SE|SA|GmbH|Co\.|Group|Holdings|Holdings,?\s+Inc\.?|Communications|Communications,?\s+Inc\.?))*'
        company_matches = re.finditer(company_pattern, text, re.IGNORECASE)
        
        for match in company_matches:
            entity = match.group()
            start, end = match.span()
            
            # Get context around the entity
            context_start = max(0, start - 50)
            context_end = min(len(text), end + 50)
            context = text[context_start:context_end]
            
            entities.append({
                'original': entity,
                'resolved': entity,
                'type': 'company',
                'context': context,
                'position': (start, end)
            })
        
        return entities
    
    def generate_entity_context_prompt(self, entities: List[Dict[str, str]], query: str) -> str:
        """
        Generate a context prompt for the model based on extracted entities
        
        Args:
            entities: List of extracted entities
            query: The original query
            
        Returns:
            Enhanced context prompt
        """
        if not entities:
            return f"Query: {query}"
        
        context_parts = [f"Query: {query}"]
        context_parts.append("Identified entities:")
        
        for entity in entities:
            if entity['type'] == 'ambiguous':
                context_parts.append(f"  - {entity['original']}: {entity['resolved']}")
            else:
                context_parts.append(f"  - {entity['original']} ({entity['type']}): {entity['resolved']}")
        
        return "\n".join(context_parts)

# Global instance
entity_resolver = EntityResolver()

def resolve_entities_in_query(query: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Resolve entities in a query with context-aware prioritization
    
    Args:
        query: The query to process
        
    Returns:
        Tuple of (enhanced_query, entities)
    """
    entities = entity_resolver.extract_entities(query)
    enhanced_context = entity_resolver.generate_entity_context_prompt(entities, query)
    return enhanced_context, entities

def is_financial_query(query: str) -> bool:
    """
    Determine if a query is primarily about financial information
    
    Args:
        query: The query to analyze
        
    Returns:
        True if the query is financial-focused, False otherwise
    """
    return entity_resolver.identify_entity_type('', query) == 'financial'