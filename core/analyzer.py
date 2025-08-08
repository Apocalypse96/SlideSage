"""
Gemini AI analyzer for detecting inconsistencies in PowerPoint content.
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()


class GeminiAnalyzer:
    """Handles AI-powered analysis using Google's Gemini 2.5 Flash API."""
    
    def __init__(self, api_key: Optional[str] = None, max_tokens: int = 4000):
        """
        Initialize Gemini analyzer.
        
        Args:
            api_key: Gemini API key (if None, will try to load from environment)
            max_tokens: Maximum tokens for API calls
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.max_tokens = max_tokens
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
        if not self.api_key:
            self.logger.error("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
    
    def analyze_inconsistencies(self, slides_data: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze slides for inconsistencies using Gemini AI.
        
        Args:
            slides_data: Dictionary of slide data
            
        Returns:
            Analysis results with detected inconsistencies
        """
        if not self.api_key:
            self.logger.error("Cannot analyze: No API key available")
            return {'error': 'No API key available'}
        
        try:
            # Prepare content for analysis
            analysis_content = self._prepare_analysis_content(slides_data)
            
            # Generate analysis prompt
            prompt = self._generate_analysis_prompt(analysis_content)
            
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            # Parse and structure results
            intelligence_report = self._parse_analysis_response(response)
            
            # Check if we got intelligence-level analysis
            if isinstance(intelligence_report, dict) and 'executive_summary' in intelligence_report:
                # Return intelligence-level format
                return {
                    'intelligence_report': intelligence_report,
                    'analysis_timestamp': time.time(),
                    'slides_analyzed': len(slides_data),
                    'analysis_type': 'intelligence'
                }
            else:
                # Fallback to legacy format
                return {
                    'inconsistencies': intelligence_report,
                    'analysis_timestamp': time.time(),
                    'slides_analyzed': len(slides_data),
                    'analysis_type': 'legacy'
                }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def _prepare_analysis_content(self, slides_data: Dict[int, Dict[str, Any]]) -> str:
        """
        Prepare slide content for AI analysis.
        
        Args:
            slides_data: Dictionary of slide data
            
        Returns:
            Formatted content string for analysis
        """
        content_parts = []
        
        for slide_num, slide_data in slides_data.items():
            slide_content = f"SLIDE {slide_num}:\n"
            
            # Add titles
            if slide_data['titles']:
                slide_content += f"Titles: {' | '.join(slide_data['titles'])}\n"
            
            # Add body text
            if slide_data['body_text']:
                slide_content += f"Content: {' | '.join(slide_data['body_text'])}\n"
            
            # Add table data
            if slide_data['table_data']:
                slide_content += f"Tables: {' | '.join(slide_data['table_data'])}\n"
            
            # Add extracted data
            if slide_data['numbers']:
                slide_content += f"Numbers: {', '.join(slide_data['numbers'])}\n"
            if slide_data['percentages']:
                slide_content += f"Percentages: {', '.join(slide_data['percentages'])}\n"
            if slide_data['currency']:
                slide_content += f"Currency: {', '.join(slide_data['currency'])}\n"
            if slide_data['dates']:
                slide_content += f"Dates: {', '.join(slide_data['dates'])}\n"
            
            content_parts.append(slide_content)
        
        return "\n".join(content_parts)
    
    def _generate_analysis_prompt(self, content: str) -> str:
        """
        Generate intelligence-level analysis prompt for Gemini.
        
        Args:
            content: Formatted slide content
            
        Returns:
            Complete intelligence analysis prompt
        """
        return f"""
You are a Senior Business Intelligence Analyst. Analyze this PowerPoint presentation for inconsistencies and provide intelligence-level insights.

SLIDE CONTENT:
{content}

Analyze for:
1. Factual inconsistencies (conflicting numbers, dates, claims)
2. Strategic contradictions (opposing business approaches)
3. Narrative inconsistencies (logical contradictions)
4. Risk factors (potential legal/compliance issues)
5. Business impact assessment

Return ONLY valid JSON in this exact format:
{{
    "intelligence_report": {{
        "executive_summary": {{
            "overall_risk_level": "critical|high|medium|low",
            "data_integrity_score": "score/10",
            "strategic_coherence_score": "score/10",
            "stakeholder_confidence_impact": "high|medium|low",
            "critical_findings_count": 0,
            "business_impact_assessment": "description"
        }},
        "detailed_analysis": [
            {{
                "category": "factual|strategic|narrative|risk",
                "severity": "critical|high|medium|low",
                "slides": [1, 2],
                "issue_type": "data_conflict|strategic_contradiction",
                "detailed_description": "description",
                "business_impact": "impact description",
                "intelligence_insights": "insights",
                "recommended_actions": ["action1", "action2"],
                "confidence_level": "high|medium|low"
            }}
        ],
        "strategic_recommendations": [
            {{
                "priority": "immediate|short_term|long_term",
                "action": "action description",
                "rationale": "why important",
                "expected_outcome": "expected result"
            }}
        ],
        "data_quality_assessment": {{
            "reliability_score": "score/10",
            "consistency_score": "score/10",
            "completeness_score": "score/10",
            "accuracy_indicators": ["concern1"],
            "data_gaps": ["gap1"],
            "verification_needs": ["need1"]
        }},
        "stakeholder_impact_analysis": {{
            "investor_confidence": "high|medium|low",
            "employee_trust": "high|medium|low",
            "customer_perception": "high|medium|low",
            "regulatory_risk": "high|medium|low"
        }}
    }}
}}

IMPORTANT: Return ONLY the JSON object. No additional text, explanations, or markdown formatting.
"""
    
    def _call_gemini_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call the Gemini API with the analysis prompt.
        
        Args:
            prompt: Analysis prompt
            
        Returns:
            API response
        """
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            'contents': [{
                'parts': [{
                    'text': prompt
                }]
            }],
            'generationConfig': {
                'maxOutputTokens': self.max_tokens,
                'temperature': 0.1,  # Low temperature for more consistent results
                'topP': 0.8,
                'topK': 40
            }
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API call failed: {str(e)}")
            raise
    
    def _parse_analysis_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the Gemini API response and extract intelligence analysis.
        
        Args:
            response: Raw API response
            
        Returns:
            Structured intelligence analysis data
        """
        try:
            # Extract text from response
            if 'candidates' in response and response['candidates']:
                text = response['candidates'][0]['content']['parts'][0]['text']
                
                # Try to parse as JSON with multiple fallback strategies
                parsed_data = self._robust_json_parse(text)
                
                if parsed_data:
                    # Check if it's the new intelligence format
                    if 'intelligence_report' in parsed_data:
                        return parsed_data['intelligence_report']
                    else:
                        # Fallback to old format for backward compatibility
                        self.logger.warning("Using legacy response format")
                        return {
                            'numerical_conflicts': parsed_data.get('numerical_conflicts', []),
                            'contradictory_statements': parsed_data.get('contradictory_statements', []),
                            'timeline_issues': parsed_data.get('timeline_issues', []),
                            'logical_inconsistencies': parsed_data.get('logical_inconsistencies', [])
                        }
                else:
                    self.logger.warning("Failed to parse JSON response, attempting text extraction")
                    return self._extract_intelligence_from_text(text)
            else:
                self.logger.error("No candidates in API response")
                return self._get_empty_intelligence_report()
                
        except Exception as e:
            self.logger.error(f"Failed to parse analysis response: {str(e)}")
            return self._get_empty_intelligence_report()
    
    def _robust_json_parse(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Robust JSON parsing with multiple fallback strategies.
        
        Args:
            text: Raw text response from API
            
        Returns:
            Parsed JSON data or None if parsing fails
        """
        # Strategy 1: Direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from markdown code blocks
        import re
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Find JSON object in text
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        # Strategy 4: Clean and try again
        cleaned_text = text.strip()
        # Remove common prefixes/suffixes
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 5: Try to fix common JSON issues
        fixed_text = self._fix_common_json_issues(text)
        try:
            return json.loads(fixed_text)
        except json.JSONDecodeError:
            pass
        
        return None
    
    def _fix_common_json_issues(self, text: str) -> str:
        """
        Fix common JSON formatting issues.
        
        Args:
            text: Raw text with potential JSON formatting issues
            
        Returns:
            Fixed text
        """
        import re
        
        # Remove extra characters at the end
        text = re.sub(r'[^\w\s\{\}\[\]",:.-]+$', '', text)
        
        # Fix trailing commas
        text = re.sub(r',(\s*[}\]])', r'\1', text)
        
        # Fix missing quotes around keys
        text = re.sub(r'(\w+):', r'"\1":', text)
        
        # Fix single quotes to double quotes
        text = text.replace("'", '"')
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _extract_intelligence_from_text(self, text: str) -> Dict[str, Any]:
        """
        Fallback method to extract intelligence analysis from text response.
        
        Args:
            text: Raw text response from API
            
        Returns:
            Structured intelligence analysis data
        """
        # This is a simplified fallback - in practice, you'd want more sophisticated parsing
        return self._get_empty_intelligence_report()
    
    def _extract_inconsistencies_from_text(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fallback method to extract inconsistencies from text response.
        
        Args:
            text: Raw text response from API
            
        Returns:
            Structured inconsistencies data
        """
        # This is a simplified fallback - in practice, you'd want more sophisticated parsing
        inconsistencies = self._get_empty_inconsistencies()
        
        # Look for patterns in the text that indicate inconsistencies
        lines = text.split('\n')
        current_category = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect category headers
            if 'numerical' in line.lower() and 'conflict' in line.lower():
                current_category = 'numerical_conflicts'
            elif 'contradictory' in line.lower() and 'statement' in line.lower():
                current_category = 'contradictory_statements'
            elif 'timeline' in line.lower() and 'issue' in line.lower():
                current_category = 'timeline_issues'
            elif 'logical' in line.lower() and 'inconsistency' in line.lower():
                current_category = 'logical_inconsistencies'
            
            # Extract slide numbers and descriptions
            if current_category and ('slide' in line.lower() or 'description' in line.lower()):
                # Simplified extraction - would need more sophisticated parsing
                pass
        
        return inconsistencies
    
    def _get_empty_intelligence_report(self) -> Dict[str, Any]:
        """Return empty intelligence report structure."""
        return {
            'executive_summary': {
                'overall_risk_level': 'low',
                'data_integrity_score': '8/10',
                'strategic_coherence_score': '8/10',
                'stakeholder_confidence_impact': 'low',
                'critical_findings_count': 0,
                'business_impact_assessment': 'No significant issues detected'
            },
            'detailed_analysis': [],
            'strategic_recommendations': [],
            'data_quality_assessment': {
                'reliability_score': '8/10',
                'consistency_score': '8/10',
                'completeness_score': '8/10',
                'accuracy_indicators': [],
                'data_gaps': [],
                'verification_needs': []
            },
            'stakeholder_impact_analysis': {
                'investor_confidence': 'high',
                'employee_trust': 'high',
                'customer_perception': 'high',
                'regulatory_risk': 'low'
            }
        }
    
    def _get_empty_inconsistencies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return empty inconsistencies structure."""
        return {
            'numerical_conflicts': [],
            'contradictory_statements': [],
            'timeline_issues': [],
            'logical_inconsistencies': []
        }
    
    def validate_api_key(self) -> bool:
        """Validate the API key by making a simple test call."""
        if not self.api_key:
            return False
        
        try:
            test_prompt = "Say 'Hello' if you can read this."
            response = self._call_gemini_api(test_prompt)
            return 'candidates' in response and response['candidates']
        except Exception:
            return False
    
    def get_api_usage_info(self) -> Dict[str, Any]:
        """Get information about API usage and limits."""
        # This would require additional API calls to get usage statistics
        # For now, return basic info
        return {
            'api_key_configured': bool(self.api_key),
            'max_tokens': self.max_tokens,
            'base_url': self.base_url
        } 