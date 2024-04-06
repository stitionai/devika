<script>
    import * as Sheet from "$lib/components/ui/sheet/index.js";
    import { Button } from "$lib/components/ui/button/index.js";
    import { Slider } from "$lib/components/ui/slider";
    import { Label } from "$lib/components/ui/label";
    import { Separator } from "$lib/components/ui/separator";
    import { Check, Menu, Undo2 } from "lucide-svelte";
</script>

<Sheet.Root>
    <Sheet.Trigger asChild let:builder>
        <Button builders={[builder]} variant="outline">
            <Menu width={20} />
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
                            <Check width={20}/>
                            Save changes
                        </Button>
                    </Sheet.Close>
                    <Button class="rounded-lg gap-2 bg-secondary text-primary">
                        <Undo2 width={20}/>
                        Restore to defaults
                    </Button>
                </div>
            </Sheet.Footer>
        </div>
    </Sheet.Content>
</Sheet.Root>
