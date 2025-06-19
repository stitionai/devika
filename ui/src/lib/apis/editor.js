import { API_BASE_URL } from '$lib/api';
import { toast } from 'svelte-sonner';
import { projectFiles, selectedProject } from '$lib/store';

/**
 * Save a file to the server
 * @param {string} filePath - Path to the file
 * @param {string} content - File content
 * @returns {Promise<boolean>} - Success status
 */
export async function saveFile(filePath, content) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/save-file`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        project_name: localStorage.getItem('selectedProject'),
        file_path: filePath,
        content
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to save file: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.status === 'success';
  } catch (error) {
    console.error('Error saving file:', error);
    toast.error(`Failed to save file: ${error.message}`);
    return false;
  }
}

/**
 * Create a new file
 * @param {string} filePath - Path to the file
 * @param {string} content - Initial file content
 * @returns {Promise<boolean>} - Success status
 */
export async function createFile(filePath, content = '') {
  try {
    const response = await fetch(`${API_BASE_URL}/api/create-file`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        project_name: localStorage.getItem('selectedProject'),
        file_path: filePath,
        content
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create file: ${response.statusText}`);
    }
    
    const data = await response.json();
    if (data.status === 'success') {
      await refreshProjectFiles();
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error creating file:', error);
    toast.error(`Failed to create file: ${error.message}`);
    return false;
  }
}

/**
 * Delete a file
 * @param {string} filePath - Path to the file
 * @returns {Promise<boolean>} - Success status
 */
export async function deleteFile(filePath) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/delete-file`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        project_name: localStorage.getItem('selectedProject'),
        file_path: filePath
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete file: ${response.statusText}`);
    }
    
    const data = await response.json();
    if (data.status === 'success') {
      await refreshProjectFiles();
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error deleting file:', error);
    toast.error(`Failed to delete file: ${error.message}`);
    return false;
  }
}

/**
 * Create a new folder
 * @param {string} folderPath - Path to the folder
 * @returns {Promise<boolean>} - Success status
 */
export async function createFolder(folderPath) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/create-folder`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        project_name: localStorage.getItem('selectedProject'),
        folder_path: folderPath
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create folder: ${response.statusText}`);
    }
    
    const data = await response.json();
    if (data.status === 'success') {
      await refreshProjectFiles();
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error creating folder:', error);
    toast.error(`Failed to create folder: ${error.message}`);
    return false;
  }
}

/**
 * Refresh project files
 * @returns {Promise<Array>} - Project files
 */
export async function refreshProjectFiles() {
  try {
    const projectName = localStorage.getItem('selectedProject');
    const response = await fetch(`${API_BASE_URL}/api/get-project-files?project_name=${projectName}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch project files: ${response.statusText}`);
    }
    
    const data = await response.json();
    projectFiles.set(data.files);
    return data.files;
  } catch (error) {
    console.error('Error fetching project files:', error);
    toast.error(`Failed to fetch project files: ${error.message}`);
    return [];
  }
}

/**
 * Get file content
 * @param {string} filePath - Path to the file
 * @returns {Promise<string>} - File content
 */
export async function getFileContent(filePath) {
  try {
    const projectName = localStorage.getItem('selectedProject');
    const response = await fetch(`${API_BASE_URL}/api/get-file-content?project_name=${projectName}&file_path=${filePath}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch file content: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.content;
  } catch (error) {
    console.error('Error fetching file content:', error);
    toast.error(`Failed to fetch file content: ${error.message}`);
    return null;
  }
}