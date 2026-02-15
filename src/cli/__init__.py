"""
CLI Tool for GitHub Agent Secretary
Command-line interface for agent operations
"""
import click
import json
import sys
from typing import Optional
from pathlib import Path

from src.secrets import secrets
from src.canonical_log import canonical_logger
from src.agents.repo_scanner import RepoScannerAgent
from src.integrations.github_integration import GitHubIntegration
from src.integrations.coolify_integration import CoolifyIntegration
from src.integrations.hostinger_integration import HostingerIntegration
from src.integrations.cloudflare_integration import CloudflareIntegration


# Global instances
_scanner = None


def get_scanner():
    """Get or create scanner instance"""
    global _scanner
    if _scanner is None:
        github_token = secrets.require('GH_PAT')
        _scanner = RepoScannerAgent(github_token)
    return _scanner


@click.group()
@click.version_option(version='1.0.0', prog_name='GitHub Agent Secretary')
def cli():
    """
    GitHub Agent Secretary CLI
    
    A command-line interface for repository analysis, PRD generation,
    and deployment management.
    """
    pass


# =============================================================================
# Repository Commands
# =============================================================================

@cli.group()
def repo():
    """Repository operations"""
    pass


@repo.command('scan')
@click.argument('url')
@click.option('--format', '-f', type=click.Choice(['markdown', 'json', 'html']), 
              default='markdown', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def scan_repo(url, format, output):
    """Scan a repository and generate analysis report"""
    click.echo(f"Scanning repository: {url}")
    
    try:
        scanner = get_scanner()
        result = scanner.scan(url)
        report = scanner.generate_report(result, format)
        
        if output:
            Path(output).write_text(report)
            click.echo(f"Report saved to: {output}")
        else:
            click.echo(report)
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@repo.command('list')
def list_repos():
    """List repositories accessible to the authenticated user"""
    try:
        github = GitHubIntegration(secrets.require('GH_PAT'))
        repos = github.list_user_repos()
        
        click.echo("Accessible repositories:")
        for repo in repos[:50]:  # Limit to 50
            click.echo(f"  - {repo}")
            
        if len(repos) > 50:
            click.echo(f"  ... and {len(repos) - 50} more")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@repo.command('info')
@click.argument('url')
def repo_info(url):
    """Get basic repository information"""
    try:
        github = GitHubIntegration(secrets.require('GH_PAT'))
        info = github.get_repo_by_url(url)
        
        click.echo(f"\nRepository: {info.full_name}")
        click.echo(f"Description: {info.description or 'No description'}")
        click.echo(f"Language: {info.language}")
        click.echo(f"Stars: {info.stars}")
        click.echo(f"Forks: {info.forks}")
        click.echo(f"Open Issues: {info.open_issues}")
        click.echo(f"License: {info.license or 'No license'}")
        click.echo(f"URL: {info.url}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# =============================================================================
# PRD Commands
# =============================================================================

@cli.group()
def prd():
    """PRD (Product Requirements Document) operations"""
    pass


@prd.command('create')
@click.argument('repo_url')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def create_prd(repo_url, output):
    """Create a new PRD for a repository"""
    click.echo(f"Creating PRD for: {repo_url}")
    click.echo("PRD creation requires interactive discussion.")
    click.echo("Please use the dashboard interface for full PRD creation.")
    # TODO: Implement interactive PRD creation


@prd.command('list')
def list_prds():
    """List all PRDs"""
    click.echo("PRDs:")
    click.echo("  (PRD storage not yet implemented)")
    # TODO: Implement from database


# =============================================================================
# Deployment Commands
# =============================================================================

@cli.group()
def deploy():
    """Deployment operations"""
    pass


@deploy.command('status')
def deploy_status():
    """Check deployment status"""
    coolify_url = secrets.get('COOLIFY_URL')
    coolify_token = secrets.get('COOLIFY_API_TOKEN')
    
    if not coolify_url or not coolify_token:
        click.echo("Coolify not configured. Set COOLIFY_URL and COOLIFY_API_TOKEN.")
        return
    
    try:
        coolify = CoolifyIntegration(coolify_url, coolify_token)
        apps = coolify.get_applications()
        
        click.echo("Applications:")
        for app in apps:
            click.echo(f"  - {app.name}: {app.status}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@deploy.command('trigger')
@click.argument('app_uuid', required=False)
@click.option('--webhook', '-w', help='Webhook URL for deployment')
def trigger_deploy(app_uuid, webhook):
    """Trigger deployment"""
    if webhook:
        try:
            import requests
            response = requests.get(webhook)
            click.echo(f"Deployment triggered via webhook: {response.status_code}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
        return
    
    if not app_uuid:
        click.echo("Error: Either app_uuid or webhook URL required", err=True)
        return
    
    coolify_url = secrets.get('COOLIFY_URL')
    coolify_token = secrets.get('COOLIFY_API_TOKEN')
    
    if not coolify_url or not coolify_token:
        click.echo("Coolify not configured.")
        return
    
    try:
        coolify = CoolifyIntegration(coolify_url, coolify_token)
        result = coolify.deploy_application(app_uuid)
        click.echo(f"Deployment triggered: {result}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@deploy.command('servers')
def list_servers():
    """List VPS servers"""
    hostinger_token = secrets.get('HOSTINGER_API_TOKEN')
    
    if not hostinger_token:
        click.echo("Hostinger not configured. Set HOSTINGER_API_TOKEN.")
        return
    
    try:
        hostinger = HostingerIntegration(hostinger_token)
        vps_list = hostinger.get_vps_list()
        
        click.echo("VPS Servers:")
        for vps in vps_list:
            click.echo(f"  - {vps.name} ({vps.ip}): {vps.status}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


# =============================================================================
# DNS Commands
# =============================================================================

@cli.group()
def dns():
    """DNS operations"""
    pass


@dns.command('list')
@click.argument('domain', required=False)
def list_dns(domain):
    """List DNS records"""
    cf_token = secrets.get('CLOUDFLARE_API_TOKEN')
    
    if not cf_token:
        click.echo("Cloudflare not configured. Set CLOUDFLARE_API_TOKEN.")
        return
    
    try:
        cf = CloudflareIntegration(cf_token)
        
        if domain:
            zone = cf.get_zone_by_name(domain)
            if zone:
                records = cf.get_dns_records(zone.id)
                click.echo(f"DNS records for {domain}:")
                for record in records:
                    click.echo(f"  {record.type} {record.name} -> {record.content} (TTL: {record.ttl})")
            else:
                click.echo(f"Zone not found: {domain}")
        else:
            zones = cf.get_zones()
            click.echo("Zones:")
            for zone in zones:
                click.echo(f"  - {zone.name} ({zone.status})")
                
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@dns.command('add')
@click.argument('domain')
@click.argument('type')
@click.argument('name')
@click.argument('content')
@click.option('--ttl', default=3600, help='Time to live')
@click.option('--proxy/--no-proxy', default=False, help='Proxy through Cloudflare')
def add_dns_record(domain, type, name, content, ttl, proxy):
    """Add DNS record"""
    cf_token = secrets.get('CLOUDFLARE_API_TOKEN')
    
    if not cf_token:
        click.echo("Cloudflare not configured.")
        return
    
    try:
        cf = CloudflareIntegration(cf_token)
        zone = cf.get_zone_by_name(domain)
        
        if not zone:
            click.echo(f"Zone not found: {domain}")
            return
        
        record = cf.create_dns_record(zone.id, type, name, content, ttl, proxy)
        click.echo(f"Created: {record.type} {record.name} -> {record.content}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


# =============================================================================
# Secrets Commands
# =============================================================================

@cli.group()
def secrets_cmd():
    """Secret operations"""
    pass


@secrets_cmd.command('list')
def list_secrets():
    """List configured secret keys"""
    keys = secrets.list_keys()
    click.echo("Configured secrets:")
    for key in keys:
        click.echo(f"  - {key}")


@secrets_cmd.command('check')
@click.argument('required_keys', nargs=-1)
def check_secrets(required_keys):
    """Check if required secrets are configured"""
    if not required_keys:
        # Default required secrets
        required_keys = [
            'GH_PAT',
            'ANTHROPIC_API_KEY',
            'OPENAI_API_KEY'
        ]
    
    status = secrets.validate_required_secrets(list(required_keys))
    
    click.echo("Secret status:")
    for key, present in status.items():
        status_str = "OK" if present else "MISSING"
        click.echo(f"  - {key}: {status_str}")
    
    missing = [k for k, v in status.items() if not v]
    if missing:
        click.echo(f"\nMissing secrets: {', '.join(missing)}")
        sys.exit(1)


@secrets_cmd.command('audit')
def audit_secrets():
    """View secret access audit log"""
    audit = secrets.get_audit_log()
    
    if not audit:
        click.echo("No secret access recorded.")
        return
    
    click.echo("Secret access audit:")
    for entry in audit:
        click.echo(f"  {entry['timestamp']}: {entry['key']} ({entry['action']})")


# =============================================================================
# Logs Commands
# =============================================================================

@cli.group()
def logs():
    """Log operations"""
    pass


@logs.command('view')
@click.option('--category', '-c', default='agent', help='Log category')
@click.option('--date', '-d', help='Date (YYYY-MM-DD)')
@click.option('--limit', '-l', default=20, help='Number of entries')
def view_logs(category, date, limit):
    """View logs"""
    entries = canonical_logger.query(category, date, limit=limit)
    
    if not entries:
        click.echo("No logs found.")
        return
    
    for entry in entries:
        click.echo(json.dumps(entry, indent=2))


@logs.command('errors')
@click.option('--hours', '-h', default=24, help='Hours to look back')
def view_errors(hours):
    """View recent errors"""
    errors = canonical_logger.get_recent_errors(hours)
    
    if not errors:
        click.echo("No errors found.")
        return
    
    click.echo(f"Recent errors (last {hours} hours):")
    for error in errors:
        click.echo(f"\n[{error['timestamp']}] {error['details'].get('error_type', 'Unknown')}")
        click.echo(f"  {error['details'].get('error_message', 'No message')}")


@logs.command('stats')
@click.option('--category', '-c', default='agent', help='Log category')
def log_stats(category):
    """View log statistics"""
    stats = canonical_logger.get_stats(category)
    
    click.echo(f"Statistics for {category}:")
    click.echo(f"  Total entries: {stats.get('total', 0)}")
    click.echo(f"  Total tokens: {stats.get('total_tokens', 0)}")
    click.echo(f"  Avg duration: {stats.get('avg_duration_ms', 0):.1f}ms")
    
    if stats.get('by_level'):
        click.echo("  By level:")
        for level, count in stats['by_level'].items():
            click.echo(f"    {level}: {count}")


# =============================================================================
# Status Command
# =============================================================================

@cli.command()
def status():
    """Show agent status"""
    click.echo("GitHub Agent Secretary Status")
    click.echo("=" * 40)
    
    # Secrets status
    click.echo(f"\nConfigured secrets: {len(secrets.list_keys())}")
    
    # Check integrations
    click.echo("\nIntegration Status:")
    
    # GitHub
    if secrets.has('GH_PAT'):
        try:
            github = GitHubIntegration(secrets.get('GH_PAT'))
            repos = github.list_user_repos()
            click.echo(f"  GitHub: OK ({len(repos)} repos accessible)")
        except:
            click.echo("  GitHub: ERROR (token may be invalid)")
    else:
        click.echo("  GitHub: NOT CONFIGURED")
    
    # Coolify
    if secrets.has('COOLIFY_URL') and secrets.has('COOLIFY_API_TOKEN'):
        try:
            coolify = CoolifyIntegration(
                secrets.get('COOLIFY_URL'),
                secrets.get('COOLIFY_API_TOKEN')
            )
            if coolify.health_check():
                click.echo("  Coolify: OK")
            else:
                click.echo("  Coolify: ERROR (health check failed)")
        except:
            click.echo("  Coolify: ERROR")
    else:
        click.echo("  Coolify: NOT CONFIGURED")
    
    # Hostinger
    if secrets.has('HOSTINGER_API_TOKEN'):
        try:
            hostinger = HostingerIntegration(secrets.get('HOSTINGER_API_TOKEN'))
            if hostinger.health_check():
                click.echo("  Hostinger: OK")
            else:
                click.echo("  Hostinger: ERROR")
        except:
            click.echo("  Hostinger: ERROR")
    else:
        click.echo("  Hostinger: NOT CONFIGURED")
    
    # Cloudflare
    if secrets.has('CLOUDFLARE_API_TOKEN'):
        try:
            cf = CloudflareIntegration(secrets.get('CLOUDFLARE_API_TOKEN'))
            if cf.verify_token():
                click.echo("  Cloudflare: OK")
            else:
                click.echo("  Cloudflare: ERROR (token invalid)")
        except:
            click.echo("  Cloudflare: ERROR")
    else:
        click.echo("  Cloudflare: NOT CONFIGURED")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == '__main__':
    cli()