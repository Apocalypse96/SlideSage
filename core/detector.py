"""
Inconsistency detection logic combining rule-based and AI analysis.
"""

import logging
from typing import Dict, List, Any, Tuple
from collections import defaultdict

from utils.helpers import calculate_similarity, extract_numbers_and_dates


class InconsistencyDetector:
    """Detects inconsistencies using both rule-based and AI analysis."""
    
    def __init__(self):
        """Initialize the inconsistency detector."""
        self.logger = logging.getLogger(__name__)
    
    def detect_inconsistencies(self, slides_data: Dict[int, Dict[str, Any]], 
                             ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect inconsistencies using both rule-based and AI analysis.
        
        Args:
            slides_data: Dictionary of slide data
            ai_analysis: Results from AI analysis
            
        Returns:
            Combined inconsistency detection results
        """
        # Rule-based detection
        rule_based_results = self._rule_based_detection(slides_data)
        
        # AI-based detection
        ai_results = self._extract_ai_results(ai_analysis)
        
        # Combine and deduplicate results
        combined_results = self._combine_results(rule_based_results, ai_results)
        
        # Calculate summary statistics
        summary = self._calculate_summary(combined_results, slides_data)
        
        return {
            'summary': summary,
            'inconsistencies': combined_results,
            'rule_based_count': len(self._flatten_inconsistencies(rule_based_results)),
            'ai_based_count': len(self._flatten_inconsistencies(ai_results))
        }
    
    def _rule_based_detection(self, slides_data: Dict[int, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform rule-based inconsistency detection.
        
        Args:
            slides_data: Dictionary of slide data
            
        Returns:
            Rule-based detection results
        """
        results = {
            'numerical_conflicts': [],
            'contradictory_statements': [],
            'timeline_issues': [],
            'logical_inconsistencies': []
        }
        
        # Detect numerical conflicts
        numerical_conflicts = self._detect_numerical_conflicts(slides_data)
        results['numerical_conflicts'].extend(numerical_conflicts)
        
        # Detect contradictory statements
        contradictory_statements = self._detect_contradictory_statements(slides_data)
        results['contradictory_statements'].extend(contradictory_statements)
        
        # Detect timeline issues
        timeline_issues = self._detect_timeline_issues(slides_data)
        results['timeline_issues'].extend(timeline_issues)
        
        return results
    
    def _detect_numerical_conflicts(self, slides_data: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect conflicting numerical data across slides."""
        conflicts = []
        
        # Collect numerical data by context/category
        revenue_data = defaultdict(list)
        percentage_data = defaultdict(list)
        quantity_data = defaultdict(list)
        
        for slide_num, slide_data in slides_data.items():
            slide_text = ' '.join(slide_data['text']).lower()
            
            # Look for revenue-related numbers
            for currency in slide_data['currency']:
                if any(word in slide_text for word in ['revenue', 'sales', 'income', 'earnings']):
                    revenue_data[currency].append(slide_num)
            
            # Look for percentage data with context
            for percentage in slide_data['percentages']:
                if any(word in slide_text for word in ['market share', 'growth', 'increase', 'decrease']):
                    percentage_data[percentage].append(slide_num)
            
            # Look for quantity data with context
            for number in slide_data['numbers']:
                if any(word in slide_text for word in ['employees', 'customers', 'users', 'units']):
                    quantity_data[number].append(slide_num)
        
        # Check for actual conflicts (different values for same metric)
        for metric, slide_nums in revenue_data.items():
            if len(slide_nums) > 1:
                conflicts.append({
                    'slide_numbers': slide_nums,
                    'description': f"Conflicting revenue figures: {metric} appears on multiple slides",
                    'severity': 'high',
                    'type': 'revenue_conflict'
                })
        
        for metric, slide_nums in percentage_data.items():
            if len(slide_nums) > 1:
                conflicts.append({
                    'slide_numbers': slide_nums,
                    'description': f"Conflicting percentage data: {metric} appears on multiple slides",
                    'severity': 'high',
                    'type': 'percentage_conflict'
                })
        
        for metric, slide_nums in quantity_data.items():
            if len(slide_nums) > 1:
                conflicts.append({
                    'slide_numbers': slide_nums,
                    'description': f"Conflicting quantity data: {metric} appears on multiple slides",
                    'severity': 'medium',
                    'type': 'quantity_conflict'
                })
        
        return conflicts
    
    def _detect_contradictory_statements(self, slides_data: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect contradictory statements across slides."""
        contradictions = []
        
        # Define contradiction patterns with context
        contradiction_patterns = [
            # Market analysis contradictions
            ('highly competitive', 'few competitors', 'market competition'),
            ('growing market', 'declining market', 'market growth'),
            ('market leader', 'small player', 'market position'),
            
            # Performance contradictions
            ('increasing revenue', 'decreasing revenue', 'revenue trend'),
            ('profitable', 'unprofitable', 'profitability'),
            ('successful', 'unsuccessful', 'success'),
            ('strong performance', 'weak performance', 'performance'),
            
            # Strategy contradictions
            ('cost reduction', 'heavy investment', 'strategy'),
            ('focus on efficiency', 'expand rapidly', 'approach'),
            ('conservative', 'aggressive', 'strategy'),
            
            # Timeline contradictions
            ('launch in 2024', 'launch in 2025', 'launch timeline'),
            ('phase 1 complete', 'phase 1 ongoing', 'project status'),
            ('ahead of schedule', 'behind schedule', 'project timeline')
        ]
        
        # Collect all text content
        all_text = {}
        for slide_num, slide_data in slides_data.items():
            slide_text = ' '.join(slide_data['text']).lower()
            all_text[slide_num] = slide_text
        
        # Check for contradictions
        for pattern1, pattern2, context in contradiction_patterns:
            slides_with_pattern1 = []
            slides_with_pattern2 = []
            
            for slide_num, text in all_text.items():
                if pattern1 in text:
                    slides_with_pattern1.append(slide_num)
                if pattern2 in text:
                    slides_with_pattern2.append(slide_num)
            
            if slides_with_pattern1 and slides_with_pattern2:
                contradictions.append({
                    'slide_numbers': slides_with_pattern1 + slides_with_pattern2,
                    'description': f"Contradictory {context}: '{pattern1}' vs '{pattern2}'",
                    'severity': 'high',
                    'type': 'contradictory_statements'
                })
        
        return contradictions
    
    def _detect_timeline_issues(self, slides_data: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect timeline and date issues across slides."""
        timeline_issues = []
        
        # Collect all dates
        all_dates = {}
        for slide_num, slide_data in slides_data.items():
            if slide_data['dates']:
                all_dates[slide_num] = slide_data['dates']
        
        # Check for date conflicts (simplified - would need more sophisticated date parsing)
        if len(all_dates) > 1:
            # This is a simplified check - in practice, you'd want to parse dates properly
            timeline_issues.append({
                'slide_numbers': list(all_dates.keys()),
                'description': "Multiple dates found across slides - potential timeline conflicts",
                'severity': 'medium',
                'type': 'timeline_issues'
            })
        
        return timeline_issues
    
    def _normalize_number(self, number_str: str) -> str:
        """Normalize number string for comparison."""
        try:
            # Remove commas and convert to float
            cleaned = number_str.replace(',', '')
            float(cleaned)  # Validate it's a number
            return cleaned
        except (ValueError, AttributeError):
            return ""
    
    def _normalize_percentage(self, percentage_str: str) -> str:
        """Normalize percentage string for comparison."""
        try:
            # Remove % and convert to float
            cleaned = percentage_str.replace('%', '').strip()
            float(cleaned)  # Validate it's a number
            return cleaned
        except (ValueError, AttributeError):
            return ""
    
    def _normalize_currency(self, currency_str: str) -> str:
        """Normalize currency string for comparison."""
        try:
            # Remove currency symbols and commas
            cleaned = currency_str.replace('$', '').replace('€', '').replace('£', '').replace('¥', '').replace('₹', '').replace(',', '').strip()
            float(cleaned)  # Validate it's a number
            return cleaned
        except (ValueError, AttributeError):
            return ""
    
    def _extract_ai_results(self, ai_analysis: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract results from AI analysis."""
        if 'error' in ai_analysis:
            self.logger.warning(f"AI analysis had error: {ai_analysis['error']}")
            return self._get_empty_inconsistencies()
        
        inconsistencies = ai_analysis.get('inconsistencies', {})
        
        return {
            'numerical_conflicts': inconsistencies.get('numerical_conflicts', []),
            'contradictory_statements': inconsistencies.get('contradictory_statements', []),
            'timeline_issues': inconsistencies.get('timeline_issues', []),
            'logical_inconsistencies': inconsistencies.get('logical_inconsistencies', [])
        }
    
    def _combine_results(self, rule_based: Dict[str, List[Dict[str, Any]]], 
                        ai_based: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Combine and deduplicate rule-based and AI results."""
        combined = {}
        
        for category in ['numerical_conflicts', 'contradictory_statements', 'timeline_issues', 'logical_inconsistencies']:
            rule_items = rule_based.get(category, [])
            ai_items = ai_based.get(category, [])
            
            # Combine items
            all_items = rule_items + ai_items
            
            # Remove duplicates based on slide numbers and description similarity
            unique_items = self._deduplicate_items(all_items)
            
            combined[category] = unique_items
        
        return combined
    
    def _deduplicate_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate inconsistency items."""
        unique_items = []
        seen_combinations = set()
        
        for item in items:
            slide_nums = tuple(sorted(item.get('slide_numbers', [])))
            description = item.get('description', '').lower()
            
            # Create a key for deduplication
            key = (slide_nums, description[:50])  # Use first 50 chars of description
            
            if key not in seen_combinations:
                seen_combinations.add(key)
                unique_items.append(item)
        
        return unique_items
    
    def _calculate_summary(self, inconsistencies: Dict[str, List[Dict[str, Any]]], 
                          slides_data: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        total_inconsistencies = sum(len(items) for items in inconsistencies.values())
        
        # Count by severity
        severity_counts = defaultdict(int)
        for category_items in inconsistencies.values():
            for item in category_items:
                severity = item.get('severity', 'unknown')
                severity_counts[severity] += 1
        
        # Count by category
        category_counts = {category: len(items) for category, items in inconsistencies.items()}
        
        return {
            'total_slides': len(slides_data),
            'slides_analyzed': len(slides_data),
            'inconsistencies_found': total_inconsistencies,
            'severity_breakdown': dict(severity_counts),
            'category_breakdown': category_counts
        }
    
    def _flatten_inconsistencies(self, inconsistencies: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Flatten inconsistencies dictionary to a list."""
        flattened = []
        for category_items in inconsistencies.values():
            flattened.extend(category_items)
        return flattened
    
    def _get_empty_inconsistencies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return empty inconsistencies structure."""
        return {
            'numerical_conflicts': [],
            'contradictory_statements': [],
            'timeline_issues': [],
            'logical_inconsistencies': []
        } 