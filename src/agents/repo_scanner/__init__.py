"""
Repository Scanner Agent
Analyzes GitHub repositories and generates comprehensive reports
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

from src.integrations.github_integration import GitHubIntegration
from src.canonical_log import canonical_logger


@dataclass
class ScanResult:
    """Repository scan result"""
    repo_url: str
    owner: str
    repo: str
    metadata: Dict[str, Any]
    languages: Dict[str, int]
    structure: List[Dict[str, Any]]
    issues: List[Dict]
    pull_requests: List[Dict]
    workflows: List[Dict]
    contributors: List[Dict]
    releases: List[Dict]
    readme: Optional[str]
    recommendations: List[str]
    health_score: float
    scanned_at: str


class RepoScannerAgent:
    """
    Agent for scanning and analyzing GitHub repositories
    
    Provides:
    - Comprehensive repository scanning
    - Health assessment
    - Recommendation generation
    - Report generation in multiple formats
    """
    
    def __init__(self, github_token: str):
        """
        Initialize repository scanner
        
        Args:
            github_token: GitHub Personal Access Token
        """
        self.github = GitHubIntegration(github_token)
    
    def scan(self, repo_url: str) -> ScanResult:
        """
        Scan a repository and generate analysis
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            ScanResult with complete analysis
        """
        correlation_id = canonical_logger.log_repo_scan(
            repo_url,
            "scan_started",
            {"status": "started"}
        )
        
        try:
            # Perform comprehensive scan
            scan_data = self.github.scan_repository(repo_url)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(scan_data)
            
            # Calculate health score
            health_score = self._calculate_health_score(scan_data)
            
            result = ScanResult(
                repo_url=repo_url,
                owner=scan_data['metadata']['owner'],
                repo=scan_data['metadata']['repo'],
                metadata=scan_data['metadata'],
                languages=scan_data['languages'],
                structure=scan_data['tree'],
                issues=scan_data['issues'],
                pull_requests=scan_data['pull_requests'],
                workflows=scan_data['workflows'],
                contributors=scan_data['contributors'],
                releases=scan_data['releases'],
                readme=scan_data['readme'],
                recommendations=recommendations,
                health_score=health_score,
                scanned_at=datetime.utcnow().isoformat()
            )
            
            canonical_logger.log_repo_scan(
                repo_url,
                "scan_completed",
                {
                    "status": "completed",
                    "recommendations_count": len(recommendations),
                    "health_score": health_score
                },
                correlation_id
            )
            
            return result
            
        except Exception as e:
            canonical_logger.log_error(
                e,
                {"repo_url": repo_url},
                correlation_id,
                repo=repo_url
            )
            raise
    
    def _generate_recommendations(self, scan_data: Dict) -> List[str]:
        """Generate recommendations based on scan data"""
        recommendations = []
        
        # Check for README
        if not scan_data.get('readme'):
            recommendations.append("Add a README.md file to document the project")
        elif len(scan_data['readme']) < 100:
            recommendations.append("Expand the README.md with more detailed documentation")
        
        # Check for CI/CD
        has_ci = any(
            '.github/workflows' in str(item.get('path', ''))
            for item in scan_data.get('tree', [])
        )
        if not has_ci:
            recommendations.append("Add CI/CD workflows for automated testing and deployment")
        
        # Check for tests
        has_tests = any(
            'test' in str(item.get('path', '')).lower() or 
            'spec' in str(item.get('path', '')).lower()
            for item in scan_data.get('tree', [])
        )
        if not has_tests:
            recommendations.append("Add test files to improve code quality and maintainability")
        
        # Check for license
        if not scan_data['metadata'].get('license'):
            recommendations.append("Add a LICENSE file to clarify usage rights")
        
        # Check for contributing guide
        has_contributing = any(
            'contributing' in str(item.get('path', '')).lower()
            for item in scan_data.get('tree', [])
        )
        if not has_contributing:
            recommendations.append("Add a CONTRIBUTING.md file to guide contributors")
        
        # Check for code of conduct
        has_coc = any(
            'code_of conduct' in str(item.get('path', '')).lower() or
            'code_of_conduct' in str(item.get('path', '')).lower()
            for item in scan_data.get('tree', [])
        )
        if not has_coc:
            recommendations.append("Consider adding a CODE_OF_CONDUCT.md file")
        
        # Check for security policy
        has_security = any(
            'security' in str(item.get('path', '')).lower()
            for item in scan_data.get('tree', [])
        )
        if not has_security:
            recommendations.append("Add a SECURITY.md file to outline security policy")
        
        # Check for open issues
        open_issues = [i for i in scan_data.get('issues', []) if i.get('state') == 'open']
        if len(open_issues) > 10:
            recommendations.append(f"Consider addressing {len(open_issues)} open issues")
        
        # Check for stale PRs
        open_prs = [pr for pr in scan_data.get('pull_requests', []) if pr.get('state') == 'open']
        if len(open_prs) > 5:
            recommendations.append(f"Review and merge/close {len(open_prs)} open pull requests")
        
        # Check for language diversity
        languages = scan_data.get('languages', {})
        if len(languages) > 5:
            recommendations.append("Consider consolidating languages for better maintainability")
        
        # Check for Docker
        has_docker = any(
            'dockerfile' in str(item.get('path', '')).lower() or
            'docker-compose' in str(item.get('path', '')).lower()
            for item in scan_data.get('tree', [])
        )
        if not has_docker:
            recommendations.append("Add Docker configuration for consistent deployment")
        
        # Check for dependency management
        has_deps = any(
            'package.json' in str(item.get('path', '')) or
            'requirements.txt' in str(item.get('path', '')) or
            'go.mod' in str(item.get('path', '')) or
            'pom.xml' in str(item.get('path', '')) or
            'Cargo.toml' in str(item.get('path', ''))
            for item in scan_data.get('tree', [])
        )
        if not has_deps:
            recommendations.append("Add dependency management file (package.json, requirements.txt, etc.)")
        
        return recommendations
    
    def _calculate_health_score(self, scan_data: Dict) -> float:
        """
        Calculate repository health score (0-100)
        
        Based on:
        - Documentation (20 points)
        - CI/CD (15 points)
        - Tests (15 points)
        - License (10 points)
        - Activity (20 points)
        - Code quality indicators (20 points)
        """
        score = 0.0
        
        # Documentation (20 points)
        if scan_data.get('readme'):
            score += 10
            if len(scan_data['readme']) > 500:
                score += 5
            if len(scan_data['readme']) > 2000:
                score += 5
        
        # CI/CD (15 points)
        has_ci = any(
            '.github/workflows' in str(item.get('path', ''))
            for item in scan_data.get('tree', [])
        )
        if has_ci:
            score += 15
        
        # Tests (15 points)
        has_tests = any(
            'test' in str(item.get('path', '')).lower()
            for item in scan_data.get('tree', [])
        )
        if has_tests:
            score += 15
        
        # License (10 points)
        if scan_data['metadata'].get('license'):
            score += 10
        
        # Activity (20 points)
        updated_at = scan_data['metadata'].get('updated_at', '')
        if updated_at:
            from datetime import datetime, timedelta
            try:
                last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_since_update = (datetime.now(last_update.tzinfo) - last_update).days
                
                if days_since_update < 7:
                    score += 20
                elif days_since_update < 30:
                    score += 15
                elif days_since_update < 90:
                    score += 10
                elif days_since_update < 180:
                    score += 5
            except:
                pass
        
        # Code quality indicators (20 points)
        # Contributors
        contributors_count = len(scan_data.get('contributors', []))
        if contributors_count > 1:
            score += 5
        if contributors_count > 5:
            score += 5
        
        # Releases
        releases_count = len(scan_data.get('releases', []))
        if releases_count > 0:
            score += 5
        
        # Issues management
        open_issues = len([i for i in scan_data.get('issues', []) if i.get('state') == 'open'])
        closed_issues = len([i for i in scan_data.get('issues', []) if i.get('state') == 'closed'])
        if closed_issues > 0:
            issue_ratio = closed_issues / (open_issues + closed_issues)
            score += min(5, issue_ratio * 5)
        
        return min(100.0, score)
    
    def generate_report(self, scan_result: ScanResult, format: str = "markdown") -> str:
        """
        Generate report from scan result
        
        Args:
            scan_result: ScanResult object
            format: Output format (markdown, json, html)
            
        Returns:
            Formatted report
        """
        if format == "json":
            return self._generate_json_report(scan_result)
        elif format == "html":
            return self._generate_html_report(scan_result)
        else:
            return self._generate_markdown_report(scan_result)
    
    def _generate_markdown_report(self, result: ScanResult) -> str:
        """Generate markdown report"""
        report = f"""# Repository Analysis Report

