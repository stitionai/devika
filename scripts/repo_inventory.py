#!/usr/bin/env python3
"""
Repository Inventory Script
Fetches all repositories and categorizes them for analysis
"""
import sys
import os
import json
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.secrets import secrets
from src.integrations.github_integration import GitHubIntegration
from src.canonical_log import canonical_logger


def fetch_all_repos(github: GitHubIntegration) -> list:
    """Fetch all repositories accessible to the user"""
    all_repos = []
    
    # Get user's own repos
    print("Fetching user repositories...")
    try:
        response = github._request("GET", "/user/repos", params={"per_page": 100, "sort": "updated", "visibility": "all"})
        user_repos = response.json()
        all_repos.extend(user_repos)
        print(f"  Found {len(user_repos)} user repos")
    except Exception as e:
        print(f"  Error fetching user repos: {e}")
    
    # Get organizations the user belongs to
    print("Fetching organizations...")
    try:
        response = github._request("GET", "/user/orgs")
        orgs = response.json()
        
        for org in orgs:
            org_login = org['login']
            print(f"  Fetching repos for org: {org_login}")
            try:
                response = github._request("GET", f"/orgs/{org_login}/repos", params={"per_page": 100})
                org_repos = response.json()
                all_repos.extend(org_repos)
                print(f"    Found {len(org_repos)} repos in {org_login}")
            except Exception as e:
                print(f"    Error fetching org repos: {e}")
    except Exception as e:
        print(f"  Error fetching organizations: {e}")
    
    return all_repos


def categorize_repos(repos: list) -> dict:
    """Categorize repositories by various criteria"""
    categories = {
        "by_visibility": defaultdict(list),
        "by_language": defaultdict(list),
        "by_owner": defaultdict(list),
        "by_status": defaultdict(list),
        "by_topic": defaultdict(list),
        "needs_attention": [],
        "active": [],
        "archived": [],
        "forks": [],
        "templates": []
    }
    
    for repo in repos:
        full_name = repo.get('full_name', 'unknown')
        
        # By visibility
        visibility = repo.get('visibility', 'unknown')
        categories["by_visibility"][visibility].append(full_name)
        
        # By language
        language = repo.get('language') or 'Unknown'
        categories["by_language"][language].append(full_name)
        
        # By owner
        owner = repo.get('owner', {}).get('login', 'unknown')
        categories["by_owner"][owner].append(full_name)
        
        # By status
        if repo.get('archived', False):
            categories["archived"].append(full_name)
            categories["by_status"]["archived"].append(full_name)
        else:
            categories["active"].append(full_name)
            categories["by_status"]["active"].append(full_name)
        
        # Forks
        if repo.get('fork', False):
            categories["forks"].append(full_name)
        
        # Topics
        for topic in repo.get('topics', []):
            categories["by_topic"][topic].append(full_name)
        
        # Needs attention
        issues = [
            not repo.get('description'),
            repo.get('open_issues_count', 0) > 10,
            not repo.get('license'),
            repo.get('size', 0) == 0
        ]
        if any(issues):
            categories["needs_attention"].append({
                "name": full_name,
                "issues": {
                    "no_description": not repo.get('description'),
                    "many_open_issues": repo.get('open_issues_count', 0) > 10,
                    "no_license": not repo.get('license'),
                    "empty": repo.get('size', 0) == 0
                }
            })
    
    return categories


