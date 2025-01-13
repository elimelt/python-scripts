import os
import sys
from datetime import datetime
import subprocess
from crontab import CronTab
import logging
import json
from typing import List, Dict

class GitAutoCommitManager:
    def __init__(self, config_path: str = "repo_config.json"):
        self.config_path = config_path
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Configure logging for the application."""
        logger = logging.getLogger('GitAutoCommit')
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        file_handler = logging.FileHandler('git_auto_commit.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger

    def load_config(self) -> Dict:
        """Load repository configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_path}")
            return {"repositories": []}
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in config file: {self.config_path}")
            return {"repositories": []}

    def save_config(self, config: Dict) -> None:
        """Save repository configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)

    def add_repository(self, repo_path: str, commit_message: str = "Auto-commit", schedule: str = "0 * * * *") -> None:
        """Add a new repository to the auto-commit configuration."""
        if not os.path.isdir(repo_path):
            self.logger.error(f"Invalid repository path: {repo_path}")
            return

        if not os.path.isdir(os.path.join(repo_path, '.git')):
            self.logger.error(f"Not a git repository: {repo_path}")
            return

        config = self.load_config()
        
        for repo in config.get("repositories", []):
            if repo["path"] == repo_path:
                self.logger.warning(f"Repository already exists: {repo_path}")
                return

        config.setdefault("repositories", []).append({
            "path": repo_path,
            "commit_message": commit_message,
            "schedule": schedule
        })
        
        self.save_config(config)
        self.update_cron_jobs()
        self.logger.info(f"Added repository: {repo_path}")

    def remove_repository(self, repo_path: str) -> None:
        """Remove a repository from the auto-commit configuration."""
        config = self.load_config()
        config["repositories"] = [repo for repo in config.get("repositories", [])
                                if repo["path"] != repo_path]
        self.save_config(config)
        self.update_cron_jobs()
        self.logger.info(f"Removed repository: {repo_path}")

    def git_auto_commit(self, repo_path: str, commit_message: str) -> None:
        """Perform git add and commit for a repository."""
        try:
            os.chdir(repo_path)
            
            status = subprocess.run(['git', 'status', '--porcelain'],
                                 capture_output=True, text=True)
            
            if not status.stdout.strip():
                self.logger.info(f"No changes to commit in {repo_path}")
                return

            subprocess.run(['git', 'add', '.'], check=True)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_message = f"{commit_message} - {timestamp}"
            subprocess.run(['git', 'commit', '-m', full_message], check=True)
            
            subprocess.run(['git', 'push'], check=True)

            self.logger.info(f"Successfully committed changes in {repo_path}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed in {repo_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error processing repository {repo_path}: {str(e)}")

    def update_cron_jobs(self) -> None:
        """Update cron jobs for all configured repositories."""
        try:
            cron = CronTab(user=True)
            
            cron.remove_all(comment='git-auto-commit')
            
            config = self.load_config()
            script_path = os.path.abspath(__file__)
            
            for repo in config.get("repositories", []):
                job = cron.new(command=f'/usr/bin/python3 {script_path} commit "{repo["path"]}"',
                             comment='git-auto-commit')
                job.setall(repo["schedule"])
            
            cron.write()
            self.logger.info("Cron jobs updated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to update cron jobs: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Add repository:    python script.py add <repo_path> [commit_message] [schedule]")
        print("  Remove repository: python script.py remove <repo_path>")
        print("  Commit changes:    python script.py commit <repo_path>")
        sys.exit(1)

    manager = GitAutoCommitManager()
    command = sys.argv[1]

    if command == "add" and len(sys.argv) >= 3:
        repo_path = os.path.abspath(sys.argv[2])
        commit_message = sys.argv[3] if len(sys.argv) > 3 else "Auto-commit"
        schedule = sys.argv[4] if len(sys.argv) > 4 else "0 * * * *"
        manager.add_repository(repo_path, commit_message, schedule)
        
    elif command == "remove" and len(sys.argv) == 3:
        repo_path = os.path.abspath(sys.argv[2])
        manager.remove_repository(repo_path)
        
    elif command == "commit" and len(sys.argv) == 3:
        repo_path = os.path.abspath(sys.argv[2])
        config = manager.load_config()
        for repo in config.get("repositories", []):
            if repo["path"] == repo_path:
                manager.git_auto_commit(repo_path, repo["commit_message"])
                break

if __name__ == "__main__":
    main()