## Overview

| Property | Value |
|----------|-------|
| **Repository** | [{result.metadata.get('full_name', 'N/A')}]({result.metadata.get('url', '#')}) |
| **Description** | {result.metadata.get('description', 'No description')} |
| **Primary Language** | {result.metadata.get('language', 'N/A')} |
| **Health Score** | {result.health_score:.1f}/100 |
| **Stars** | {result.metadata.get('stars', 0)} |
| **Forks** | {result.metadata.get('forks', 0)} |
| **Open Issues** | {result.metadata.get('open_issues', 0)} |
| **License** | {result.metadata.get('license', 'No license')} |
| **Last Updated** | {result.metadata.get('updated_at', 'N/A')} |
| **Scanned At** | {result.scanned_at} |

## Languages

| Language | Bytes | Percentage |
|----------|-------|------------|
"""
        total_bytes = sum(result.languages.values())
        for lang, bytes_count in sorted(result.languages.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            report += f"| {lang} | {bytes_count:,} | {percentage:.1f}% |\n"
        
        report += f"""
## Structure

| Type | Count |
|------|-------|
| Files | {len([i for i in result.structure if i.get('type') == 'blob'])} |
| Directories | {len([i for i in result.structure if i.get('type') == 'tree'])} |

## Issues & Pull Requests

