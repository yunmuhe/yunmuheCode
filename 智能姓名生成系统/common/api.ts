declare const process:
  | {
      env?: Record<string, string | undefined>;
    }
  | undefined;

interface UniRequestSuccessResult {
  statusCode: number;
  data: unknown;
}

interface UniRequestFailResult {
  errMsg?: string;
}

interface UniRequestOptions {
  url: string;
  method: "GET" | "POST" | "DELETE";
  data?: RequestData;
  timeout: number;
  header: Record<string, string>;
  success: (res: UniRequestSuccessResult) => void;
  fail: (error: UniRequestFailResult) => void;
}

interface UniStorageLike {
  request: (options: UniRequestOptions) => void;
  setStorageSync: (key: string, value: unknown) => void;
  getStorageSync: (key: string) => unknown;
  removeStorageSync: (key: string) => void;
}

declare const uni: UniStorageLike;

const BASE_URL =
  (typeof process !== "undefined" && process?.env?.VITE_API_BASE_URL) ||
  "http://127.0.0.1:5000";
const DEFAULT_REQUEST_TIMEOUT_MS = 120000;
const REQUEST_TIMEOUT_MS = (() => {
  const raw =
    typeof process !== "undefined" ? process?.env?.VITE_API_TIMEOUT_MS : undefined;
  const parsed = Number(raw);
  return Number.isFinite(parsed) && parsed > 0
    ? parsed
    : DEFAULT_REQUEST_TIMEOUT_MS;
})();
const AUTH_TOKEN_KEY = "auth_token";
const AUTH_USER_KEY = "auth_user";

interface RequestOptions {
  url: string;
  method?: "GET" | "POST" | "DELETE";
  data?: RequestData;
  headers?: Record<string, string>;
}

export type RequestData = Record<string, unknown>;
export type ApiFeatureValue = string | number | boolean | null;
export type GeneratedNameFeatures = Record<string, ApiFeatureValue>;

export interface BackendCacheStats {
  active_entries?: number;
  expired_entries?: number;
  total_entries?: number;
}

export interface BackendStats {
  available_apis?: number;
  today_generated?: number;
  cache_stats?: BackendCacheStats;
  api_status?: Record<string, unknown>;
  [key: string]: unknown;
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
  features?: GeneratedNameFeatures;
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
  stats: BackendStats;
  error?: string;
}

export interface AuthUser {
  id: number;
  phone: string;
  role?: "admin" | "user" | string;
  is_enabled?: boolean;
  must_change_password?: boolean;
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
  const { url, method = "GET", data, headers = {} } = options;
  const token = getAuthToken();
  const requestHeaders: Record<string, string> = {
    "Content-Type": "application/json",
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
      timeout: REQUEST_TIMEOUT_MS,
      header: requestHeaders,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T);
          return;
        }
        reject(new Error(getRequestErrorMessage(res.data, res.statusCode)));
      },
      fail: (error) => {
        reject(new Error(error.errMsg || "Network request failed"));
      },
    });
  });
};

const isReadableErrorMessage = (error: string): boolean => {
  const normalized = error.trim();
  if (!normalized) {
    return false;
  }

  return !/^[?？]+$/.test(normalized);
};

const getStatusCodeErrorMessage = (statusCode: number): string => {
  if (statusCode === 400) {
    return "请求参数不正确";
  }

  if (statusCode === 401) {
    return "请先登录后再继续";
  }

  if (statusCode === 403) {
    return "当前账号暂无权限执行此操作";
  }

  if (statusCode === 404) {
    return "请求的资源不存在";
  }

  if (statusCode >= 500) {
    return "服务暂时不可用，请稍后重试";
  }

  return `Request failed (${statusCode})`;
};

const getRequestErrorMessage = (data: unknown, statusCode: number): string => {
  if (typeof data === "object" && data !== null && "error" in data) {
    const error = data.error;
    if (typeof error === "string" && isReadableErrorMessage(error)) {
      return error;
    }
  }

  return getStatusCodeErrorMessage(statusCode);
};

export const getApiBaseUrl = () => BASE_URL;

export const setAuthToken = (token: string) => {
  uni.setStorageSync(AUTH_TOKEN_KEY, token);
};

