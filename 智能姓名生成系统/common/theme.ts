interface UniThemeLike {
	getSystemInfoSync: () => { theme?: string };
	getStorageSync: (key: string) => unknown;
	setNavigationBarColor: (options: { frontColor: string; backgroundColor: string }) => void;
	setBackgroundColor: (options: {
		backgroundColor: string;
		backgroundColorTop: string;
		backgroundColorBottom: string;
	}) => void;
	setTabBarStyle: (options: {
		color: string;
		selectedColor: string;
		backgroundColor: string;
		borderStyle: 'white' | 'black';
	}) => void;
	setStorageSync: (key: string, data: unknown) => void;
	$emit?: (event: string, payload: unknown) => void;
}

declare const uni: UniThemeLike;

export type ThemeMode = 'light' | 'dark' | 'auto';
export type ThemeKey = ThemeMode;

export interface ThemePalette {
	navFront: '#ffffff' | '#000000';
	navBackground: string;
	tabColor: string;
	tabSelected: string;
	tabBackground: string;
	tabBorder: 'white' | 'black';
	pageBackground: string;
	surface: string;
	surfaceMuted: string;
	surfaceSoft: string;
	borderColor: string;
	textPrimary: string;
	textSecondary: string;
	accent: string;
	accentSoft: string;
	accentContrast: string;
	success: string;
	danger: string;
	warning: string;
	shadowSoft: string;
	interactiveActiveBg: string;
	warningSoft: string;
	warningBorder: string;
	disabledBg: string;
	disabledText: string;
	disabledIcon: string;
}

const palettes: Record<'light' | 'dark', ThemePalette> = {
	light: {
		navFront: '#000000',
		navBackground: '#FFFFFF',
		tabColor: '#7A7E83',
		tabSelected: '#4a90e2',
		tabBackground: '#FFFFFF',
		tabBorder: 'black',
		pageBackground: '#F8F8F8',
		surface: '#FFFFFF',
		surfaceMuted: '#F3F5F7',
		surfaceSoft: '#FAFBFC',
		borderColor: '#E6E8EB',
		textPrimary: '#333333',
		textSecondary: '#8A9099',
		accent: '#4A90E2',
		accentSoft: '#EAF4FF',
		accentContrast: '#FFFFFF',
		success: '#2ECC71',
		danger: '#E74C3C',
		warning: '#FF8F4D',
		shadowSoft: '0 2rpx 10rpx rgba(0, 0, 0, 0.05)',
		interactiveActiveBg: '#EAF4FF',
		warningSoft: '#FFF7E8',
		warningBorder: '#FFD8A8',
		disabledBg: '#E6E8EB',
		disabledText: '#A8B0BA',
		disabledIcon: '#C1C7D0'
	},
	dark: {
		navFront: '#FFFFFF',
		navBackground: '#1f1f1f',
		tabColor: '#a2a5b0',
		tabSelected: '#4a90e2',
		tabBackground: '#111111',
		tabBorder: 'white',
		pageBackground: '#111111',
		surface: '#1B1B1B',
		surfaceMuted: '#262626',
		surfaceSoft: '#20252C',
		borderColor: '#343A40',
		textPrimary: '#F5F7FA',
		textSecondary: '#A8B0BA',
		accent: '#6EA8FF',
		accentSoft: '#1D3557',
		accentContrast: '#F5F7FA',
		success: '#4DD78A',
		danger: '#FF7D7D',
		warning: '#FFB86B',
		shadowSoft: '0 4rpx 16rpx rgba(0, 0, 0, 0.24)',
		interactiveActiveBg: '#1D3557',
		warningSoft: '#4A3724',
		warningBorder: '#8A5A30',
		disabledBg: '#2F353C',
		disabledText: '#7F8791',
		disabledIcon: '#666E78'
	}
};

const STORAGE_KEY_MODE = 'theme_mode';

const resolveTheme = (mode: ThemeMode): 'light' | 'dark' => {
	if (mode === 'auto') {
		try {
			const sys = uni.getSystemInfoSync();
			return (sys.theme === 'dark' ? 'dark' : 'light') as 'light' | 'dark';
		} catch (e) {
			return 'light';
		}
	}
	return mode;
};

export const getStoredTheme = (): ThemeMode => {
	try {
		const stored = uni.getStorageSync(STORAGE_KEY_MODE);
		if (stored === 'light' || stored === 'dark' || stored === 'auto') {
			return stored;
		}
	} catch (e) {}
	return 'light';
};

export const getRuntimeThemePalette = (mode?: ThemeMode): ThemePalette => {
	const targetMode = mode || getStoredTheme();
	return palettes[resolveTheme(targetMode)];
};

export const createThemeCssVars = (palette: ThemePalette): Record<string, string> => ({
	'--page-bg': palette.pageBackground,
	'--surface': palette.surface,
	'--surface-muted': palette.surfaceMuted,
	'--surface-soft': palette.surfaceSoft,
	'--border-color': palette.borderColor,
	'--text-primary': palette.textPrimary,
	'--text-secondary': palette.textSecondary,
	'--accent': palette.accent,
	'--accent-soft': palette.accentSoft,
	'--accent-contrast': palette.accentContrast,
	'--success': palette.success,
	'--danger': palette.danger,
	'--warning': palette.warning,
	'--shadow-soft': palette.shadowSoft,
	'--interactive-active-bg': palette.interactiveActiveBg,
	'--warning-soft': palette.warningSoft,
	'--warning-border': palette.warningBorder,
	'--disabled-bg': palette.disabledBg,
	'--disabled-text': palette.disabledText,
	'--disabled-icon': palette.disabledIcon,
});

export const applyTheme = (mode?: ThemeMode) => {
	const targetMode = mode || getStoredTheme();
	const resolved = resolveTheme(targetMode);
	const palette = palettes[resolved];

	try {
		uni.setNavigationBarColor({
			frontColor: palette.navFront,
			backgroundColor: palette.navBackground
		});
	} catch (e) {}

	try {
		uni.setBackgroundColor({
			backgroundColor: palette.pageBackground,
			backgroundColorTop: palette.pageBackground,
			backgroundColorBottom: palette.pageBackground
		});
	} catch (e) {}

	try {
		uni.setTabBarStyle({
			color: palette.tabColor,
			selectedColor: palette.tabSelected,
			backgroundColor: palette.tabBackground,
			borderStyle: palette.tabBorder
		});
	} catch (e) {}

	try {
		uni.setStorageSync(STORAGE_KEY_MODE, targetMode);
		uni.setStorageSync('theme_runtime', resolved);
	} catch (e) {}

	try {
		if (typeof uni.$emit === 'function') {
			uni.$emit('theme-changed', {
				mode: targetMode,
				resolved,
				palette,
			});
		}
	} catch (e) {}
};