| Type | Open | Total |
|------|------|-------|
| Issues | {len([i for i in result.issues if i.get('state') == 'open'])} | {len(result.issues)} |
| Pull Requests | {len([pr for pr in result.pull_requests if pr.get('state') == 'open'])} | {len(result.pull_requests)} |

## CI/CD

Workflow runs: {len(result.workflows)}

## Contributors

Total contributors: {len(result.contributors)}

## Releases

Total releases: {len(result.releases)}

## Recommendations

"""
        if result.recommendations:
            for i, rec in enumerate(result.recommendations, 1):
                report += f"{i}. {rec}\n"
        else:
            report += "No recommendations - repository looks healthy!\n"
        
        return report
    
    def _generate_json_report(self, result: ScanResult) -> str:
        """Generate JSON report"""
        return json.dumps({
            "repo_url": result.repo_url,
            "metadata": result.metadata,
            "languages": result.languages,
            "structure_summary": {
                "files": len([i for i in result.structure if i.get('type') == 'blob']),
                "directories": len([i for i in result.structure if i.get('type') == 'tree'])
            },
            "issues_count": len(result.issues),
            "pull_requests_count": len(result.pull_requests),
            "workflows_count": len(result.workflows),
            "contributors_count": len(result.contributors),
            "releases_count": len(result.releases),
            "recommendations": result.recommendations,
            "health_score": result.health_score,
            "scanned_at": result.scanned_at
        }, indent=2)
    
    def _generate_html_report(self, result: ScanResult) -> str:
        """Generate HTML report"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Repository Analysis: {result.metadata.get('full_name', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .health-score {{ font-size: 24px; font-weight: bold; color: {'#4CAF50' if result.health_score >= 70 else '#FFC107' if result.health_score >= 40 else '#F44336'}; }}
        .recommendations {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Repository Analysis Report</h1>
    
    <h2>Overview</h2>
    <table>
        <tr><th>Property</th><th>Value</th></tr>
        <tr><td>Repository</td><td><a href="{result.metadata.get('url', '#')}">{result.metadata.get('full_name', 'N/A')}</a></td></tr>
        <tr><td>Description</td><td>{result.metadata.get('description', 'No description')}</td></tr>
        <tr><td>Primary Language</td><td>{result.metadata.get('language', 'N/A')}</td></tr>
        <tr><td>Health Score</td><td class="health-score">{result.health_score:.1f}/100</td></tr>
        <tr><td>Stars</td><td>{result.metadata.get('stars', 0)}</td></tr>
        <tr><td>Forks</td><td>{result.metadata.get('forks', 0)}</td></tr>
        <tr><td>Open Issues</td><td>{result.metadata.get('open_issues', 0)}</td></tr>
        <tr><td>License</td><td>{result.metadata.get('license', 'No license')}</td></tr>
        <tr><td>Last Updated</td><td>{result.metadata.get('updated_at', 'N/A')}</td></tr>
        <tr><td>Scanned At</td><td>{result.scanned_at}</td></tr>
    </table>
    
    <h2>Recommendations</h2>
    <div class="recommendations">
        <ol>
            {''.join(f'<li>{rec}</li>' for rec in result.recommendations)}
        </ol>
    </div>
</body>
</html>"""