from typing import Dict, Any, List, Set

class HeuristicGuard:
    """
    Filtre heuristique pour requêtes LLM en Français.
    """
    
    OPERANTS: Set[str] = {
        'donne', 'fais', 'analyse', 'génère', 'genere', 'calcule', 
        'audit', 'verdict', 'système', 'crée', 'cree', 'optimise', 
        'explique', 'compare', 'résume', 'resume', 'évalue', 'evalue', 
        'teste', 'montre', 'prouve', 'liste', 'décris', 'decris', 'generate'
    }
    
    FORMATS: Set[str] = {
        'json', 'tableau', 'liste', 'markdown', 'csv', 'expert', 
        'physique', 'code', 'python', 'sql'
    }

    THRESH_OPTIMAL: float = 2.3
    THRESH_ADMISSIBLE: float = 1.0

    @classmethod
    def analyze(cls, prompt: str) -> Dict[str, Any]:
        prompt = prompt.strip()
        if len(prompt) < 3:
            return {"S": 0.0, "verdict": "INCOHERENCE", "valid": False}

        tokens: List[str] = prompt.lower().split()
        t_len: int = len(tokens)
        
        # Calcul de base
        beta: float = 1.0
        if t_len < 4: beta *= 0.6
        if t_len > 100: beta *= 0.85
        
        # Complexité sémantique (Sécurité contre division par zéro)
        complex_terms = len([t for t in tokens if len(t) > 7])
        if t_len > 0 and (complex_terms / t_len) > 0.4:
            beta *= 1.15
        
        # Calcul du gradient (deltaC)
        score_delta: float = 0.1
        if any(op in tokens for op in cls.OPERANTS): score_delta += 0.45
        if any(fmt in tokens for fmt in cls.FORMATS): score_delta += 0.35
        
        delta_c: float = min(1.0, score_delta + 0.1)
        lambda_val: float = max(0.08, 1.1 - (score_delta * 0.85))
        
        s_score: float = (beta * delta_c) / lambda_val
        
        # Verdict
        verdict: str = "INCOHERENCE"
        if s_score >= cls.THRESH_OPTIMAL: verdict = "OPTIMAL"
        elif s_score >= cls.THRESH_ADMISSIBLE: verdict = "ADMISSIBLE"
        
        return {
            "S": round(s_score, 2),
            "verdict": verdict,
            "valid": s_score >= cls.THRESH_ADMISSIBLE
        }