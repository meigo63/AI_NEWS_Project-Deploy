import os
import logging
import re
from typing import Tuple, Optional, Dict
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google Gemini API for factual verification."""
    
    def __init__(self):
        """Initialize Gemini service."""
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
       
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_article_comprehensive(self, article_text: str) -> Dict[str, str]:
        """طلب التصنيف والملخص والتحليل في طلب واحد."""
        try:
            prompt = f"""Act as a professional Fact-Checker. Analyze the following news article:
            
            ARTICLE: "{article_text}"
            
            Please provide your response in this EXACT format:
            VERDICT: [Either 'REAL' or 'FAKE']
            SUMMARY: [Provide 3-5 bullet points]
            EXPLANATION: [A brief explanation of your factual reasoning]
            """
            
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                return None
            
            res_text = response.text
            
            return {
                'verdict': self._extract_section(res_text, "VERDICT").upper(),
                'summary': self._extract_section(res_text, "SUMMARY"),
                'explanation': self._extract_section(res_text, "EXPLANATION")
            }
        except Exception as e:
            logger.error(f"Gemini Comprehensive Error: {str(e)}")
            return None

    def generate_explanation(
        self, 
        article_text: str, 
        prediction_label: str, 
        confidence_score: float
    ) -> Tuple[str, str, str]:
        """دالة التوافق مع الكود القديم لضمان عدم تعطل النظام."""
        try:
            res = self.analyze_article_comprehensive(article_text)
            if res:
                return res['summary'], res['explanation'], f"Gemini verdict: {res['verdict']}"
            
            return "No summary available", "Verification service failed.", "N/A"
        except Exception as e:
            logger.error(f"Gemini Error: {str(e)}")
            return "Error", f"Service unavailable: {str(e)}", "Error"

    def _extract_section(self, text: str, section_name: str) -> str:
        """استخراج الأقسام باستخدام Regex بدقة عالية."""
        pattern = rf"{section_name}:\s*(.*?)(?=VERDICT:|SUMMARY:|EXPLANATION:|$)"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def should_verify(self, confidence_score: float) -> bool:
        """تفعيل Gemini تلقائياً إذا كانت الثقة أقل من 80%."""
        return confidence_score < 80