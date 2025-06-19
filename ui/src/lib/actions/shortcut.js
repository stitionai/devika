export function shortcut(node, shortcuts) {
  function handleKeydown(event) {
    const key = event.key.toLowerCase();
    const ctrl = event.ctrlKey || event.metaKey;
    const shift = event.shiftKey;
    const alt = event.altKey;
    
    for (const [shortcut, handler] of Object.entries(shortcuts)) {
      const parts = shortcut.toLowerCase().split('+');
      const shortcutKey = parts[parts.length - 1];
      const hasCtrl = parts.includes('ctrl') || parts.includes('cmd');
      const hasShift = parts.includes('shift');
      const hasAlt = parts.includes('alt');
      
      if (
        key === shortcutKey &&
        ctrl === hasCtrl &&
        shift === hasShift &&
        alt === hasAlt
      ) {
        event.preventDefault();
        handler(event);
        break;
      }
    }
  }
  
  node.addEventListener('keydown', handleKeydown);
  
  return {
    update(newShortcuts) {
      shortcuts = newShortcuts;
    },
    destroy() {
      node.removeEventListener('keydown', handleKeydown);
    }
  };
}