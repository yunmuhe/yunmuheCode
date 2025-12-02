declare const process: any;
declare const uni: any;

// 默认服务器地址（根据平台区分）
const DEFAULT_BASE_URL_H5 = 'http://127.0.0.1:5000';
const DEFAULT_BASE_URL_ANDROID = 'http://10.0.2.2:5000';  // Android模拟器特殊地址
const DEFAULT_BASE_URL_IOS = 'http://localhost:5000';

type Nullable<T> = T | null | undefined;

// 获取平台特定的默认服务器地址
const getDefaultBaseUrl = (): string => {
	// 尝试从环境变量读取
	const metaEnv = typeof import.meta !== 'undefined' ? (import.meta as any).env : undefined;
	const processEnv = typeof process !== 'undefined' ? (process as any).env : undefined;
	const candidates: Nullable<string>[] = [
		metaEnv?.VITE_API_BASE_URL,
		metaEnv?.UNI_APP_API_BASE_URL,
		processEnv?.VITE_API_BASE_URL,
		processEnv?.UNI_APP_API_BASE_URL,
	];

	for (const value of candidates) {
		if (value && typeof value === 'string' && value.trim().length > 0) {
			return value.trim();
		}
	}

	// 根据平台返回默认地址
	try {
		const platform = uni.getSystemInfoSync().platform;
		if (platform === 'android') {
			return DEFAULT_BASE_URL_ANDROID;
		} else if (platform === 'ios') {
			return DEFAULT_BASE_URL_IOS;
		}
	} catch (e) {
		console.error('获取平台信息失败:', e);
	}

	return DEFAULT_BASE_URL_H5;
};

// 当前使用的服务器地址
let BASE_URL = getDefaultBaseUrl();

interface RequestOptions {
	url: string;
	method?: 'GET' | 'POST' | 'DELETE';
	data?: Record<string, any>;
}

interface GenerateNamesPayload {
	description: string;
	count: number;
	cultural_style: string;
	gender: string;
	age: string;
	preferred_api?: string;
	use_cache?: boolean;
}

export interface GeneratedName {
	id: string;
	name: string;
	meaning: string;
	source?: string;
	features?: Record<string, any>;
	created_at?: number;
}

export interface GenerateNamesResponse {
	success: boolean;
	names: GeneratedName[];
	error?: string;
	api_name?: string;
	model?: string;
	total_generated?: number;
	successfully_processed?: number;
	description?: string;
	generated_at?: number;
}

export interface OptionsResponse {
	success: boolean;
	options: {
		cultural_styles: string[];
		genders: string[];
		ages: string[];
		apis: string[];
	};
	error?: string;
}

export interface StatsResponse {
	success: boolean;
	stats: Record<string, any>;
	error?: string;
}

const request = <T>(options: RequestOptions): Promise<T> => {
	const { url, method = 'GET', data } = options;

	return new Promise((resolve, reject) => {
		uni.request({
			url: `${BASE_URL}${url}`,
			method,
			data,
			timeout: 15000,
			header: {
				'Content-Type': 'application/json',
			},
			success: (res) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data as T);
				} else {
					const message =
						(typeof res.data === 'object' && res.data && 'error' in res.data && (res.data as any).error) ||
						`请求失败（${res.statusCode}）`;
					reject(new Error(message as string));
				}
			},
			fail: (error) => {
				reject(new Error(error.errMsg || '网络请求失败'));
			},
		});
	});
};

export const fetchBackendOptions = (): Promise<OptionsResponse> => {
	return request<OptionsResponse>({
		url: '/options',
		method: 'GET',
	});
};

export const generateNames = (payload: GenerateNamesPayload): Promise<GenerateNamesResponse> => {
	return request<GenerateNamesResponse>({
		url: '/generate',
		method: 'POST',
		data: payload,
	});
};

export const fetchBackendStats = (): Promise<StatsResponse> => {
	return request<StatsResponse>({
		url: '/stats',
		method: 'GET',
	});
};

export const getApiBaseUrl = () => BASE_URL;

// ==================== 智能服务器发现机制 ====================

const SERVER_URL_KEY = 'custom_server_url';

/**
 * 测试指定服务器地址是否可用
 */
const testServerUrl = (url: string): Promise<boolean> => {
	return new Promise((resolve) => {
		uni.request({
			url: `${url}/health`,
			method: 'GET',
			timeout: 3000,
			success: (res) => {
				if (res.statusCode === 200 && res.data && res.data.status === 'healthy') {
					resolve(true);
				} else {
					resolve(false);
				}
			},
			fail: () => {
				resolve(false);
			}
		});
	});
};

/**
 * 根据平台生成候选服务器地址列表
 */
const getCandidateUrls = (): string[] => {
	const candidates: string[] = [];

	try {
		const platform = uni.getSystemInfoSync().platform;

		if (platform === 'android') {
			// Android模拟器特殊地址
			candidates.push('http://10.0.2.2:5000');

			// 常见局域网IP地址段
			for (let i = 1; i <= 255; i++) {
				candidates.push(`http://192.168.10.${i}:5000`);
			}
			for (let i = 1; i <= 255; i++) {
				candidates.push(`http://192.168.1.${i}:5000`);
			}
		} else if (platform === 'ios') {
			// iOS通常使用localhost或本机IP
			candidates.push('http://localhost:5000');
			candidates.push('http://127.0.0.1:5000');
		} else {
			// H5浏览器环境
			candidates.push('http://127.0.0.1:5000');
			candidates.push('http://localhost:5000');
		}
	} catch (e) {
		console.error('获取平台信息失败:', e);
		candidates.push('http://127.0.0.1:5000');
	}

	return candidates;
};

