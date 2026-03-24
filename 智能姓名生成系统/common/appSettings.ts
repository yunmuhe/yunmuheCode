import type { ThemeMode } from './theme';
import type { AppFontSize } from './fontScale';

export type StylePreference = 'chinese_modern' | 'chinese_traditional' | 'fantasy';

export interface LocalSettings {
	generateCount: number;
	stylePreference: StylePreference;
	autoCopy: boolean;
	theme: ThemeMode;
	fontSize: AppFontSize;
	animation: boolean;
	retentionTime: '7天' | '30天' | '永久';
	autoClean: boolean;
	cloudSync: boolean;
}

export const SETTINGS_STORAGE_KEY = 'app_settings';

export const STYLE_OPTIONS: ReadonlyArray<{ label: string; value: StylePreference }> = [
	{ label: '现代中文', value: 'chinese_modern' },
	{ label: '传统中文', value: 'chinese_traditional' },
	{ label: '奇幻风格', value: 'fantasy' },
];

export const FONT_SIZE_OPTIONS: ReadonlyArray<{ label: string; value: AppFontSize }> = [
	{ label: '小', value: 'small' },
	{ label: '中', value: 'medium' },
	{ label: '大', value: 'large' },
];

export const THEME_OPTIONS: ReadonlyArray<{ label: string; value: ThemeMode }> = [
	{ label: '浅色', value: 'light' },
	{ label: '深色', value: 'dark' },
	{ label: '自动', value: 'auto' },
];

export const RETENTION_OPTIONS = ['7天', '30天', '永久'] as const;

export const DEFAULT_SETTINGS: LocalSettings = {
	generateCount: 3,
	stylePreference: 'chinese_modern',
	autoCopy: true,
	theme: 'light',
	fontSize: 'medium',
	animation: true,
	retentionTime: '30天',
	autoClean: false,
	cloudSync: true,
};

const isStylePreference = (value: unknown): value is StylePreference =>
	value === 'chinese_modern' || value === 'chinese_traditional' || value === 'fantasy';

const isThemeMode = (value: unknown): value is ThemeMode =>
	value === 'light' || value === 'dark' || value === 'auto';

const isFontSize = (value: unknown): value is AppFontSize =>
	value === 'small' || value === 'medium' || value === 'large';

const isRetentionTime = (value: unknown): value is LocalSettings['retentionTime'] =>
	value === '7天' || value === '30天' || value === '永久';

export const readSettings = (): LocalSettings => {
	try {
		const stored = uni.getStorageSync(SETTINGS_STORAGE_KEY);
		if (!stored || typeof stored !== 'object') {
			return { ...DEFAULT_SETTINGS };
		}

		const record = stored as Partial<Record<keyof LocalSettings, unknown>>;
		return {
			generateCount:
				typeof record.generateCount === 'number'
					? Math.min(10, Math.max(1, record.generateCount))
					: DEFAULT_SETTINGS.generateCount,
			stylePreference: isStylePreference(record.stylePreference)
				? record.stylePreference
				: DEFAULT_SETTINGS.stylePreference,
			autoCopy:
				typeof record.autoCopy === 'boolean'
					? record.autoCopy
					: DEFAULT_SETTINGS.autoCopy,
			theme: isThemeMode(record.theme) ? record.theme : DEFAULT_SETTINGS.theme,
			fontSize: isFontSize(record.fontSize) ? record.fontSize : DEFAULT_SETTINGS.fontSize,
			animation:
				typeof record.animation === 'boolean'
					? record.animation
					: DEFAULT_SETTINGS.animation,
			retentionTime: isRetentionTime(record.retentionTime)
				? record.retentionTime
				: DEFAULT_SETTINGS.retentionTime,
			autoClean:
				typeof record.autoClean === 'boolean'
					? record.autoClean
					: DEFAULT_SETTINGS.autoClean,
			cloudSync:
				typeof record.cloudSync === 'boolean'
					? record.cloudSync
					: DEFAULT_SETTINGS.cloudSync,
		};
	} catch (error) {
		return { ...DEFAULT_SETTINGS };
	}
};

export const readAppSettings = readSettings;

export const writeSettings = (settings: LocalSettings): void => {
	try {
		uni.setStorageSync(SETTINGS_STORAGE_KEY, { ...settings });
	} catch (error) {}
};

export const patchSettings = (patch: Partial<LocalSettings>): LocalSettings => {
	const nextSettings = {
		...readSettings(),
		...patch,
	};

	writeSettings(nextSettings);
	return nextSettings;
};

export const updateAppSettings = patchSettings;

export const getStyleLabel = (value: StylePreference): string =>
	STYLE_OPTIONS.find((item) => item.value === value)?.label || STYLE_OPTIONS[0].label;

export const getThemeLabel = (value: ThemeMode): string =>
	THEME_OPTIONS.find((item) => item.value === value)?.label || THEME_OPTIONS[0].label;

export const getFontSizeLabel = (value: AppFontSize): string =>
	FONT_SIZE_OPTIONS.find((item) => item.value === value)?.label || FONT_SIZE_OPTIONS[1].label;
