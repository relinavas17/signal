"""
Optional Resume Analyzer Agent using Phidata
Provides AI-powered fit explanations for candidates
"""

import os
from typing import Dict, List, Optional
import json
import logging

# Try to import phidata, but make it optional
try:
    from phi.agent import Agent
    from phi.model.openai import OpenAIChat
    from phi.tools.duckduckgo import DuckDuckGoSearch
    PHIDATA_AVAILABLE = True
except ImportError:
    PHIDATA_AVAILABLE = False
    Agent = None
    OpenAIChat = None
    DuckDuckGoSearch = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeAnalyzerAgent:
    """Agent for analyzing candidate fit and generating explanations"""
    
    def __init__(self):
        self.enabled = os.getenv("PHIDATA_ENABLED", "false").lower() == "true"
        self.model = os.getenv("AGENT_MODEL", "gpt-4o")
        
        if self.enabled and PHIDATA_AVAILABLE:
            self.agent = Agent(
                model=OpenAIChat(id=self.model),
                tools=[DuckDuckGoSearch()],
                instructions=[
                    "You are a professional HR analyst specializing in candidate assessment.",
                    "Analyze resumes and job requirements to provide structured fit assessments.",
                    "Focus on skills match, experience relevance, and potential gaps.",
                    "Provide actionable insights for recruiters.",
                    "Be concise but thorough in your analysis."
                ],
                show_tool_calls=False,
                markdown=True,
            )
        else:
            self.agent = None
    
    def analyze_candidate_fit(
        self, 
        resume_text: str, 
        query: str, 
        candidate_name: str
    ) -> Optional[Dict]:
        """
        Analyze candidate fit against a search query/job requirement
        
        Args:
            resume_text: The candidate's resume content
            query: The search query or job requirement
            candidate_name: Name of the candidate
            
        Returns:
            Dictionary with fit analysis or None if agent is disabled
        """
        if not self.enabled or not PHIDATA_AVAILABLE:
            if not PHIDATA_AVAILABLE:
                logger.info("Phidata not available - Resume Analyzer Agent disabled")
            else:
                logger.info("Resume Analyzer Agent is disabled")
            return None
            
        try:
            prompt = f"""
            Analyze the following candidate's fit for the given requirement:
            
            **Candidate:** {candidate_name}
            **Requirement:** {query}
            
            **Resume:**
            {resume_text}
            
            Please provide a structured analysis in the following JSON format:
            {{
                "summary": "Brief 2-3 sentence summary of candidate fit",
                "top_skills_matched": ["skill1", "skill2", "skill3"],
                "experience_relevance": "Brief assessment of relevant experience",
                "potential_gaps": ["gap1", "gap2"],
                "fit_percentage": 85,
                "recommendation": "hire/consider/pass with brief reason"
            }}
            
            Focus on:
            1. Skills alignment with the requirement
            2. Experience level and relevance
            3. Any notable achievements or projects
            4. Potential areas for development
            5. Overall recommendation
            """
            
            response = self.agent.run(prompt)
            
            # Extract JSON from the response
            response_text = str(response)
            
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                try:
                    analysis = json.loads(json_str)
                    logger.info(f"Successfully analyzed candidate {candidate_name}")
                    return analysis
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response for {candidate_name}")
                    return {
                        "summary": response_text[:200] + "...",
                        "top_skills_matched": [],
                        "experience_relevance": "Analysis available in summary",
                        "potential_gaps": [],
                        "fit_percentage": 50,
                        "recommendation": "review"
                    }
            else:
                logger.error(f"No JSON found in response for {candidate_name}")
                return {
                    "summary": response_text[:200] + "...",
                    "top_skills_matched": [],
                    "experience_relevance": "Analysis available in summary", 
                    "potential_gaps": [],
                    "fit_percentage": 50,
                    "recommendation": "review"
                }
                
        except Exception as e:
            logger.error(f"Error analyzing candidate {candidate_name}: {str(e)}")
            return None
    
    def generate_fit_explanation(self, analysis: Dict) -> str:
        """
        Generate a human-readable fit explanation from analysis
        
        Args:
            analysis: The structured analysis dictionary
            
        Returns:
            Formatted explanation string
        """
        if not analysis:
            return "Analysis not available"
            
        explanation = f"""**Summary:** {analysis.get('summary', 'No summary available')}

**Key Skills Matched:**
{chr(10).join(f"• {skill}" for skill in analysis.get('top_skills_matched', []))}

**Experience Relevance:** {analysis.get('experience_relevance', 'Not assessed')}

**Potential Development Areas:**
{chr(10).join(f"• {gap}" for gap in analysis.get('potential_gaps', []))}

**Fit Score:** {analysis.get('fit_percentage', 0)}%

**Recommendation:** {analysis.get('recommendation', 'Review required').title()}
"""
        
        return explanation

# Global instance
resume_analyzer = ResumeAnalyzerAgent()

def analyze_candidate_fit(resume_text: str, query: str, candidate_name: str) -> Optional[str]:
    """
    Convenience function to analyze candidate fit and return explanation
    
    Args:
        resume_text: The candidate's resume content
        query: The search query or job requirement  
        candidate_name: Name of the candidate
        
    Returns:
        Formatted fit explanation or None
    """
    analysis = resume_analyzer.analyze_candidate_fit(resume_text, query, candidate_name)
    if analysis:
        return resume_analyzer.generate_fit_explanation(analysis)
    return None
