import subprocess
import os
from typing import List, Dict, Any, Optional

class GitConnector:
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir

    def _run_git(self, args: List[str]) -> str:
        try:
            # PAGER=cat is set automatically by the agent guidelines, but we can pass env just in case.
            env = os.environ.copy()
            env["PAGER"] = "cat"
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                env=env
            )
            return result.stdout
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            return ""

    def is_git_repo(self) -> bool:
        res = self._run_git(["rev-parse", "--is-inside-work-tree"])
        return res.strip() == "true"

    def search_commits(self, file_path: str, max_count: int = 5) -> List[Dict[str, Any]]:
        """
        Finds commits affecting the specified file.
        """
        output = self._run_git([
            "log", 
            f"-n {max_count}", 
            "--pretty=format:%H|%an|%ad|%s", 
            "--date=short", 
            "--", 
            file_path
        ])
        
        commits = []
        if not output:
            return commits

        for line in output.strip().split("\n"):
            parts = line.split("|")
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3]
                })
        return commits

    def blame_signal(self, file_path: str, signal_name: str) -> List[Dict[str, Any]]:
        """
        Blames lines containing the signal name in the file.
        """
        # Find lines containing the signal first
        lines_containing_signal = []
        if not os.path.exists(os.path.join(self.repo_dir, file_path)):
            return []

        with open(os.path.join(self.repo_dir, file_path), 'r', errors='ignore') as f:
            for idx, line in enumerate(f, 1):
                if signal_name in line:
                    lines_containing_signal.append(idx)

        blame_info = []
        for line_num in lines_containing_signal:
            # git blame -L line,line file
            output = self._run_git(["blame", "-L", f"{line_num},{line_num}", "--", file_path])
            if output:
                blame_info.append({
                    "line_number": line_num,
                    "raw_blame": output.strip()
                })
        return blame_info

    def recent_changes(self, max_count: int = 5) -> List[Dict[str, Any]]:
        """
        Returns recent commits in the repository.
        """
        output = self._run_git([
            "log", 
            f"-n {max_count}", 
            "--pretty=format:%H|%an|%ad|%s", 
            "--date=short"
        ])
        
        commits = []
        if not output:
            return commits

        for line in output.strip().split("\n"):
            parts = line.split("|")
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "subject": parts[3]
                })
        return commits
