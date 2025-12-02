declare const uni: any;

export type ThemeMode = 'light' | 'dark' | 'auto';

interface Palette {
	navFront: '#ffffff' | '#000000';
	navBackground: string;
	tabColor: string;
	tabSelected: string;
	tabBackground: string;
	tabBorder: 'white' | 'black';
	pageBackground: string;
}

const palettes: Record<'light' | 'dark', Palette> = {
	light: {
		navFront: '#000000',
		navBackground: '#FFFFFF',
		tabColor: '#7A7E83',
		tabSelected: '#4a90e2',
		tabBackground: '#FFFFFF',
		tabBorder: 'black',
		pageBackground: '#F8F8F8'
	},
	dark: {
		navFront: '#FFFFFF',
		navBackground: '#1f1f1f',
		tabColor: '#a2a5b0',
		tabSelected: '#4a90e2',
		tabBackground: '#111111',
		tabBorder: 'white',
		pageBackground: '#000000'
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
};

