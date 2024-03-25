<script>
    import { fetchLogs } from "$lib/api";
    import { onMount } from "svelte";

    let logs = [];
    let socket_logs = [];

    const logColors = {
        'ERROR': 'text-red-500',
        'EXCEPT': 'text-red-500',
        'WARNING': 'text-yellow-500',
        'INFO': 'text-blue-500',
        'DEBUG': 'text-gray-500'
    };

    function getTextColor(log) {
        for (const key in logColors) {
            if (log.includes(key)) {
                return logColors[key];
            }
        }
        return '';
    }

    onMount(async () => {
        const log = await fetchLogs();
        const last_100_logs = log.split("\n").slice(-100).reverse().filter(log => log !== "");

        [logs, socket_logs] = last_100_logs.reduce(([logs, socket_logs], log) => {
            if (log.includes("SOCKET")) {
                socket_logs.push(log);
            } else {
                logs.push(log);
            }
            return [logs, socket_logs];
        }, [[], []]);
    });
</script>

<div class="p-4 h-full gap-8 flex flex-col overflow-x-clip">
    <h1 class="text-3xl">Logs</h1>
    <div class="flex gap-4 overflow-y-auto">
        <div class="flex flex-col gap-4 w-1/2">
            <h1 class="text-2xl">Request logs</h1>
            <div class="flex flex-col gap-2">
                {#each logs as log}
                    <p class=" whitespace-normal break-words {getTextColor(log)}">
                        {@html log}
                    </p>
                {/each}
            </div>
        </div>
        <div class="flex flex-col gap-4 w-1/2">
            <h1 class="text-2xl">Socket logs</h1>
            <div class="flex flex-col gap-2">
                {#each socket_logs as log}
                    <p class="{getTextColor(log)}">
                        {@html log}
                    </p>
                {/each}
            </div>
        </div>
    </div>
</div>