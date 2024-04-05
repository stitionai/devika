import { fontFamily } from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
const config = {
    darkMode: ["class"],
    content: ["./src/**/*.{html,js,svelte,ts}"],
    safelist: ["dark"],
    theme: {
        container: {
            center: true,
            padding: "2rem",
            screens: {
                "2xl": "1400px"
            }
        },
        extend: {
			colors: {
                'primary': 'var(--primary)',
                'background': 'var(--background)',
                'secondary': 'var(--secondary)',
                'tertiary': 'var(--tertiary)',
                'foreground': 'var(--foreground)',
                'foreground-light': 'var(--foreground-light)',
                'foreground-secondary': 'var(--foreground-secondary)',
                'border': 'var(--border)',
                'seperator': 'var(--seperator)',
                'window-outline': 'var(--window-outline)',
                'browser-window-dots': 'var(--browser-window-dots)',
                'browser-window-search': 'var(--browser-window-search)',
                'browser-window-foreground': 'var(--browser-window-foreground)',
                'browser-window-background': 'var(--browser-window-background)',
                'terminal-window-dots': 'var(--terminal-window-dots)',
                'terminal-background': 'var(--terminal-background)',
                'monologue-background': 'var(--monologue-background)',
                'monologue-outline': 'var(--monologue-outline)',
            },
            fontFamily: {
                sans: [...fontFamily.sans]
            }
        }
    },
};

export default config;