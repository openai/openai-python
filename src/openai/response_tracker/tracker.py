"""
Response Knowledge Tracker
Tracks and evaluates AI response quality
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import time

class ResponseQuality:
    """Response quality assessment"""
    def __init__(self, response_id: str, content: str):
        self.response_id = response_id
        self.content = content
        self.timestamp = time.time()
        self.metrics: Dict[str, float] = {}
        self.feedback: List[Dict] = []
        self.confidence = 0.5
    
    def add_feedback(self, feedback_type: str, value: float, note: Optional[str] = None):
        """Add user feedback"""
        self.feedback.append({
            'type': feedback_type,
            'value': value,
            'note': note,
            'timestamp': time.time()
        })
        self._recalculate_confidence()
    
    def _recalculate_confidence(self):
        """Recalculate confidence based on feedback"""
        if not self.feedback:
            return
        
        values = [f['value'] for f in self.feedback]
        self.confidence = sum(values) / len(values)
    
    def get_metrics(self) -> Dict[str, float]:
        """Get quality metrics"""
        return {
            'confidence': self.confidence,
            'feedback_count': len(self.feedback),
            'age': time.time() - self.timestamp
        }

class ResponseTracker:
    """
    Tracks AI responses and their quality over time.
    Enables knowledge accumulation and confidence tracking.
    """
    
    def __init__(self):
        self.responses: Dict[str, ResponseQuality] = {}
        self.model_stats: Dict[str, Dict] = {}
    
    def track(self, response_id: str, content: str, model: str) -> ResponseQuality:
        """Track a new response"""
        quality = ResponseQuality(response_id, content)
        self.responses[response_id] = quality
        
        # Update model stats
        if model not in self.model_stats:
            self.model_stats[model] = {
                'count': 0,
                'avg_confidence': 0.0,
                'total_confidence': 0.0
            }
        
        stats = self.model_stats[model]
        stats['count'] += 1
        stats['total_confidence'] += quality.confidence
        stats['avg_confidence'] = stats['total_confidence'] / stats['count']
        
        return quality
    
    def add_feedback(self, response_id: str, feedback_type: str, 
                   value: float, note: Optional[str] = None) -> bool:
        """Add feedback to a response"""
        if response_id not in self.responses:
            return False
        
        self.responses[response_id].add_feedback(feedback_type, value, note)
        return True
    
    def get_response(self, response_id: str) -> Optional[ResponseQuality]:
        """Get response quality"""
        return self.responses.get(response_id)
    
    def get_model_stats(self, model: str) -> Optional[Dict]:
        """Get model statistics"""
        return self.model_stats.get(model)
    
    def get_high_confidence_responses(self, threshold: float = 0.8) -> List[ResponseQuality]:
        """Get responses above confidence threshold"""
        return [
            r for r in self.responses.values()
            if r.confidence >= threshold
        ]
    
    def get_all_stats(self) -> Dict:
        """Get overall statistics"""
        return {
            'total_responses': len(self.responses),
            'models': self.model_stats,
            'high_confidence_count': len(self.get_high_confidence_responses())
        }
