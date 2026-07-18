from typing import List, Dict, Any
from app.config import regression_service

def search_bug(query: str) -> List[Dict[str, Any]]:
    """
    Performs a semantic search over historical bug databases.
    """
    return regression_service.search_bug(query)

def similar_failures(failure_description: str) -> List[Dict[str, Any]]:
    """
    Searches the historical bug database to find bugs with similar failure symptoms, logs, or signals.
    """
    # Simply perform semantic search on the failure description
    return regression_service.search_bug(failure_description, top_k=3)

def regression_summary(run_id_a: str, run_id_b: str) -> Dict[str, Any]:
    """
    Compares two overnight regression runs and lists new failures, resolved failures, and runtime trends.
    """
    return regression_service.get_regression_summary(run_id_a, run_id_b)
