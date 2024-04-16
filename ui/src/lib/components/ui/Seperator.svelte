<script>
	export let height = '20'; // default value
	export let direction = 'horizontal'; // default value
</script>

<div 
	class="w-[1px] bg-secondary shrink-0" 
	style="{direction === 'horizontal' ? `height: ${height}px;` : `width: 90%; height: 1px;`}"
/>