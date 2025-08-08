"""
Output formatting for inconsistency detection results.
"""

import yaml
import logging
from typing import Dict, List, Any
from datetime import datetime

from utils.helpers import format_duration


class OutputFormatter:
    """Formats inconsistency detection results in various output formats."""
    
    def __init__(self):
        """Initialize the output formatter."""
        self.logger = logging.getLogger(__name__)
    
    def format_results(self, results: Dict[str, Any], output_format: str = 'yaml', 
                      analysis_time: float = 0.0) -> str:
        """
        Format results in the specified output format.
        
        Args:
            results: Analysis results
            output_format: Desired output format ('yaml', 'markdown', 'text')
            analysis_time: Time taken for analysis in seconds
            
        Returns:
            Formatted output string
        """
        # Check if this is intelligence-level analysis
        if 'executive_summary' in results:
            return self._format_intelligence_report(results, output_format, analysis_time)
        else:
            # Legacy format
            if output_format.lower() == 'yaml':
                return self._format_yaml(results, analysis_time)
            elif output_format.lower() == 'markdown':
                return self._format_markdown(results, analysis_time)
            elif output_format.lower() == 'text':
                return self._format_text(results, analysis_time)
            else:
                self.logger.warning(f"Unknown output format: {output_format}. Using YAML.")
                return self._format_yaml(results, analysis_time)
    
    def _format_yaml(self, results: Dict[str, Any], analysis_time: float) -> str:
        """Format results as YAML."""
        try:
            # Prepare data for YAML output
            yaml_data = {
                'analysis_info': {
                    'timestamp': datetime.now().isoformat(),
                    'analysis_time': format_duration(analysis_time),
                    'tool_version': 'SlideSage v1.0'
                },
                'summary': results.get('summary', {}),
                'inconsistencies': results.get('inconsistencies', {})
            }
            
            # Convert to YAML string
            yaml_output = yaml.dump(yaml_data, default_flow_style=False, indent=2, 
                                  allow_unicode=True, sort_keys=False)
            
            return yaml_output
            
        except Exception as e:
            self.logger.error(f"Failed to format YAML output: {str(e)}")
            return f"Error formatting output: {str(e)}"
    
    def _format_markdown(self, results: Dict[str, Any], analysis_time: float) -> str:
        """Format results as Markdown."""
        try:
            lines = []
            
            # Header
            lines.append("# SlideSage Analysis Report")
            lines.append("")
            lines.append(f"**Analysis completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**Analysis time:** {format_duration(analysis_time)}")
            lines.append("")
            
            # Summary
            summary = results.get('summary', {})
            lines.append("## Summary")
            lines.append("")
            lines.append(f"- **Total slides analyzed:** {summary.get('total_slides', 0)}")
            lines.append(f"- **Inconsistencies found:** {summary.get('inconsistencies_found', 0)}")
            lines.append("")
            
            # Severity breakdown
            severity_breakdown = summary.get('severity_breakdown', {})
            if severity_breakdown:
                lines.append("### Severity Breakdown")
                lines.append("")
                for severity, count in severity_breakdown.items():
                    lines.append(f"- **{severity.title()}:** {count}")
                lines.append("")
            
            # Category breakdown
            category_breakdown = summary.get('category_breakdown', {})
            if category_breakdown:
                lines.append("### Category Breakdown")
                lines.append("")
                for category, count in category_breakdown.items():
                    lines.append(f"- **{category.replace('_', ' ').title()}:** {count}")
                lines.append("")
            
            # Inconsistencies
            inconsistencies = results.get('inconsistencies', {})
            if any(inconsistencies.values()):
                lines.append("## Detected Inconsistencies")
                lines.append("")
                
                for category, items in inconsistencies.items():
                    if items:
                        lines.append(f"### {category.replace('_', ' ').title()}")
                        lines.append("")
                        
                        for i, item in enumerate(items, 1):
                            slide_nums = item.get('slide_numbers', [])
                            description = item.get('description', '')
                            severity = item.get('severity', 'unknown')
                            
                            lines.append(f"#### {i}. {description}")
                            lines.append("")
                            lines.append(f"- **Slides:** {', '.join(map(str, slide_nums))}")
                            lines.append(f"- **Severity:** {severity.title()}")
                            lines.append("")
            else:
                lines.append("## No Inconsistencies Found")
                lines.append("")
                lines.append("✅ No inconsistencies were detected in the presentation.")
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Failed to format Markdown output: {str(e)}")
            return f"Error formatting output: {str(e)}"
    
    def _format_text(self, results: Dict[str, Any], analysis_time: float) -> str:
        """Format results as plain text."""
        try:
            lines = []
            
            # Header
            lines.append("=" * 60)
            lines.append("SLIDESAGE ANALYSIS REPORT")
            lines.append("=" * 60)
            lines.append("")
            lines.append(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Analysis time: {format_duration(analysis_time)}")
            lines.append("")
            
            # Summary
            summary = results.get('summary', {})
            lines.append("SUMMARY")
            lines.append("-" * 20)
            lines.append(f"Total slides analyzed: {summary.get('total_slides', 0)}")
            lines.append(f"Inconsistencies found: {summary.get('inconsistencies_found', 0)}")
            lines.append("")
            
            # Severity breakdown
            severity_breakdown = summary.get('severity_breakdown', {})
            if severity_breakdown:
                lines.append("Severity Breakdown:")
                for severity, count in severity_breakdown.items():
                    lines.append(f"  {severity.title()}: {count}")
                lines.append("")
            
            # Category breakdown
            category_breakdown = summary.get('category_breakdown', {})
            if category_breakdown:
                lines.append("Category Breakdown:")
                for category, count in category_breakdown.items():
                    lines.append(f"  {category.replace('_', ' ').title()}: {count}")
                lines.append("")
            
            # Inconsistencies
            inconsistencies = results.get('inconsistencies', {})
            if any(inconsistencies.values()):
                lines.append("DETECTED INCONSISTENCIES")
                lines.append("=" * 30)
                lines.append("")
                
                for category, items in inconsistencies.items():
                    if items:
                        lines.append(f"{category.replace('_', ' ').upper()}")
                        lines.append("-" * len(category.replace('_', ' ')))
                        lines.append("")
                        
                        for i, item in enumerate(items, 1):
                            slide_nums = item.get('slide_numbers', [])
                            description = item.get('description', '')
                            severity = item.get('severity', 'unknown')
                            
                            lines.append(f"{i}. {description}")
                            lines.append(f"   Slides: {', '.join(map(str, slide_nums))}")
                            lines.append(f"   Severity: {severity.title()}")
                            lines.append("")
            else:
                lines.append("NO INCONSISTENCIES FOUND")
                lines.append("=" * 25)
                lines.append("")
                lines.append("✅ No inconsistencies were detected in the presentation.")
                lines.append("")
            
            lines.append("=" * 60)
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Failed to format text output: {str(e)}")
            return f"Error formatting output: {str(e)}"
    
    def format_error(self, error_message: str, output_format: str = 'text') -> str:
        """
        Format error messages in the specified output format.
        
        Args:
            error_message: Error message to format
            output_format: Desired output format
            
        Returns:
            Formatted error message
        """
        if output_format.lower() == 'yaml':
            error_data = {
                'error': {
                    'message': error_message,
                    'timestamp': datetime.now().isoformat()
                }
            }
            return yaml.dump(error_data, default_flow_style=False, indent=2)
        
        elif output_format.lower() == 'markdown':
            return f"# Error\n\n**{error_message}**\n\n*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        else:  # text format
            lines = [
                "ERROR",
                "=" * 20,
                error_message,
                "",
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            return "\n".join(lines)
    
    def _format_intelligence_report(self, results: Dict[str, Any], output_format: str, analysis_time: float) -> str:
        """
        Format intelligence-level analysis results.
        
        Args:
            results: Intelligence analysis results
            output_format: Desired output format
            analysis_time: Time taken for analysis
            
        Returns:
            Formatted intelligence report
        """
        if output_format.lower() == 'yaml':
            return self._format_intelligence_yaml(results, analysis_time)
        elif output_format.lower() == 'markdown':
            return self._format_intelligence_markdown(results, analysis_time)
        else:
            return self._format_intelligence_text(results, analysis_time)
    
    def _format_intelligence_yaml(self, results: Dict[str, Any], analysis_time: float) -> str:
        """Format intelligence report as YAML."""
        try:
            yaml_data = {
                'intelligence_report': {
                    'analysis_info': {
                        'timestamp': datetime.now().isoformat(),
                        'analysis_time': format_duration(analysis_time),
                        'tool_version': 'SlideSage Intelligence v2.0'
                    },
                    'executive_summary': results.get('executive_summary', {}),
                    'detailed_analysis': results.get('detailed_analysis', []),
                    'strategic_recommendations': results.get('strategic_recommendations', []),
                    'data_quality_assessment': results.get('data_quality_assessment', {}),
                    'stakeholder_impact_analysis': results.get('stakeholder_impact_analysis', {})
                }
            }
            
            return yaml.dump(yaml_data, default_flow_style=False, indent=2, 
                           allow_unicode=True, sort_keys=False)
            
        except Exception as e:
            self.logger.error(f"Failed to format intelligence YAML: {str(e)}")
            return f"Error formatting intelligence output: {str(e)}"
    
    def _format_intelligence_markdown(self, results: Dict[str, Any], analysis_time: float) -> str:
        """Format intelligence report as Markdown."""
        try:
            lines = []
            
            # Header
            lines.append("# 🎯 SlideSage Intelligence Report")
            lines.append("")
            lines.append(f"**Analysis completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**Analysis time:** {format_duration(analysis_time)}")
            lines.append("")
            
            # Executive Summary
            summary = results.get('executive_summary', {})
            lines.append("## 📊 Executive Summary")
            lines.append("")
            lines.append(f"- **Overall Risk Level:** {summary.get('overall_risk_level', 'unknown').title()}")
            lines.append(f"- **Data Integrity Score:** {summary.get('data_integrity_score', 'N/A')}")
            lines.append(f"- **Strategic Coherence Score:** {summary.get('strategic_coherence_score', 'N/A')}")
            lines.append(f"- **Stakeholder Confidence Impact:** {summary.get('stakeholder_confidence_impact', 'unknown').title()}")
            lines.append(f"- **Critical Findings:** {summary.get('critical_findings_count', 0)}")
            lines.append("")
            lines.append(f"**Business Impact Assessment:** {summary.get('business_impact_assessment', 'N/A')}")
            lines.append("")
            
            # Detailed Analysis
            detailed_analysis = results.get('detailed_analysis', [])
            if detailed_analysis:
                lines.append("## 🔍 Detailed Intelligence Analysis")
                lines.append("")
                
                for i, analysis in enumerate(detailed_analysis, 1):
                    category = analysis.get('category', 'unknown').title()
                    severity = analysis.get('severity', 'unknown').title()
                    slides = analysis.get('slides', [])
                    description = analysis.get('detailed_description', '')
                    impact = analysis.get('business_impact', '')
                    insights = analysis.get('intelligence_insights', '')
                    recommendations = analysis.get('recommended_actions', [])
                    
                    lines.append(f"### {i}. {category} Issue - {severity} Severity")
                    lines.append("")
                    lines.append(f"**Slides:** {', '.join(map(str, slides))}")
                    lines.append("")
                    lines.append(f"**Description:** {description}")
                    lines.append("")
                    lines.append(f"**Business Impact:** {impact}")
                    lines.append("")
                    lines.append(f"**Intelligence Insights:** {insights}")
                    lines.append("")
                    
                    if recommendations:
                        lines.append("**Recommended Actions:**")
                        for rec in recommendations:
                            lines.append(f"- {rec}")
                        lines.append("")
            else:
                lines.append("## ✅ No Critical Issues Detected")
                lines.append("")
                lines.append("The presentation shows good consistency and data integrity.")
                lines.append("")
            
            # Strategic Recommendations
            strategic_recs = results.get('strategic_recommendations', [])
            if strategic_recs:
                lines.append("## 🎯 Strategic Recommendations")
                lines.append("")
                
                for i, rec in enumerate(strategic_recs, 1):
                    priority = rec.get('priority', 'unknown').title()
                    action = rec.get('action', '')
                    rationale = rec.get('rationale', '')
                    outcome = rec.get('expected_outcome', '')
                    
                    lines.append(f"### {i}. {priority} Priority")
                    lines.append("")
                    lines.append(f"**Action:** {action}")
                    lines.append("")
                    lines.append(f"**Rationale:** {rationale}")
                    lines.append("")
                    lines.append(f"**Expected Outcome:** {outcome}")
                    lines.append("")
            
            # Data Quality Assessment
            data_quality = results.get('data_quality_assessment', {})
            if data_quality:
                lines.append("## 📈 Data Quality Assessment")
                lines.append("")
                lines.append(f"- **Reliability Score:** {data_quality.get('reliability_score', 'N/A')}")
                lines.append(f"- **Consistency Score:** {data_quality.get('consistency_score', 'N/A')}")
                lines.append(f"- **Completeness Score:** {data_quality.get('completeness_score', 'N/A')}")
                lines.append("")
                
                accuracy_indicators = data_quality.get('accuracy_indicators', [])
                if accuracy_indicators:
                    lines.append("**Accuracy Concerns:**")
                    for indicator in accuracy_indicators:
                        lines.append(f"- {indicator}")
                    lines.append("")
                
                data_gaps = data_quality.get('data_gaps', [])
                if data_gaps:
                    lines.append("**Data Gaps:**")
                    for gap in data_gaps:
                        lines.append(f"- {gap}")
                    lines.append("")
            
            # Stakeholder Impact
            stakeholder_impact = results.get('stakeholder_impact_analysis', {})
            if stakeholder_impact:
                lines.append("## 👥 Stakeholder Impact Analysis")
                lines.append("")
                lines.append(f"- **Investor Confidence:** {stakeholder_impact.get('investor_confidence', 'unknown').title()}")
                lines.append(f"- **Employee Trust:** {stakeholder_impact.get('employee_trust', 'unknown').title()}")
                lines.append(f"- **Customer Perception:** {stakeholder_impact.get('customer_perception', 'unknown').title()}")
                lines.append(f"- **Regulatory Risk:** {stakeholder_impact.get('regulatory_risk', 'unknown').title()}")
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Failed to format intelligence Markdown: {str(e)}")
            return f"Error formatting intelligence output: {str(e)}"
    
    def _format_intelligence_text(self, results: Dict[str, Any], analysis_time: float) -> str:
        """Format intelligence report as plain text."""
        try:
            lines = []
            
            # Header
            lines.append("=" * 80)
            lines.append("🎯 SLIDESAGE INTELLIGENCE REPORT")
            lines.append("=" * 80)
            lines.append("")
            lines.append(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Analysis time: {format_duration(analysis_time)}")
            lines.append("")
            
            # Executive Summary
            summary = results.get('executive_summary', {})
            lines.append("📊 EXECUTIVE SUMMARY")
            lines.append("-" * 30)
            lines.append(f"Overall Risk Level: {summary.get('overall_risk_level', 'unknown').title()}")
            lines.append(f"Data Integrity Score: {summary.get('data_integrity_score', 'N/A')}")
            lines.append(f"Strategic Coherence Score: {summary.get('strategic_coherence_score', 'N/A')}")
            lines.append(f"Stakeholder Confidence Impact: {summary.get('stakeholder_confidence_impact', 'unknown').title()}")
            lines.append(f"Critical Findings: {summary.get('critical_findings_count', 0)}")
            lines.append("")
            lines.append(f"Business Impact Assessment: {summary.get('business_impact_assessment', 'N/A')}")
            lines.append("")
            
            # Detailed Analysis
            detailed_analysis = results.get('detailed_analysis', [])
            if detailed_analysis:
                lines.append("🔍 DETAILED INTELLIGENCE ANALYSIS")
                lines.append("=" * 50)
                lines.append("")
                
                for i, analysis in enumerate(detailed_analysis, 1):
                    category = analysis.get('category', 'unknown').title()
                    severity = analysis.get('severity', 'unknown').title()
                    slides = analysis.get('slides', [])
                    description = analysis.get('detailed_description', '')
                    impact = analysis.get('business_impact', '')
                    insights = analysis.get('intelligence_insights', '')
                    recommendations = analysis.get('recommended_actions', [])
                    
                    lines.append(f"{i}. {category} ISSUE - {severity} SEVERITY")
                    lines.append(f"   Slides: {', '.join(map(str, slides))}")
                    lines.append("")
                    lines.append(f"   Description: {description}")
                    lines.append("")
                    lines.append(f"   Business Impact: {impact}")
                    lines.append("")
                    lines.append(f"   Intelligence Insights: {insights}")
                    lines.append("")
                    
                    if recommendations:
                        lines.append("   Recommended Actions:")
                        for rec in recommendations:
                            lines.append(f"   - {rec}")
                        lines.append("")
            else:
                lines.append("✅ NO CRITICAL ISSUES DETECTED")
                lines.append("=" * 35)
                lines.append("")
                lines.append("The presentation shows good consistency and data integrity.")
                lines.append("")
            
            # Strategic Recommendations
            strategic_recs = results.get('strategic_recommendations', [])
            if strategic_recs:
                lines.append("🎯 STRATEGIC RECOMMENDATIONS")
                lines.append("=" * 35)
                lines.append("")
                
                for i, rec in enumerate(strategic_recs, 1):
                    priority = rec.get('priority', 'unknown').title()
                    action = rec.get('action', '')
                    rationale = rec.get('rationale', '')
                    outcome = rec.get('expected_outcome', '')
                    
                    lines.append(f"{i}. {priority} PRIORITY")
                    lines.append(f"   Action: {action}")
                    lines.append(f"   Rationale: {rationale}")
                    lines.append(f"   Expected Outcome: {outcome}")
                    lines.append("")
            
            # Data Quality Assessment
            data_quality = results.get('data_quality_assessment', {})
            if data_quality:
                lines.append("📈 DATA QUALITY ASSESSMENT")
                lines.append("-" * 30)
                lines.append(f"Reliability Score: {data_quality.get('reliability_score', 'N/A')}")
                lines.append(f"Consistency Score: {data_quality.get('consistency_score', 'N/A')}")
                lines.append(f"Completeness Score: {data_quality.get('completeness_score', 'N/A')}")
                lines.append("")
            
            # Stakeholder Impact
            stakeholder_impact = results.get('stakeholder_impact_analysis', {})
            if stakeholder_impact:
                lines.append("👥 STAKEHOLDER IMPACT ANALYSIS")
                lines.append("-" * 35)
                lines.append(f"Investor Confidence: {stakeholder_impact.get('investor_confidence', 'unknown').title()}")
                lines.append(f"Employee Trust: {stakeholder_impact.get('employee_trust', 'unknown').title()}")
                lines.append(f"Customer Perception: {stakeholder_impact.get('customer_perception', 'unknown').title()}")
                lines.append(f"Regulatory Risk: {stakeholder_impact.get('regulatory_risk', 'unknown').title()}")
                lines.append("")
            
            lines.append("=" * 80)
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Failed to format intelligence text: {str(e)}")
            return f"Error formatting intelligence output: {str(e)}"
    
    def format_progress(self, current: int, total: int, message: str = "") -> str:
        """
        Format progress information.
        
        Args:
            current: Current progress value
            total: Total value
            message: Optional message
            
        Returns:
            Formatted progress string
        """
        percentage = (current / total * 100) if total > 0 else 0
        progress_bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
        
        progress_text = f"[{progress_bar}] {percentage:.1f}% ({current}/{total})"
        
        if message:
            progress_text += f" - {message}"
        
        return progress_text 