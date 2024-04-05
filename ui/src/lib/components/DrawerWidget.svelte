<script>
    import * as Sheet from "$lib/components/ui/sheet/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Slider } from "$lib/components/ui/slider";
    import { Label } from "$lib/components/ui/label";
    import { Separator } from "$lib/components/ui/separator";
    import * as Select from "$lib/components/ui/select/index.js";

    import {
        searchEngineList,
    } from "$lib/store";
    import { get } from "svelte/store";

    const engines = [
        { value: "google", label: "Google" },
        { value: "bing", label: "Bing" },
        { value: "duckduckgo", label: "DuckDuckGo" }
    ]

    let selectedSearchEngine;

    const checkListAndSetItem = (list, itemKey, defaultItem) => {
        if (get(list) && get(list).length > 0) {
        const item = localStorage.getItem(itemKey);
        return item ? item : defaultItem;
        } else {
        localStorage.setItem(itemKey, "");
        return defaultItem;
        }
    };

    selectedSearchEngine = checkListAndSetItem(
        searchEngineList,
        "selectedSearchEngine",
        "Select Search Engine",
    );

    function selectSearchEngine(searchEngine) {
        selectedSearchEngine = searchEngine;
        localStorage.setItem("selectedSearchEngine", searchEngine);
    }

</script>

<Sheet.Root>
    <Sheet.Trigger asChild let:builder>
        <Button builders={[builder]} variant="outline">
            <svg width=20 xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="rgba(173,184,194,1)"><path d="M3 4H21V6H3V4ZM3 11H21V13H3V11ZM3 18H21V20H3V18Z"></path></svg>
        </Button>
    </Sheet.Trigger>
    <Sheet.Content side="right" class="p-5">
        <Sheet.Header class="p-2">
            <Sheet.Title>Modify Settings</Sheet.Title>
            <Sheet.Description>
                <!-- Make changes to your profile here. Click save when you're done. -->
                <Separator />
            </Sheet.Description>
        </Sheet.Header>
        <!-- <Select.Root>
            <Select.Trigger class="w-[180px]">
              <Select.Value placeholder="Select an engine" />
            </Select.Trigger>
            <Select.Content>
              <Select.Group>
                <Select.Label>Search Engine</Select.Label>
                {#each engines as engine}
                  <Select.Item value={engine.value} label={engine.label} on:click={() => selectSearchEngine(engine.value)}
                    >{engine.label}</Select.Item
                  >
                {/each}
              </Select.Group>
            </Select.Content>
            <Select.Input name="selected engine" />
          </Select.Root> -->
        <div class="grid gap-4 py-4 px-2">
            <div class="flex flex-col gap-4 mb-2">
                <div class="flex justify-between items-center mb-3">
                    <Label for="temperature" class="font-bold"
                        >Temperature</Label
                    >
                    <p>0.6</p>
                </div>
                <Slider
                    class="dark"
                    id="temperature"
                    value={[4]}
                    max={10}
                    step={1}
                />
            </div>
            <div class="flex flex-col gap-4 mb-2">
                <div class="flex justify-between items-center mb-3">
                    <Label for="token" class="font-bold">Max Token</Label>
                    <p>100000</p>
                </div>
                <Slider
                    class="dark"
                    id="token"
                    value={[33]}
                    max={100}
                    step={1}
                />
            </div>
            <div class="flex flex-col gap-4 mb-2">
                <div class="flex justify-between items-center mb-3">
                    <Label for="topp" class="font-bold">Top P</Label>
                    <p>0.6</p>
                </div>
                <Slider class="dark" id="topp" value={[6]} max={10} step={1} />
            </div>
        </div>
        <Sheet.Footer class="fixed bottom-10 w-max">
            <Sheet.Close asChild let:builder>
                <Button builders={[builder]} type="submit">Save changes</Button>
            </Sheet.Close>
        </Sheet.Footer>
    </Sheet.Content>
</Sheet.Root>