export const getAuthToken = (): string => {
  const stored = uni.getStorageSync(AUTH_TOKEN_KEY);
  return typeof stored === "string" ? stored : "";
};

export const clearAuthToken = () => {
  uni.removeStorageSync(AUTH_TOKEN_KEY);
  uni.removeStorageSync(AUTH_USER_KEY);
};

export const setAuthUser = (user: AuthUser) => {
  uni.setStorageSync(AUTH_USER_KEY, user);
};

export const getAuthUser = (): AuthUser | null => {
  const stored = uni.getStorageSync(AUTH_USER_KEY);
  return stored && typeof stored === "object" ? (stored as AuthUser) : null;
};

export const authRegister = (payload: {
  phone: string;
  password: string;
  code?: string;
}): Promise<AuthRegisterResponse> => {
  return request<AuthRegisterResponse>({
    url: "/auth/register",
    method: "POST",
    data: payload,
  });
};

export const authLogin = (payload: {
  phone: string;
  password: string;
}): Promise<AuthLoginResponse> => {
  return request<AuthLoginResponse>({
    url: "/auth/login",
    method: "POST",
    data: payload,
  });
};

export const authMe = (): Promise<AuthMeResponse> => {
  return request<AuthMeResponse>({
    url: "/auth/me",
    method: "GET",
  });
};

export const authLogout = (): Promise<{ success: boolean; error?: string }> => {
  return request<{ success: boolean; error?: string }>({
    url: "/auth/logout",
    method: "POST",
  });
};

export const authChangePassword = (payload: {
  old_password: string;
  new_password: string;
}): Promise<{ success: boolean; error?: string }> => {
  return request<{ success: boolean; error?: string }>({
    url: "/auth/change-password",
    method: "POST",
    data: payload,
  });
};

export const fetchBackendOptions = (): Promise<OptionsResponse> => {
  return request<OptionsResponse>({
    url: "/options",
    method: "GET",
  });
};

export const generateNames = (
  payload: GenerateNamesPayload,
): Promise<GenerateNamesResponse> => {
  return request<GenerateNamesResponse>({
    url: "/generate",
    method: "POST",
    data: payload,
  });
};

export const fetchBackendStats = (): Promise<StatsResponse> => {
  return request<StatsResponse>({
    url: "/stats",
    method: "GET",
  });
};

export const fetchHealth = (): Promise<{
  status: string;
  timestamp: string;
  version?: string;
}> => {
  return request<{ status: string; timestamp: string; version?: string }>({
    url: "/health",
    method: "GET",
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

export const getFavorites = (): Promise<{
  success: boolean;
  items: FavoriteItem[];
}> => {
  return request<{
    success: boolean;
    items: FavoriteItem[];
  }>({
    url: "/favorites",
    method: "GET",
  });
};

export const addFavorite = (
  item: FavoriteItem,
): Promise<{ success: boolean; item: FavoriteItem }> => {
  return request<{ success: boolean; item: FavoriteItem }>({
    url: "/favorites",
    method: "POST",
    data: item,
  });
};

export const deleteFavorites = (
  ids: string[] | string,
): Promise<{ success: boolean; deleted: string[] }> => {
  const idsArray = Array.isArray(ids) ? ids : [ids];
  return request<{ success: boolean; deleted: string[] }>({
    url: "/favorites",
    method: "DELETE",
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

export const getHistoryList = (params: {
  page?: number;
  page_size?: number;
  q?: string;
}) => {
  const page = params.page ?? 1;
  const page_size = params.page_size ?? 10;
  const q = params.q ?? "";
  const url = `/history/list?page=${page}&page_size=${page_size}&q=${encodeURIComponent(q)}`;
  return request<{
    success: boolean;
    items: HistoryItem[];
    total: number;
    page: number;
    page_size: number;
  }>({
    url,
    method: "GET",
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

export const getModels = (params?: {
  api?: string;
  refresh?: boolean;
}): Promise<ModelsResponse> => {
  const queryParams = new URLSearchParams();
  if (params?.api) {
    queryParams.append("api", params.api);
  }
  if (params?.refresh) {
    queryParams.append("refresh", "true");
  }
  const queryString = queryParams.toString();
  const url = `/models${queryString ? "?" + queryString : ""}`;
  return request<ModelsResponse>({
    url,
    method: "GET",
  });
};
