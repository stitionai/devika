export function clickOutside(node, callback) {
  function handleClick(event) {
    if (!node.contains(event.target)) {
      callback();
    }
  }
  
  document.addEventListener('click', handleClick, true);
  
  return {
    destroy() {
      document.removeEventListener('click', handleClick, true);
    }
  };
}