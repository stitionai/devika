<script>
    import * as Sheet from "$lib/components/ui/sheet/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Slider } from "$lib/components/ui/slider";
    import { Label } from "$lib/components/ui/label";
    import { Separator } from "$lib/components/ui/separator";
    import * as Select from "$lib/components/ui/select/index.js";

    import { searchEngineList } from "$lib/store";
    import { get } from "svelte/store";

    const engines = [
        { value: "google", label: "Google" },
        { value: "bing", label: "Bing" },
        { value: "duckduckgo", label: "DuckDuckGo" },
    ];

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
            <svg
                width="20"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="rgba(173,184,194,1)"
                ><path d="M3 4H21V6H3V4ZM3 11H21V13H3V11ZM3 18H21V20H3V18Z"
                ></path></svg
            >
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
            <Select.Content class="p-0">
              <Select.Group>
                {#each engines as engine}
                  <Select.Item class="outline-none border-none w-[280px] px-3 py-3 text-sm font-semibold border-2 text-tertiary-foreground bg-secondary" value={engine.value} label={engine.label} on:click={() => selectSearchEngine(engine.value)}
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
        <div class="relative w-full h-2/3">
            <Sheet.Footer class="block bottom-16  w-full absolute">
                <div class="flex flex-col gap-4 mb-2">
                    <Sheet.Close asChild let:builder>
                        <Button class="rounded-lg gap-2 text-black" builders={[builder]} type="submit">
                            <svg width=24 xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="rgba(0,0,0,1)"><path d="M9.9997 15.1709L19.1921 5.97852L20.6063 7.39273L9.9997 17.9993L3.63574 11.6354L5.04996 10.2212L9.9997 15.1709Z"></path></svg>
                            Save changes
                        </Button>
                    </Sheet.Close>
                    <Button class="rounded-lg gap-2 bg-secondary text-primary">
                        <svg width=20 xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="rgba(255,255,255,1)"><path d="M5.82843 6.99955L8.36396 9.53509L6.94975 10.9493L2 5.99955L6.94975 1.0498L8.36396 2.46402L5.82843 4.99955H13C17.4183 4.99955 21 8.58127 21 12.9996C21 17.4178 17.4183 20.9996 13 20.9996H4V18.9996H13C16.3137 18.9996 19 16.3133 19 12.9996C19 9.68584 16.3137 6.99955 13 6.99955H5.82843Z"></path></svg>
                        Restore to defaults</Button>
                </div>
            </Sheet.Footer>
        </div>
    </Sheet.Content>
</Sheet.Root>
