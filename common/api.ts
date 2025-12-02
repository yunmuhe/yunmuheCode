declare const process: any;
declare const uni: any;

// 固定服务器地址
const BASE_URL = 'http://127.0.0.1:5000';

type Nullable<T> = T | null | undefined;

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