/**
 * 自动发现可用的服务器地址
 * 1. 检查用户自定义地址
 * 2. 如失效，并行测试候选地址
 * 3. 选择响应最快的可用服务器
 */
export const discoverServer = async (): Promise<string> => {
	console.log('[智能服务器发现] 开始自动发现服务器...');

	// 1. 优先检查用户自定义地址
	try {
		const customUrl = uni.getStorageSync(SERVER_URL_KEY);
		if (customUrl && typeof customUrl === 'string') {
			console.log(`[智能服务器发现] 测试自定义地址: ${customUrl}`);
			const isAvailable = await testServerUrl(customUrl);
			if (isAvailable) {
				console.log(`[智能服务器发现] 自定义地址可用: ${customUrl}`);
				BASE_URL = customUrl;
				return customUrl;
			}
			console.log('[智能服务器发现] 自定义地址不可用，开始扫描...');
		}
	} catch (e) {
		console.error('[智能服务器发现] 读取自定义地址失败:', e);
	}

	// 2. 并行测试候选地址
	const candidates = getCandidateUrls();
	console.log(`[智能服务器发现] 并行测试 ${candidates.length} 个候选地址...`);

	// 使用Promise.race找到第一个响应的服务器
	const testPromises = candidates.map(async (url) => {
		const isAvailable = await testServerUrl(url);
		if (isAvailable) {
			return url;
		}
		return null;
	});

	try {
		// 等待所有测试完成，选择第一个可用的
		const results = await Promise.all(testPromises);
		const availableUrl = results.find(url => url !== null);

		if (availableUrl) {
			console.log(`[智能服务器发现] 发现可用服务器: ${availableUrl}`);
			BASE_URL = availableUrl;
			// 保存为自定义地址（下次优先使用）
			uni.setStorageSync(SERVER_URL_KEY, availableUrl);
			return availableUrl;
		}
	} catch (e) {
		console.error('[智能服务器发现] 服务器扫描失败:', e);
	}

	// 3. 全部失败，返回默认地址
	console.warn('[智能服务器发现] 未找到可用服务器，使用默认地址');
	const defaultUrl = getDefaultBaseUrl();
	BASE_URL = defaultUrl;
	return defaultUrl;
};

/**
 * 手动设置服务器地址
 */
export const setServerUrl = async (url: string): Promise<boolean> => {
	if (!url || typeof url !== 'string') {
		return false;
	}

	// 测试连通性
	const isAvailable = await testServerUrl(url);
	if (isAvailable) {
		BASE_URL = url;
		uni.setStorageSync(SERVER_URL_KEY, url);
		console.log(`[服务器配置] 已保存自定义地址: ${url}`);
		return true;
	}

	console.error(`[服务器配置] 地址不可用: ${url}`);
	return false;
};

/**
 * 获取当前保存的自定义服务器地址
 */
export const getCustomServerUrl = (): string | null => {
	try {
		return uni.getStorageSync(SERVER_URL_KEY) || null;
	} catch (e) {
		return null;
	}
};

/**
 * 清除自定义服务器地址
 */
export const clearCustomServerUrl = (): void => {
	try {
		uni.removeStorageSync(SERVER_URL_KEY);
		BASE_URL = getDefaultBaseUrl();
		console.log('[服务器配置] 已清除自定义地址，恢复默认');
	} catch (e) {
		console.error('[服务器配置] 清除失败:', e);
	}
};

/**
 * 确保服务器地址可用（启动时调用）
 * 如果当前地址不可用，自动触发服务器发现
 */
export const ensureServerUrl = async (): Promise<string> => {
	const isAvailable = await testServerUrl(BASE_URL);
	if (isAvailable) {
		console.log(`[服务器检查] 当前地址可用: ${BASE_URL}`);
		return BASE_URL;
	}

	console.warn(`[服务器检查] 当前地址不可用: ${BASE_URL}，开始自动发现...`);
	return await discoverServer();
};

export const fetchHealth = (): Promise<{ status: string; timestamp: string; version?: string }> => {
	return request<{ status: string; timestamp: string; version?: string }>({
		url: '/health',
		method: 'GET',
	});
};

// -------- Favorites --------
export interface FavoriteItem {
	id: string;
	name: string;
	meaning: string;
	style?: string;
	gender?: string;
	source?: string;
	time?: string;
}

export const getFavorites = (): Promise<{ success: boolean; items: FavoriteItem[] }> => {
	return request({
		url: '/favorites',
		method: 'GET',
	});
};

export const addFavorite = (item: FavoriteItem): Promise<{ success: boolean; item: FavoriteItem }> => {
	return request({
		url: '/favorites',
		method: 'POST',
		data: item,
	});
};

export const deleteFavorites = (ids: string[] | string): Promise<{ success: boolean; deleted: string[] }> => {
	const idsArray = Array.isArray(ids) ? ids : [ids];
	return request({
		url: '/favorites',
		method: 'DELETE',
		data: { ids: idsArray },
	});
};

// -------- History --------
export interface HistoryItem {
	id: string;
	description: string;
	count: number;
	time: string;
	names: string[];
}

export const getHistoryList = (params: { page?: number; page_size?: number; q?: string }) => {
	const page = params.page ?? 1;
	const page_size = params.page_size ?? 10;
	const q = params.q ?? '';
	const url = `/history/list?page=${page}&page_size=${page_size}&q=${encodeURIComponent(q)}`;
	return request<{ success: boolean; items: HistoryItem[]; total: number; page: number; page_size: number }>({
		url,
		method: 'GET',
	});
};

