import os
import json
import subprocess
import requests
from pathlib import Path
""" 
Handler for cloud functionality
"""
def compare_versions(v1, v2):
    """
    Compare two version strings.
    Returns: -1 if v1 < v2, 0 if v1 == v2, 1 if v1 > v2
    """
    def parse_version(v):
        return [int(x) for x in v.split('.')]
    
    v1_parts = parse_version(v1)
    v2_parts = parse_version(v2)
    
    # Pad shorter version with zeros
    while len(v1_parts) < len(v2_parts):
        v1_parts.append(0)
    while len(v2_parts) < len(v1_parts):
        v2_parts.append(0)
    
    for i, j in zip(v1_parts, v2_parts):
        if i < j:
            return -1
        elif i > j:
            return 1
    return 0

class UpdateChecker:
    def __init__(self, repo="aghastmuffin/studify"):
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        self.current_version = self._get_current_version()
        
    def _get_current_version(self):
        """Get the current version from a local version file."""
        version_file = Path(__file__).parent / "_version.json"
        
        if not version_file.exists():
            # Create version file if it doesn't exist
            with open(version_file, 'w') as f:
                version_data = {"version": "0.1.0"}
                json.dump(version_data, f)
            return "0.1.0"
        
        try:
            with open(version_file, 'r') as f:
                version_data = json.load(f)
                return version_data.get("version", "0.1.0")
        except Exception as e:
            print(f"Error reading version file: {e}")
            return "0.1.0"
    
    def _update_current_version(self, new_version):
        """Update the local version file."""
        version_file = Path(__file__).parent / "version.json"
        with open(version_file, 'w') as f:
            json.dump({"version": new_version}, f)
        self.current_version = new_version
    
    def check_for_update(self):
        """Check if there's a newer version available on GitHub."""
        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            # Use custom version comparison function
            is_update_available = compare_versions(self.current_version, latest_version) < 0
            
            return {
                "current_version": self.current_version,
                "latest_version": latest_version,
                "update_available": is_update_available,
                "release_notes": latest_release.get('body', 'No release notes available'),
                "release_url": latest_release.get('html_url', '')
            }
        except requests.RequestException as e:
            print(f"Error checking for updates: {e}")
            return {
                "current_version": self.current_version,
                "update_available": False,
                "error": str(e)
            }
    
    def is_git_repo(self):
        """Check if current directory is a git repository."""
        return os.path.exists(Path(__file__).parent / ".git")
    
    def update(self):
        """Update the application using git pull."""
        if not self.is_git_repo():
            return {"success": False, "message": "Not a git repository. Cannot update automatically."}
        
        try:
            # Navigate to the project root directory
            os.chdir(Path(__file__).parent)
            
            # Run git pull to update
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if "Already up to date" in result.stdout:
                return {"success": True, "message": "Already up to date!"}
            
            # Update version file after successful update
            update_info = self.check_for_update()
            if update_info.get("latest_version"):
                self._update_current_version(update_info["latest_version"])
            
            return {"success": True, "message": "Update successful!", "details": result.stdout}
        
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "message": "Update failed!",
                "error": e.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Update failed!",
                "error": str(e)
            }

def check_for_updates(silent=False):
    """
    Check for updates and return info.
    If silent=True, only returns info without console output.
    """
    updater = UpdateChecker()
    update_info = updater.check_for_update()
    
    if not silent:
        if update_info.get("update_available", False):
            print(f"Update available: {update_info['current_version']} → {update_info['latest_version']}")
            print("\nRelease Notes:")
            print(update_info.get('release_notes', 'No release notes available'))
        else:
            print(f"You're running the latest version: {update_info['current_version']}")
        
    return update_info

def update_app():
    """Perform the update operation."""
    updater = UpdateChecker()
    return updater.update()


def updatefunc():
    update_info = check_for_updates()
    
    if update_info.get("update_available", False):
        updater = UpdateChecker()
        if updater.is_git_repo():
            response = input("Do you want to update now? (y/n): ").lower().strip()
            
            if response == 'y' or response == 'yes':
                print("Updating...")
                result = updater.update()
                
                if result["success"]:
                    print(result["message"])
                    if "details" in result:
                        print(f"Details: {result['details']}")
                else:
                    print(f"Update failed: {result['message']}")
                    if "error" in result:
                        print(f"Error: {result['error']}")
            else:
                print("Update cancelled.")
        else:
            print("This is not a git repository. Cannot update automatically.")
            print("fixing.")
            os.system("git init")
            updatefunc()

# Run CLI interface if script is executed directly
if __name__ == "__main__":
    update_info = check_for_updates()
    
    if update_info.get("update_available", False):
        updater = UpdateChecker()
        if updater.is_git_repo():
            response = input("Do you want to update now? (y/n): ").lower().strip()
            
            if response == 'y' or response == 'yes':
                print("Updating...")
                result = updater.update()
                
                if result["success"]:
                    print(result["message"])
                    if "details" in result:
                        print(f"Details: {result['details']}")
                else:
                    print(f"Update failed: {result['message']}")
                    if "error" in result:
                        print(f"Error: {result['error']}")
            else:
                print("Update cancelled.")
        else:
            print("This is not a git repository. Cannot update automatically.")
            print(f"Please download the latest version from: {update_info.get('release_url', '')}")

#our data is stored on another service by aghastmuffin. Much appreciation to study.priv.adsforafrica.me
