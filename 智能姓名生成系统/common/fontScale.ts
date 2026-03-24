export type AppFontSize = 'small' | 'medium' | 'large';

interface UniFontScaleLike {
	getStorageSync: (key: string) => unknown;
}

declare const uni: UniFontScaleLike;

const SETTINGS_STORAGE_KEY = 'app_settings';
const DEFAULT_FONT_SIZE: AppFontSize = 'medium';

const isFontSize = (value: unknown): value is AppFontSize => {
	return value === 'small' || value === 'medium' || value === 'large';
};

export const getStoredFontSize = (): AppFontSize => {
	try {
		const stored = uni.getStorageSync(SETTINGS_STORAGE_KEY);
		if (stored && typeof stored === 'object' && 'fontSize' in stored) {
			const fontSize = (stored as { fontSize?: unknown }).fontSize;
			if (isFontSize(fontSize)) {
				return fontSize;
			}
		}
	} catch (error) {}

	return DEFAULT_FONT_SIZE;
};

export const applyFontScale = (fontSize?: AppFontSize): AppFontSize => {
	const nextFontSize = isFontSize(fontSize) ? fontSize : getStoredFontSize();

	if (typeof document !== 'undefined') {
		document.documentElement.setAttribute('data-font-scale', nextFontSize);
		document.body?.setAttribute('data-font-scale', nextFontSize);
	}

	return nextFontSize;
};
