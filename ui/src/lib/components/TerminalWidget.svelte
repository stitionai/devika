<script>
  import { onMount } from "svelte";
  import "xterm/css/xterm.css";
  import { agentState } from "$lib/store";

  let terminalElement;
  let terminal;
  let fitAddon;
  // agentState.subscribe((value) => {
  //   $agentState = value;
  // });

  onMount(async () => {
    let xterm = await import('xterm');
    let xtermAddonFit = await import('xterm-addon-fit')

    terminal = new xterm.Terminal({
      disableStdin: true,
      cursorBlink: true,
      convertEol: true,
      rows: 1,
      theme: {
        background: "#111315",
        foreground: "#9CA3AB",
        innerText: "#00FFFF",
        cursor: "#00FFFF",
      },
    });
    fitAddon = new xtermAddonFit.FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.open(terminalElement);
    fitAddon.fit();

    let previousState = {};

    agentState.subscribe((state) => {
      if (state && state.terminal_session) {
        let command = state.terminal_session.command || '$ "Waiting..."';
        let output = state.terminal_session.output || "Waiting...";
        let title = state.terminal_session.title || "Terminal";

        // Check if the current state is different from the previous state
        if (
          command !== previousState.command ||
          output !== previousState.output ||
          title !== previousState.title
        ) {
          addCommandAndOutput(command, output, title);

          // Update the previous state
          previousState = { command, output, title };
        }
      }
      else {
        // Reset the terminal
        terminal.reset();
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

<div class="flex flex-col border-[4px] overflow-hidden rounded-3xl h-1/2 border-window-outline bg-terminal-background">
  <div class="flex items-center p-2 py-3 border-b">
    <div class="flex ml-2 mr-4 space-x-2">
      <div class="red-dot"></div>
      <div class="yellow-dot"></div>
      <div class="green-dot"></div>
    </div>
    <span id="terminal-title" class="text-primary-foreground">devika's Terminal</span>
  </div>
  <div
    id="terminal-content"
    class="w-full h-full rounded-bl-lg bg-primary"
    bind:this={terminalElement}
  ></div>
</div>

<style>
  #terminal-content :global(.xterm) {
    padding: 10px;
    height: 100%; /* Ensure terminal content height is fixed */
  }

  #terminal-content :global(.xterm-viewport) {
    overflow-y: auto !important;
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
  .red-dot {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: #FF605C;
  }
  .yellow-dot {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color:  #FFBD44;
  }
  .green-dot {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  background-color: #00CA4E;
  }
  
</style>
