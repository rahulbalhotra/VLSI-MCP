from typing import List, Dict, Any
from app.config import git_connector

def search_commits(file_path: str, max_count: int = 5) -> List[Dict[str, Any]]:
    """
    Finds commits affecting the specified file.
    """
    return git_connector.search_commits(file_path, max_count)

def blame_signal(file_path: str, signal_name: str) -> List[Dict[str, Any]]:
    """
    Identifies which commits modified the lines containing the specified signal.
    """
    return git_connector.blame_signal(file_path, signal_name)

def recent_changes(max_count: int = 5) -> List[Dict[str, Any]]:
    """
    Returns the latest modifications/commits in the repository.
    """
    return git_connector.recent_changes(max_count)
