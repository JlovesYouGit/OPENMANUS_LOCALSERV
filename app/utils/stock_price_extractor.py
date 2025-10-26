"""
Enhanced Stock Price Extraction with Validation and Source Tracking
This module implements improved stock price extraction with validation and source tracking.
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class StockPriceData:
    """Data class for stock price information with metadata"""
    symbol: str
    price: float
    currency: str = "USD"
    source: str = ""
    timestamp: str = ""
    confidence: float = 0.0
    validation_notes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.validation_notes is None:
            self.validation_notes = []

class StockPriceExtractor:
    """Enhanced stock price extractor with validation and source tracking"""
    
    def __init__(self):
        # Valid stock price range (in USD)
        self.min_price = 0.01
        self.max_price = 1000000.0
        
        # Common financial sources
        self.trusted_sources = [
            "Yahoo Finance", "Google Finance", "MarketWatch", 
            "Bloomberg", "Reuters", "CNBC", "WSJ", "Financial Times"
        ]
        
        # Price patterns with confidence scores
        self.price_patterns = [
            # Pattern 1: $XXX.XX (most common) - High confidence
            (r'\$\s*([0-9]+[0-9,]*\.?[0-9]+)', 0.9),
            # Pattern 2: XXX.XX USD - High confidence
            (r'([0-9]+[0-9,]*\.?[0-9]+)\s*(?:usd|dollars?|\$)', 0.85),
            # Pattern 3: Price: $XXX.XX - High confidence
            (r'(?:price|current price|stock price)[:\s]*\$?\s*([0-9]+[0-9,]*\.?[0-9]+)', 0.9),
            # Pattern 4: Numerical patterns with decimal - Medium confidence
            (r'\b([0-9]+[0-9,]*\.[0-9]{2})\b', 0.7),
            # Pattern 5: Stock ticker specific patterns (AAPL: $175.50) - High confidence
            (r'(?:aapl|apple|msft|microsoft|goog|google|amzn|amazon|tsla|tesla|nvda|nvidia|meta|fb|facebook|nflx|netflix|ibm|intc|intel|amd|adbe|adobe|crm|salesforce)[:\s]*\$?\s*([0-9]+[0-9,]*\.?[0-9]+)', 0.95),
        ]
        
        # Currency symbols and codes
        self.currency_mapping = {
            '$': 'USD',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY',
            '₹': 'INR',
            'USD': 'USD',
            'EUR': 'EUR',
            'GBP': 'GBP',
            'JPY': 'JPY',
            'INR': 'INR',
        }
    
    def extract_stock_prices(self, content: str, source: str = "") -> List[StockPriceData]:
        """
        Extract stock prices from content with validation and source tracking
        
        Args:
            content: The content to extract prices from
            source: The source of the content
            
        Returns:
            List of validated stock price data
        """
        prices = []
        content_lower = content.lower()
        
        # Extract potential stock symbols
        ticker_symbols = self._extract_ticker_symbols(content)
        
        # Try each price pattern
        for pattern, base_confidence in self.price_patterns:
            matches = re.finditer(pattern, content_lower)
            for match in matches:
                price_str = match.group(1).replace(',', '')
                try:
                    price = float(price_str)
                    
                    # Validate price range
                    if not (self.min_price <= price <= self.max_price):
                        continue
                    
                    # Determine currency
                    currency = self._determine_currency(content, match.start(), match.end())
                    
                    # Determine confidence based on validation
                    confidence = self._calculate_confidence(price, pattern, content, match)
                    
                    # Create stock price data
                    price_data = StockPriceData(
                        symbol=ticker_symbols[0] if ticker_symbols else "UNKNOWN",
                        price=price,
                        currency=currency,
                        source=source,
                        timestamp=datetime.now().isoformat(),
                        confidence=confidence * base_confidence
                    )
                    
                    # Add validation notes
                    self._add_validation_notes(price_data, content, match)
                    
                    prices.append(price_data)
                except ValueError:
                    continue
        
        # Sort by confidence (highest first)
        prices.sort(key=lambda x: x.confidence, reverse=True)
        return prices
    
    def _extract_ticker_symbols(self, content: str) -> List[str]:
        """Extract ticker symbols from content"""
        # Common ticker patterns
        ticker_pattern = r'\b[A-Z]{1,5}[:\s]*\$?[0-9]'
        matches = re.findall(ticker_pattern, content)
        symbols = []
        for match in matches:
            # Extract just the symbol part
            symbol = re.sub(r'[:\s]*\$?[0-9].*$', '', match)
            if symbol:
                symbols.append(symbol)
        return symbols
    
    def _determine_currency(self, content: str, start: int, end: int) -> str:
        """Determine currency from context"""
        # Check around the match for currency symbols
        context_start = max(0, start - 10)
        context_end = min(len(content), end + 10)
        context = content[context_start:context_end].lower()
        
        for symbol, currency in self.currency_mapping.items():
            if symbol.lower() in context:
                return currency
        
        return "USD"  # Default to USD
    
    def _calculate_confidence(self, price: float, pattern: str, content: str, match) -> float:
        """Calculate confidence score for a price extraction"""
        confidence = 1.0
        
        # Check if price is within reasonable range for a stock price
        # Avoid extremely low prices that might be errors
        if price < 1.0:
            confidence *= 0.5  # Lower confidence for very low prices
        
        # Check if price has exactly 2 decimal places (typical for stock prices)
        price_str = str(price)
        if '.' in price_str and len(price_str.split('.')[1]) == 2:
            confidence *= 1.2  # Boost confidence
        elif price > 10000:
            confidence *= 0.8  # Lower confidence for very high prices
        
        # Check context for financial terms
        context_start = max(0, match.start() - 50)
        context_end = min(len(content), match.end() + 50)
        context = content[context_start:context_end].lower()
        
        financial_terms = ['stock', 'price', 'share', 'market', 'trading', 'exchange']
        financial_count = sum(1 for term in financial_terms if term in context)
        if financial_count > 0:
            confidence *= 1.1  # Boost confidence
        
        # Cap confidence at 1.0
        return min(confidence, 1.0)
    
    def _add_validation_notes(self, price_data: StockPriceData, content: str, match):
        """Add validation notes to price data"""
        notes = []
        
        # Check if price is within reasonable range
        if price_data.price < 1.0:
            notes.append("Price is very low, may be incorrect")
        elif price_data.price > 10000:
            notes.append("Price is very high, verify accuracy")
        
        # Check decimal places
        price_str = str(price_data.price)
        if '.' in price_str:
            decimal_places = len(price_str.split('.')[1])
            if decimal_places != 2:
                notes.append(f"Price has {decimal_places} decimal places, expected 2")
        
        # Check source trustworthiness
        if price_data.source:
            is_trusted = any(trusted.lower() in price_data.source.lower() 
                           for trusted in self.trusted_sources)
            if not is_trusted:
                notes.append("Source is not in trusted financial sources list")
        
        price_data.validation_notes = notes
    
    def validate_price_consistency(self, prices: List[StockPriceData]) -> Dict[str, Any]:
        """
        Validate consistency between multiple price extractions
        
        Args:
            prices: List of extracted prices
            
        Returns:
            Dictionary with validation results
        """
        if not prices:
            return {"consistent": False, "reason": "No prices extracted"}
        
        if len(prices) == 1:
            return {"consistent": True, "primary_price": prices[0]}
        
        # Group prices by symbol
        symbol_groups = {}
        for price in prices:
            if price.symbol not in symbol_groups:
                symbol_groups[price.symbol] = []
            symbol_groups[price.symbol].append(price)
        
        # Validate each symbol group
        results = {}
        for symbol, symbol_prices in symbol_groups.items():
            if len(symbol_prices) == 1:
                results[symbol] = {"consistent": True, "primary_price": symbol_prices[0]}
                continue
            
            # Sort by confidence
            symbol_prices.sort(key=lambda x: x.confidence, reverse=True)
            primary_price = symbol_prices[0]
            
            # Check if other prices are within 5% of the primary price
            consistent = True
            inconsistent_prices = []
            for price in symbol_prices[1:]:
                if primary_price.price > 0:
                    diff_percent = abs(price.price - primary_price.price) / primary_price.price * 100
                    if diff_percent > 5.0:  # 5% threshold
                        consistent = False
                        inconsistent_prices.append(price)
            
            results[symbol] = {
                "consistent": consistent,
                "primary_price": primary_price,
                "inconsistent_prices": inconsistent_prices if inconsistent_prices else None
            }
        
        return results
    
    def format_price_output(self, price_data: StockPriceData) -> str:
        """
        Format price data for output with metadata
        
        Args:
            price_data: The price data to format
            
        Returns:
            Formatted string with price and metadata
        """
        formatted = f"${price_data.price:.2f} {price_data.currency}"
        if price_data.symbol != "UNKNOWN":
            formatted = f"{price_data.symbol}: {formatted}"
        
        # Add metadata
        metadata = []
        if price_data.source:
            metadata.append(f"Source: {price_data.source}")
        if price_data.timestamp:
            # Format timestamp to be more readable
            try:
                dt = datetime.fromisoformat(price_data.timestamp)
                metadata.append(f"Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                metadata.append(f"Time: {price_data.timestamp}")
        if price_data.confidence < 0.8:
            metadata.append(f"Confidence: {price_data.confidence:.2f}")
        
        if metadata:
            formatted += f" ({', '.join(metadata)})"
        
        # Add validation warnings if any
        if price_data.validation_notes:
            formatted += f"\n⚠️  Validation warnings: {', '.join(price_data.validation_notes)}"
        
        return formatted

# Global instance
stock_extractor = StockPriceExtractor()

def extract_and_validate_stock_prices(content: str, source: str = "") -> Tuple[List[StockPriceData], str]:
    """
    Extract and validate stock prices from content
    
    Args:
        content: The content to extract prices from
        source: The source of the content
        
    Returns:
        Tuple of (list of validated prices, formatted output string)
    """
    prices = stock_extractor.extract_stock_prices(content, source)
    validation_results = stock_extractor.validate_price_consistency(prices)
    
    if not prices:
        return [], "No stock prices found in the content."
    
    # Format output based on validation results
    output_lines = []
    
    for symbol, result in validation_results.items():
        if result["consistent"]:
            primary_price = result["primary_price"]
            formatted_price = stock_extractor.format_price_output(primary_price)
            output_lines.append(formatted_price)
        else:
            # Show inconsistency warning
            primary_price = result["primary_price"]
            formatted_price = stock_extractor.format_price_output(primary_price)
            output_lines.append(f"⚠️  {formatted_price}")
            
            if result["inconsistent_prices"]:
                output_lines.append("Inconsistent prices found:")
                for inconsistent_price in result["inconsistent_prices"]:
                    formatted_inconsistent = stock_extractor.format_price_output(inconsistent_price)
                    output_lines.append(f"  - {formatted_inconsistent}")
    
    return prices, "\n".join(output_lines)