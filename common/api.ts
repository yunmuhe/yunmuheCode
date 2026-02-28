declare const process: any;
declare const uni: any;

const BASE_URL =
	(typeof process !== 'undefined' && process?.env?.VITE_API_BASE_URL) ||
	'http://127.0.0.1:5000';
const AUTH_TOKEN_KEY = 'auth_token';
const AUTH_USER_KEY = 'auth_user';

interface RequestOptions {
	url: string;
	method?: 'GET' | 'POST' | 'DELETE';
	data?: Record<string, any>;
	headers?: Record<string, string>;
}

interface GenerateNamesPayload {
	description: string;
	count: number;
	cultural_style: string;
	gender: string;
	age: string;
	preferred_api?: string;
	use_cache?: boolean;
	model?: string;
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

export interface AuthUser {
	id: number;
	phone: string;
	created_at?: string;
	updated_at?: string;
	last_login_at?: string;
}

export interface AuthRegisterResponse {
	success: boolean;
	user?: AuthUser;
	error?: string;
}

export interface AuthLoginResponse {
	success: boolean;
	token?: string;
	expires_at?: string;
	user?: AuthUser;
	error?: string;
}

export interface AuthMeResponse {
	success: boolean;
	user?: AuthUser;
	error?: string;
}

const request = <T>(options: RequestOptions): Promise<T> => {
	const { url, method = 'GET', data, headers = {} } = options;
	const token = getAuthToken();
	const requestHeaders: Record<string, string> = {
		'Content-Type': 'application/json',
		...headers,
	};

	if (token && !requestHeaders.Authorization) {
		requestHeaders.Authorization = `Bearer ${token}`;
	}

	return new Promise((resolve, reject) => {
		uni.request({
			url: `${BASE_URL}${url}`,
			method,
			data,
			timeout: 15000,
			header: requestHeaders,
			success: (res: any) => {
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data as T);
					return;
				}
				const message =
					(typeof res.data === 'object' && res.data && 'error' in res.data && (res.data as any).error) ||
					`Request failed (${res.statusCode})`;
				reject(new Error(message as string));
			},
			fail: (error: any) => {
				reject(new Error(error.errMsg || 'Network request failed'));
			},
		});
	});
};

export const getApiBaseUrl = () => BASE_URL;

export const setAuthToken = (token: string) => {
	uni.setStorageSync(AUTH_TOKEN_KEY, token);
};

export const getAuthToken = (): string => {
	return uni.getStorageSync(AUTH_TOKEN_KEY) || '';
};

export const clearAuthToken = () => {
	uni.removeStorageSync(AUTH_TOKEN_KEY);
	uni.removeStorageSync(AUTH_USER_KEY);
};

export const setAuthUser = (user: AuthUser) => {
	uni.setStorageSync(AUTH_USER_KEY, user);
};

export const getAuthUser = (): AuthUser | null => {
	return uni.getStorageSync(AUTH_USER_KEY) || null;
};

export const authRegister = (payload: { phone: string; password: string; code?: string }): Promise<AuthRegisterResponse> => {
	return request<AuthRegisterResponse>({
		url: '/auth/register',
		method: 'POST',
		data: payload,
	});
};

export const authLogin = (payload: { phone: string; password: string }): Promise<AuthLoginResponse> => {
	return request<AuthLoginResponse>({
		url: '/auth/login',
		method: 'POST',
		data: payload,
	});
};

export const authMe = (): Promise<AuthMeResponse> => {
	return request<AuthMeResponse>({
		url: '/auth/me',
		method: 'GET',
	});
};

export const authLogout = (): Promise<{ success: boolean; error?: string }> => {
	return request<{ success: boolean; error?: string }>({
		url: '/auth/logout',
		method: 'POST',
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

export const fetchHealth = (): Promise<{ status: string; timestamp: string; version?: string }> => {
	return request<{ status: string; timestamp: string; version?: string }>({
		url: '/health',
		method: 'GET',
	});
};

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

export interface ModelInfo {
	id: string;
	name: string;
	description: string;
	is_default: boolean;
}

export interface ModelsResponse {
	success: boolean;
	models?: Record<string, ModelInfo[]>;
	platforms?: string[];
	total_count?: number;
	api?: string;
	count?: number;
	error?: string;
}

export const getModels = (params?: { api?: string; refresh?: boolean }): Promise<ModelsResponse> => {
	const queryParams = new URLSearchParams();
	if (params?.api) {
		queryParams.append('api', params.api);
	}
	if (params?.refresh) {
		queryParams.append('refresh', 'true');
	}
	const queryString = queryParams.toString();
	const url = `/models${queryString ? '?' + queryString : ''}`;
	return request<ModelsResponse>({
		url,
		method: 'GET',
	});
};
