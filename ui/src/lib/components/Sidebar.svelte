<script>
  import SidebarButton from "./ui/SidebarButton.svelte";
  import { page } from "$app/stores";
  import {Icons} from "./../icons"

  let navItems = [
    {
      icon: Icons.HOME,
      tooltip: "Home",
      route: "/",
    },
    {
      icon: Icons.SETTINGS,
      tooltip: "Settings",
      route: "/settings",
    },
    {
      icon: Icons.LOGS,
      tooltip: "Logs",
      route: "/logs",
    },
  ];
</script>

<div
  class="flex flex-col text-tertiary mx-2 my-4 gap-6 items-center bg-secondary rounded-xl p-6"
>
  {#each navItems as { icon, tooltip, route }, i}
    <SidebarButton
      icon={icon}
      href={route}
      {tooltip}
      isSelected={$page.url.pathname == route}
    />
  {/each}
</div>
