<script>
  import SidebarButton from "./ui/SidebarButton.svelte";
  import { page } from "$app/stores";
  import Clock from "lucide-svelte/icons/clock";
  import Home from "lucide-svelte/icons/home";
  import Settings from "lucide-svelte/icons/settings";
    

  let navItems = [
    {
      icon: Home,
      tooltip: "Home",
      route: "/",
    },
    {
      icon: Settings,
      tooltip: "Settings",
      route: "/settings",
    },
    {
      icon: Clock,
      tooltip: "Logs",
      route: "/logs",
    },
  ];
  console.log($page.url)
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
