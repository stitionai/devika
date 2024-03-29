<script>
	import { onMount } from "svelte";
	import "xterm/css/xterm.css";
	import { agentState } from "$lib/store";

	let terminalElement;
	let terminal;
	let fitAddon;

	onMount(async () => {
		let xterm = await import("xterm");
		let xtermAddonFit = await import("xterm-addon-fit");

		terminal = new xterm.Terminal({
			disableStdin: true,
			cursorBlink: true,
			convertEol: true,
			rows: 1
		});

		fitAddon = new xtermAddonFit.FitAddon();
		terminal.loadAddon(fitAddon);
		terminal.open(terminalElement);
		fitAddon.fit();

		let previousState = {};

		agentState.subscribe((state) => {
			if (state && state.terminal_session) {
				console.log("Terminal state: ", state.terminal_session);

				let command = state.terminal_session.command || 'echo "Waiting..."';
				let output = state.terminal_session.output || "Waiting...";
				let title = state.terminal_session.title || "Terminal";

				// Check if the current state is different from the previous state
				if (
					command !== previousState.command ||
					output !== previousState.output ||
					title !== previousState.title
				) {
					console.log("Command: ", command);
					addCommandAndOutput(command, output, title);

					// Update the previous state
					previousState = { command, output, title };
				}
			}

			fitAddon.fit();
		});
	});

	function addCommandAndOutput(command, output, title) {
		if (title) {
			document.getElementById("terminal-title").innerText = title;
		}
		terminal.reset();
		terminal.write(`$ ${command}\r\n\r\n${output}\r\n`);
	}
</script>

<div class="flex flex-1 flex-col overflow-hidden rounded border border-indigo-700 bg-slate-950">
	<div class="flex items-center border-b border-gray-700 p-2">
		<div class="ml-2 mr-4 flex space-x-2">
			<div class="h-3 w-3 rounded-full bg-red-500"></div>
			<div class="h-3 w-3 rounded-full bg-yellow-400"></div>
			<div class="h-3 w-3 rounded-full bg-green-500"></div>
		</div>
		<span id="terminal-title">Terminal</span>
	</div>
	<div
		id="terminal-content"
		class="flex flex-grow overflow-hidden bg-black"
		bind:this={terminalElement}
		style="height: 100%; margin-left: 5px;"
	></div>
</div>

<style>
	#terminal-content {
		height: 100%;
	}

	#terminal-content :global(.xterm) {
		padding: 10px;
		height: 100%; /* Ensure terminal content height is fixed */
	}

	#terminal-content :global(.xterm-viewport) {
		overflow-y: auto !important;
		height: 100%;
	}

	#terminal-content::-webkit-scrollbar,
	#terminal-content :global(.xterm-viewport)::-webkit-scrollbar {
		width: 4px;
	}

	#terminal-content::-webkit-scrollbar-track,
	#terminal-content :global(.xterm-viewport)::-webkit-scrollbar-track {
		background: #020617;
		border-radius: 10px;
	}

	#terminal-content::-webkit-scrollbar-thumb,
	#terminal-content :global(.xterm-viewport)::-webkit-scrollbar-thumb {
		background: #4337c9;
		border-radius: 10px;
	}
</style>