def generate_report(repos: list, categories: dict) -> str:
    """Generate a comprehensive report"""
    report = []
    report.append("# Repository Inventory Report")
    report.append(f"\nGenerated: {datetime.utcnow().isoformat()}")
    report.append(f"\n## Summary\n")
    
    total = len(repos)
    public = len(categories["by_visibility"].get("public", []))
    private = len(categories["by_visibility"].get("private", []))
    
    report.append(f"- **Total Repositories**: {total}")
    report.append(f"- **Public**: {public}")
    report.append(f"- **Private**: {private}")
    report.append(f"- **Active**: {len(categories['active'])}")
    report.append(f"- **Archived**: {len(categories['archived'])}")
    report.append(f"- **Forks**: {len(categories['forks'])}")
    
    report.append(f"\n## By Visibility\n")
    for visibility, repos_list in sorted(categories["by_visibility"].items()):
        report.append(f"### {visibility.upper()} ({len(repos_list)})\n")
        for repo in sorted(repos_list):
            report.append(f"- {repo}")
    
    report.append(f"\n## By Language\n")
    for language, repos_list in sorted(categories["by_language"].items(), key=lambda x: len(x[1]), reverse=True):
        report.append(f"### {language} ({len(repos_list)})\n")
        for repo in sorted(repos_list):
            report.append(f"- {repo}")
    
    report.append(f"\n## By Owner\n")
    for owner, repos_list in sorted(categories["by_owner"].items()):
        report.append(f"### {owner} ({len(repos_list)})\n")
        for repo in sorted(repos_list):
            report.append(f"- {repo}")
    
    report.append(f"\n## By Topic\n")
    topics = {k: v for k, v in categories["by_topic"].items() if v}
    if topics:
        for topic, repos_list in sorted(topics.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
            report.append(f"- **{topic}**: {len(repos_list)} repos")
    else:
        report.append("No topics defined.")
    
    report.append(f"\n## Needs Attention\n")
    if categories["needs_attention"]:
        for item in categories["needs_attention"]:
            issues_str = ", ".join(k for k, v in item["issues"].items() if v)
            report.append(f"- **{item['name']}**: {issues_str}")
    else:
        report.append("All repositories look good!")
    
    report.append(f"\n## Detailed Repository List\n")
    for repo in sorted(repos, key=lambda x: x.get('full_name', '')):
        name = repo.get('full_name', 'unknown')
        desc = repo.get('description', 'No description')[:50]
        lang = repo.get('language', 'Unknown')
        stars = repo.get('stargazers_count', 0)
        visibility = repo.get('visibility', 'unknown')
        archived = " [ARCHIVED]" if repo.get('archived') else ""
        fork = " [FORK]" if repo.get('fork') else ""
        
        report.append(f"- **{name}**{archived}{fork}")
        report.append(f"  - {desc}...")
        report.append(f"  - Language: {lang} | Stars: {stars} | {visibility}")
    
    return "\n".join(report)


def main():
    """Main function"""
    print("=" * 60)
    print("GitHub Repository Inventory")
    print("=" * 60)
    
    # Get GitHub token
    github_token = secrets.get('GH_PAT')
    if not github_token:
        print("Error: GH_PAT not found in secrets")
        sys.exit(1)
    
    # Initialize GitHub integration
    github = GitHubIntegration(github_token)
    
    # Fetch all repos
    repos = fetch_all_repos(github)
    
    if not repos:
        print("No repositories found!")
        sys.exit(1)
    
    print(f"\nTotal repositories found: {len(repos)}")
    
    # Categorize
    print("\nCategorizing repositories...")
    categories = categorize_repos(repos)
    
    # Generate report
    print("\nGenerating report...")
    report = generate_report(repos, categories)
    
    # Save report
    report_path = "reports/repo_inventory.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")
    
    # Also save JSON data
    json_path = "reports/repo_inventory.json"
    with open(json_path, 'w') as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat(),
            "total_count": len(repos),
            "categories": {k: dict(v) if isinstance(v, defaultdict) else v for k, v in categories.items()},
            "repositories": repos
        }, f, indent=2, default=str)
    print(f"JSON data saved to: {json_path}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Repositories: {len(repos)}")
    print(f"Public: {len(categories['by_visibility'].get('public', []))}")
    print(f"Private: {len(categories['by_visibility'].get('private', []))}")
    print(f"Active: {len(categories['active'])}")
    print(f"Archived: {len(categories['archived'])}")
    print(f"Forks: {len(categories['forks'])}")
    print(f"Needs Attention: {len(categories['needs_attention'])}")
    
    # Print languages
    print("\nTop Languages:")
    for lang, repos_list in sorted(categories["by_language"].items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  {lang}: {len(repos_list)}")
    
    # Print owners
    print("\nOwners:")
    for owner, repos_list in sorted(categories["by_owner"].items()):
        print(f"  {owner}: {len(repos_list)}")


if __name__ == "__main__":
    main()