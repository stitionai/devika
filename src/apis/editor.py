from flask import Blueprint, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from src.config import Config
from src.project import ProjectManager
from src.logger import Logger

editor_bp = Blueprint('editor', __name__, template_folder='../templates')
logger = Logger()
config = Config()
manager = ProjectManager()

# File type to language mapping
LANGUAGE_MAP = {
    'js': 'javascript',
    'jsx': 'javascript',
    'ts': 'typescript',
    'tsx': 'typescript',
    'py': 'python',
    'html': 'html',
    'css': 'css',
    'scss': 'scss',
    'json': 'json',
    'md': 'markdown',
    'yml': 'yaml',
    'yaml': 'yaml',
    'xml': 'xml',
    'sql': 'sql',
    'sh': 'shell'
}

# File icon mapping
ICON_MAP = {
    'js': 'fab fa-js-square text-yellow-500',
    'jsx': 'fab fa-react text-blue-400',
    'ts': 'fab fa-js-square text-blue-600',
    'tsx': 'fab fa-react text-blue-600',
    'py': 'fab fa-python text-green-500',
    'html': 'fab fa-html5 text-orange-500',
    'css': 'fab fa-css3-alt text-blue-500',
    'scss': 'fab fa-sass text-pink-500',
    'json': 'fas fa-brackets-curly text-yellow-600',
    'md': 'fab fa-markdown text-gray-600',
    'xml': 'fas fa-code text-orange-400',
    'svg': 'fas fa-vector-square text-purple-500',
    'png': 'fas fa-image text-green-400',
    'jpg': 'fas fa-image text-green-400',
    'pdf': 'fas fa-file-pdf text-red-500',
    'zip': 'fas fa-file-archive text-gray-500'
}

def get_file_icon(filename):
    """Get Font Awesome icon class for file type"""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    return ICON_MAP.get(ext, 'fas fa-file text-gray-400')

def get_file_language(filename):
    """Get Monaco editor language for file type"""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    return LANGUAGE_MAP.get(ext, 'plaintext')

def build_file_tree(files, expanded_folders=None):
    """Build hierarchical file tree from flat file list"""
    if expanded_folders is None:
        expanded_folders = set()
    
    tree = {}
    
    for file in files:
        parts = file['file'].split('/')
        current = tree
        
        for i, part in enumerate(parts):
            path = '/'.join(parts[:i+1])
            is_file = i == len(parts) - 1
            
            if part not in current:
                current[part] = {
                    'name': part,
                    'path': path,
                    'type': 'file' if is_file else 'folder',
                    'level': i,
                    'expanded': path in expanded_folders,
                    'children': {} if not is_file else None,
                    'size': len(file['code'].encode('utf-8')) if is_file else 0,
                    'modified': False,
                    'language': get_file_language(part) if is_file else None,
                    'content': file['code'] if is_file else None
                }
            
            if not is_file:
                current = current[part]['children']
    
    return flatten_tree(tree)

def flatten_tree(tree, result=None):
    """Flatten tree structure for template rendering"""
    if result is None:
        result = []
    
    for item in tree.values():
        result.append(item)
        if item['type'] == 'folder' and item['expanded'] and item['children']:
            flatten_tree(item['children'], result)
    
    return result

