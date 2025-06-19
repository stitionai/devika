<script>
  import { notifications } from '$lib/stores/editor.js';
  import { fade, fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';

  function getNotificationIcon(type) {
    switch (type) {
      case 'success':
        return 'fas fa-check-circle text-green-500';
      case 'error':
        return 'fas fa-exclamation-circle text-red-500';
      case 'warning':
        return 'fas fa-exclamation-triangle text-yellow-500';
      case 'info':
      default:
        return 'fas fa-info-circle text-blue-500';
    }
  }

  function getNotificationClass(type) {
    switch (type) {
      case 'success':
        return 'border-green-500 bg-green-50 dark:bg-green-900/20';
      case 'error':
        return 'border-red-500 bg-red-50 dark:bg-red-900/20';
      case 'warning':
        return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20';
      case 'info':
      default:
        return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
    }
  }

  function dismissNotification(id) {
    notifications.update(n => n.filter(notif => notif.id !== id));
  }
</script>

<div class="notification-container fixed top-4 right-4 z-50 space-y-2">
  {#each $notifications as notification (notification.id)}
    <div
      class="notification flex items-center p-4 rounded-lg border-l-4 shadow-lg max-w-sm {getNotificationClass(notification.type)}"
      transition:fly={{ x: 300, duration: 300, easing: quintOut }}
    >
      <i class="{getNotificationIcon(notification.type)} mr-3"></i>
      
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium text-foreground">{notification.message}</p>
      </div>
      
      <button
        class="ml-3 text-tertiary hover:text-foreground transition-colors"
        on:click={() => dismissNotification(notification.id)}
      >
        <i class="fas fa-times text-xs"></i>
      </button>
    </div>
  {/each}
</div>

<style>
  .notification {
    backdrop-filter: blur(10px);
    animation: notificationSlide 0.3s ease-out;
  }
  
  @keyframes notificationSlide {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
</style>