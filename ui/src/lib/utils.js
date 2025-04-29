import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { cubicOut } from "svelte/easing";

/**
 * Merges multiple class names or class name arrays into a single string using the `twMerge` function.
 *
 * @param {...(string|string[])} inputs - A rest parameter that accepts one or more strings or arrays of strings representing class names.
 * @returns {string} - A single string containing all the merged class names, properly concatenated and deduplicated.
 */
export function cn(...inputs) {
	return twMerge(clsx(inputs));
}

/**
 * Creates a transformation animation that scales and translates an element over time.
 *
 * @param {HTMLElement} node - The target HTML element to animate.
 * @param {Object} [params] - Optional parameters for the animation.
 * @param {number} [params.y=-8] - Vertical translation distance in pixels.
 * @param {number} [params.x=0] - Horizontal translation distance in pixels.
 * @param {number} [params.start=0.95] - Starting scale value.
 * @param {number} [params.duration=150] - Duration of the animation in milliseconds.
 * @returns {Object} An object containing the animation properties: duration, delay, css, and easing.
 */
export const flyAndScale = (
	node,
	params = { y: -8, x: 0, start: 0.95, duration: 150 }
) => {
	const style = getComputedStyle(node);
	const transform = style.transform === "none" ? "" : style.transform;

	/**
	 * Converts a value from one scale to another.
	 *
	 * @param {number} valueA - The value on the original scale to be converted.
	 * @param {[number, number]} scaleA - An array representing the minimum and maximum values of the original scale.
	 * @param {[number, number]} scaleB - An array representing the minimum and maximum values of the target scale.
	 * @returns {number} The equivalent value on the new scale.
	 *
	 * @throws {Error} If any of the input scales are invalid (e.g., minA >= maxA or minB >= maxB).
	 */
	const scaleConversion = (valueA, scaleA, scaleB) => {
		const [minA, maxA] = scaleA;
		const [minB, maxB] = scaleB;

		const percentage = (valueA - minA) / (maxA - minA);
		const valueB = percentage * (maxB - minB) + minB;

		return valueB;
	};

	/**
	 * Converts an object representing CSS styles into a string formatted for use in inline styles.
	 *
	 * @param {Object} style - An object where keys are CSS property names and values are corresponding property values.
	 * @returns {string} A string of CSS properties and values, suitable for use as inline styles.
	 * @throws {TypeError} If the input is not an object.
	 */
	const styleToString = (style) => {
		return Object.keys(style).reduce((str, key) => {
			if (style[key] === undefined) return str;
			return str + `${key}:${style[key]};`;
		}, "");
	};

	return {
		duration: params.duration ?? 200,
		delay: 0,
		css: (t) => {
			const y = scaleConversion(t, [0, 1], [params.y ?? 5, 0]);
			const x = scaleConversion(t, [0, 1], [params.x ?? 0, 0]);
			const scale = scaleConversion(t, [0, 1], [params.start ?? 0.95, 1]);

			return styleToString({
				transform: `${transform} translate3d(${x}px, ${y}px, 0) scale(${scale})`,
				opacity: t
			});
		},
		easing: cubicOut
	};
};