@editor_bp.route('/editor')
def editor_main():
    """Main editor interface"""
    try:
        # Get current project from session or query params
        current_project = request.args.get('project') or session.get('current_project')
        
        # Get all projects
        projects = [{'name': p} for p in manager.get_project_list()]
        
        # Get project files if project is selected
        project_files = []
        active_file = None
        open_tabs = []
        
        if current_project:
            session['current_project'] = current_project
            files = manager.get_project_files(current_project)
            
            # Get expanded folders from session
            expanded_folders = set(session.get('expanded_folders', []))
            
            # Build file tree
            project_files = build_file_tree(files, expanded_folders)
            
            # Get open tabs from session
            open_tabs = session.get('open_tabs', [])
            
            # Get active file
            active_file_path = session.get('active_file')
            if active_file_path:
                for file in files:
                    if file['file'] == active_file_path:
                        active_file = {
                            'name': file['file'].split('/')[-1],
                            'path': file['file'],
                            'content': file['code'],
                            'language': get_file_language(file['file']),
                            'size': len(file['code'].encode('utf-8')),
                            'modified': False
                        }
                        break
        
        # Theme settings
        theme_class = session.get('theme', 'dark')
        theme_config = {
            'primary': '#2F3337' if theme_class == 'dark' else '#ffffff',
            'background': '#1D1F21' if theme_class == 'dark' else '#ffffff',
            'secondary': '#2F3337' if theme_class == 'dark' else '#f1f2f5',
            'tertiary': '#81878C' if theme_class == 'dark' else '#919AA3',
            'foreground': '#dcdcdc' if theme_class == 'dark' else '#303438',
            'border': '#2B2F34' if theme_class == 'dark' else '#E4E3E8',
            'success': '#22c55e',
            'warning': '#f59e0b',
            'error': '#ef4444'
        }
        
        # Editor settings
        editor_settings = session.get('editor_settings', {
            'fontSize': 14,
            'fontFamily': 'Monaco, Menlo, "Ubuntu Mono", monospace',
            'wordWrap': True,
            'minimap': True,
            'lineNumbers': True,
            'autoSave': True,
            'autoSaveDelay': 2000,
            'tabSize': 2,
            'insertSpaces': True
        })
        
        # Available commands for command palette
        available_commands = [
            {
                'id': 'file.new',
                'title': 'New File',
                'description': 'Create a new file',
                'icon': 'fas fa-file-plus',
                'shortcut': 'Ctrl+N'
            },
            {
                'id': 'file.save',
                'title': 'Save File',
                'description': 'Save the current file',
                'icon': 'fas fa-save',
                'shortcut': 'Ctrl+S'
            },
            {
                'id': 'file.saveAll',
                'title': 'Save All Files',
                'description': 'Save all modified files',
                'icon': 'fas fa-save',
                'shortcut': 'Ctrl+Shift+S'
            },
            {
                'id': 'edit.find',
                'title': 'Find',
                'description': 'Find text in current file',
                'icon': 'fas fa-search',
                'shortcut': 'Ctrl+F'
            },
            {
                'id': 'edit.replace',
                'title': 'Find and Replace',
                'description': 'Find and replace text',
                'icon': 'fas fa-search-plus',
                'shortcut': 'Ctrl+H'
            },
            {
                'id': 'edit.format',
                'title': 'Format Document',
                'description': 'Format the current document',
                'icon': 'fas fa-code',
                'shortcut': 'Shift+Alt+F'
            },
            {
                'id': 'view.toggleMinimap',
                'title': 'Toggle Minimap',
                'description': 'Show or hide the minimap',
                'icon': 'fas fa-map'
            },
            {
                'id': 'view.commandPalette',
                'title': 'Command Palette',
                'description': 'Show all commands',
                'icon': 'fas fa-terminal',
                'shortcut': 'Ctrl+Shift+P'
            }
        ]
        
        # Git status (mock data)
        git_status = {
            'branch': 'main',
            'changes': 0
        } if current_project else None
        
        return render_template('editor/main.html',
            projects=projects,
            current_project=current_project,
            project_files=project_files,
            active_file=active_file,
            open_tabs=open_tabs,
            theme_class=theme_class,
            theme=theme_config,
            editor_settings=editor_settings,
            available_commands=available_commands,
            connected=True,
            git_status=git_status,
            api_base_url=request.host_url.rstrip('/'),
            get_file_icon=get_file_icon
        )
        
    except Exception as e:
        logger.error(f"Error loading editor: {str(e)}")
        return render_template('editor/error.html', error=str(e)), 500

