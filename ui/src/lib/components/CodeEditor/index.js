// Export all enhanced code editor components
export { default as EnhancedWebCodeEditor } from './EnhancedWebCodeEditor.svelte';
export { default as EnhancedEditor } from './EnhancedEditor.svelte';
export { default as SmartFileExplorer } from './SmartFileExplorer.svelte';
export { default as AdvancedTabManager } from './AdvancedTabManager.svelte';
export { default as CommandPalette } from './CommandPalette.svelte';
export { default as NotificationSystem } from './NotificationSystem.svelte';
export { default as EditorToolbar } from './EditorToolbar.svelte';
export { default as StatusBar } from './StatusBar.svelte';

// Export utilities and stores
export * from './monaco-config.js';
export * from '$lib/stores/editor.js';
export * from '$lib/utils/debounce.js';
export * from '$lib/actions/shortcut.js';
export * from '$lib/actions/clickOutside.js';