@editor_bp.route('/editor/api/file/open', methods=['POST'])
def open_file():
    """Open a file in the editor"""
    try:
        data = request.json
        project_name = data.get('project')
        file_path = data.get('path')
        
        if not project_name or not file_path:
            return jsonify({'error': 'Missing project or file path'}), 400
        
        # Get file content
        files = manager.get_project_files(project_name)
        file_content = None
        
        for file in files:
            if file['file'] == file_path:
                file_content = file['code']
                break
        
        if file_content is None:
            return jsonify({'error': 'File not found'}), 404
        
        # Update session
        session['current_project'] = project_name
        session['active_file'] = file_path
        
        # Add to open tabs if not already open
        open_tabs = session.get('open_tabs', [])
        if not any(tab['path'] == file_path for tab in open_tabs):
            open_tabs.append({
                'name': file_path.split('/')[-1],
                'path': file_path,
                'modified': False
            })
            session['open_tabs'] = open_tabs
        
        return jsonify({
            'success': True,
            'file': {
                'name': file_path.split('/')[-1],
                'path': file_path,
                'content': file_content,
                'language': get_file_language(file_path),
                'size': len(file_content.encode('utf-8'))
            }
        })
        
    except Exception as e:
        logger.error(f"Error opening file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@editor_bp.route('/editor/api/file/save', methods=['POST'])
def save_file():
    """Save a file"""
    try:
        data = request.json
        project_name = data.get('project')
        file_path = data.get('path')
        content = data.get('content', '')
        
        if not project_name or not file_path:
            return jsonify({'error': 'Missing project or file path'}), 400
        
        # Save file using existing API
        response = manager.save_file(project_name, file_path, content)
        
        if response:
            # Update tab status
            open_tabs = session.get('open_tabs', [])
            for tab in open_tabs:
                if tab['path'] == file_path:
                    tab['modified'] = False
                    break
            session['open_tabs'] = open_tabs
            
            return jsonify({'success': True, 'message': f'Saved {file_path}'})
        else:
            return jsonify({'error': 'Failed to save file'}), 500
            
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@editor_bp.route('/editor/api/file/create', methods=['POST'])
def create_file():
    """Create a new file"""
    try:
        data = request.json
        project_name = data.get('project')
        file_path = data.get('path')
        content = data.get('content', '')
        
        if not project_name or not file_path:
            return jsonify({'error': 'Missing project or file path'}), 400
        
        # Create file using existing API
        response = manager.create_file(project_name, file_path, content)
        
        if response:
            return jsonify({'success': True, 'message': f'Created {file_path}'})
        else:
            return jsonify({'error': 'Failed to create file'}), 500
            
    except Exception as e:
        logger.error(f"Error creating file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@editor_bp.route('/editor/api/folder/toggle', methods=['POST'])
def toggle_folder():
    """Toggle folder expansion state"""
    try:
        data = request.json
        folder_path = data.get('path')
        
        if not folder_path:
            return jsonify({'error': 'Missing folder path'}), 400
        
        expanded_folders = set(session.get('expanded_folders', []))
        
        if folder_path in expanded_folders:
            expanded_folders.remove(folder_path)
        else:
            expanded_folders.add(folder_path)
        
        session['expanded_folders'] = list(expanded_folders)
        
        return jsonify({'success': True, 'expanded': folder_path in expanded_folders})
        
    except Exception as e:
        logger.error(f"Error toggling folder: {str(e)}")
        return jsonify({'error': str(e)}), 500

@editor_bp.route('/editor/api/tab/close', methods=['POST'])
def close_tab():
    """Close a tab"""
    try:
        data = request.json
        file_path = data.get('path')
        
        if not file_path:
            return jsonify({'error': 'Missing file path'}), 400
        
        # Remove from open tabs
        open_tabs = session.get('open_tabs', [])
        open_tabs = [tab for tab in open_tabs if tab['path'] != file_path]
        session['open_tabs'] = open_tabs
        
        # Update active file if it was the closed tab
        if session.get('active_file') == file_path:
            session['active_file'] = open_tabs[0]['path'] if open_tabs else None
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error closing tab: {str(e)}")
        return jsonify({'error': str(e)}), 500

@editor_bp.route('/editor/api/settings/update', methods=['POST'])
def update_settings():
    """Update editor settings"""
    try:
        data = request.json
        
        # Update editor settings in session
        current_settings = session.get('editor_settings', {})
        current_settings.update(data)
        session['editor_settings'] = current_settings
        
        return jsonify({'success': True, 'settings': current_settings})
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@editor_bp.route('/editor/api/theme/toggle', methods=['POST'])
def toggle_theme():
    """Toggle between light and dark theme"""
    try:
        current_theme = session.get('theme', 'dark')
        new_theme = 'light' if current_theme == 'dark' else 'dark'
        session['theme'] = new_theme
        
        return jsonify({'success': True, 'theme': new_theme})
        
    except Exception as e:
        logger.error(f"Error toggling theme: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Template filters
@editor_bp.app_template_filter('filesizeformat')
def filesizeformat(value):
    """Format file size in human readable format"""
    if value == 0:
        return '0 B'
    
    units = ['B', 'KB', 'MB', 'GB']
    size = float(value)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"