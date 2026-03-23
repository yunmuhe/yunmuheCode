<template>
    <view class="settings-container" :style="themeVars">
        <!-- 顶部导航栏-->
        <CustomNavBar title="设置" />

        <!-- 用户信息区域 -->
        <view class="user-section">
            <view class="user-avatar" @click="handleUserClick">
                <image
                        v-if="isLogin"
                    class="avatar-image"
                    :src="
                        userInfo.avatar ||
                        '/static/common/default-avatar.svg'
                    "
                    mode="aspectFill"
                />
                <uni-icons v-else type="contact" size="60" :color="themePalette.textSecondary" />
            </view>
            <view class="user-info">
                <text v-if="isLogin" class="user-name">{{
                    maskedPhone
                }}</text>
                <text v-else class="login-text" @click="handleLogin"
                    >点击登录</text>
                <text v-if="isLogin && userInfo.isAdmin" class="vip-tag"
                    >管理员</text>
                <text v-else-if="isLogin" class="member-tag">普通会员</text>
            </view>
        </view>

        <!-- 智能体连接与状态-->
        <view class="settings-group">
            <text class="group-title">智能体连接</text>
            <view class="settings-item">
                <text class="item-label">当前地址</text>
                <text
                    class="item-value"
                    style="font-size: 24rpx; word-break: break-all"
                    >{{ apiBaseUrl }}</text>
            </view>
            <view class="settings-item">
                <text class="item-label">连接状态</text>
                <view style="display: flex; align-items: center">
                    <view
                        :style="{
                            width: '14rpx',
                            height: '14rpx',
                            borderRadius: '50%',
                            backgroundColor: health.ok ? themePalette.success : themePalette.danger,
                            marginRight: '12rpx',
                        }"
                    ></view>
                    <text class="item-value">{{
                        health.ok ? "已连接" : "未连接"
                    }}</text>
                    <text
                        v-if="health.version"
                        :style="{ marginLeft: '12rpx', color: themePalette.textSecondary }"
                        >v{{ health.version }}</text
                    >
                    <button
                        class="stats-btn"
                        style="margin-left: 16rpx"
                        size="mini"
                        @click="refreshHealth"
                        :disabled="health.loading"
                    >
                        {{ health.loading ? "检查中..." : "重新检查" }}
                    </button>
                </view>
            </view>
        </view>

        <!-- 偏好设置分组（含默认API提供商） -->
        <view class="settings-group">
            <text class="group-title">偏好设置</text>
            <view class="settings-item">
                <text class="item-label">默认生成数量</text>
                <uni-number-box
                    v-model="settings.generateCount"
                    :min="1"
                    :max="10"
                    @change="handleGenerateCountChange"
                />
            </view>
            <view class="settings-item" v-if="apiOptions.length">
                <text class="item-label">默认API提供商</text>
                <picker
                    mode="selector"
                    :range="apiOptionLabels"
                    :value="apiIndex"
                    @change="handleApiChange"
                >
                    <view class="picker-value">{{
                        apiOptionLabels[apiIndex]
                    }}</view>
                </picker>
            </view>
            <view class="settings-item">
                <text class="item-label">默认风格偏好</text>
                <uni-segmented-control
                    :current="styleIndex"
                    :values="styles"
                    @clickItem="handleStyleChange"
                />
            </view>
            <view class="settings-item">
                <text class="item-label">自动复制结果</text>
                <switch
                    :checked="settings.autoCopy"
                    @change="handleAutoCopyChange"
                    :color="themePalette.accent"
                />
            </view>
        </view>

        <!-- 显示设置分组 -->
        <view class="settings-group">
            <text class="group-title">显示设置</text>
            <view class="settings-item">
                <text class="item-label">主题模式</text>
                <radio-group @change="handleThemeChange">
                    <label
                        class="radio-item"
                        v-for="item in themes"
                        :key="item.value"
                    >
                        <radio
                            :value="item.value"
                            :checked="settings.theme === item.value"
                        />
                        <text>{{ item.name }}</text>
                    </label>
                </radio-group>
            </view>
            <view class="settings-item">
                <text class="item-label">字体大小</text>
                <slider
                    :value="fontSizeIndex"
                    :min="0"
                    :max="2"
                    @change="handleFontSizeChange"
                    :step="1"
                    :activeColor="themePalette.accent"
                />
                <view class="slider-labels">
                    <text>小</text>
                    <text>中</text>
                    <text>大</text>
                </view>
            </view>
            <view class="settings-item">
                <text class="item-label">动画效果</text>
                <switch
                    :checked="settings.animation"
                    @change="handleAnimationChange"
                    :color="themePalette.accent"
                />
            </view>
        </view>

        <!-- 存储设置分组 -->
        <view class="settings-group">
            <text class="group-title">存储设置</text>
            <view class="settings-item">
                <text class="item-label">历史记录保留时间</text>
                <picker
                    mode="selector"
                    :range="retentionTimes"
                    :value="retentionIndex"
                    @change="handleRetentionChange"
                >
                    <view class="picker-value">
                        {{ retentionTimes[retentionIndex] }}
                        <uni-icons type="arrowright" size="16" :color="themePalette.textSecondary" />
                    </view>
                </picker>
            </view>
            <view class="settings-item">
                <text class="item-label">自动清理设置</text>
                <switch
                    :checked="settings.autoClean"
                    @change="handleAutoCleanChange"
                    :color="themePalette.accent"
                />
            </view>
            <view class="settings-item">
                <text class="item-label">数据备份与恢复</text>
                <button
                    type="default"
                    size="mini"
                    @click="handleBackup"
                    class="backup-btn"
                >
                    备份
                </button>
            </view>
        </view>

        <!-- 账户与数据分组-->
        <view class="settings-group">
            <text class="group-title">账户与数据</text>
            <view class="settings-item">
                <text class="item-label">用户名</text>
                <text class="item-value">{{
                    isLogin ? maskedPhone : "未登录"
                }}</text>
            </view>
            <view class="settings-item" v-if="isLogin && userInfo.isAdmin">
                <text class="item-label">后台管理</text>
                <button
                    type="default"
                    size="mini"
                    @click="goAdmin"
                    class="stats-btn"
                >
                    进入
                </button>
            </view>
            <view class="settings-item">
                <text class="item-label">{{
                    isLogin ? "退出登录" : "账号登录"
                }}</text>
                <button
                    type="default"
                    size="mini"
                    @click="isLogin ? handleLogout() : handleLogin()"
                    class="clear-btn"
                >
                    {{ isLogin ? "退出" : "登录" }}
                </button>
            </view>
            <view class="settings-item">
                <text class="item-label">云端同步</text>
                <switch
                    :checked="settings.cloudSync"
                    @change="handleCloudSyncChange"
                    :color="themePalette.accent"
                />
            </view>
            <view class="settings-item">
                <text class="item-label">数据统计</text>
                <button
                    type="default"
                    size="mini"
                    @click="handleViewStats"
                    class="stats-btn"
                >
                    查看
                </button>
            </view>
            <view class="settings-item">
                <text class="item-label">清除缓存</text>
                <button
                    type="default"
                    size="mini"
                    @click="handleClearCache"
                    class="clear-btn"
                >
                    清除
                </button>
            </view>
        </view>

        <!-- 关于与支持分组-->
        <view class="settings-group">
            <text class="group-title">关于与支持</text>
            <view class="settings-item">
                <text class="item-label">应用版本</text>
                <text class="item-value">v1.2.0</text>
            </view>
            <view class="settings-item" @click="handleUserAgreement">
                <text class="item-label">用户协议</text>
                <uni-icons type="arrowright" size="16" :color="themePalette.textSecondary" />
            </view>
            <view class="settings-item" @click="handlePrivacyPolicy">
                <text class="item-label">隐私政策</text>
                <uni-icons type="arrowright" size="16" :color="themePalette.textSecondary" />
            </view>
            <view class="settings-item" @click="handleFeedback">
                <text class="item-label">反馈与帮助</text>
                <uni-icons type="arrowright" size="16" :color="themePalette.textSecondary" />
            </view>
            <view class="settings-item" @click="handleShareApp">
                <text class="item-label">分享应用</text>
                <uni-icons type="arrowright" size="16" :color="themePalette.textSecondary" />
            </view>
        </view>
    </view>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import {
    authMe,
    authLogout,
    clearAuthToken,
    fetchBackendOptions,
    fetchBackendStats,
    fetchHealth,
    getAuthUser,
    getApiBaseUrl,
    setAuthUser,
    type AuthUser,
    type BackendStats,
} from "../../common/api";
import { applyTheme, createThemeCssVars, getRuntimeThemePalette, getStoredTheme, ThemeMode, type ThemePalette } from "../../common/theme";
import { maskPhoneNumber } from "../../common/phoneMask";
import CustomNavBar from "../../components/CustomNavBar.vue";
import uniIcons from "@/uni_modules/uni-icons/components/uni-icons/uni-icons.vue";
import uniNumberBox from "@/uni_modules/uni-number-box/components/uni-number-box/uni-number-box.vue";
import uniSegmentedControl from "@/uni_modules/uni-segmented-control/components/uni-segmented-control/uni-segmented-control.vue";

type LocalSettings = {
    generateCount: number;
    stylePreference: string;
    autoCopy: boolean;
    theme: ThemeMode;
    fontSize: "small" | "medium" | "large";
    animation: boolean;
    retentionTime: string;
    autoClean: boolean;
    cloudSync: boolean;
};

interface SegmentedControlClickEvent {
    currentIndex: number;
}

interface ToggleChangeEvent {
    detail: {
        value: boolean;
    };
}

interface RadioGroupChangeEvent {
    detail: {
        value: string;
    };
}

interface RangeChangeEvent {
    detail: {
        value: number;
    };
}

interface PickerChangeEvent {
    detail: {
        value: string | number;
    };
}

interface ModalConfirmResult {
    confirm?: boolean;
}

const SETTINGS_STORAGE_KEY = "app_settings";
const STYLE_OPTIONS = [
    { label: "现代中文", value: "chinese_modern" },
    { label: "传统中文", value: "chinese_traditional" },
    { label: "奇幻风格", value: "fantasy" },
];
const STYLE_VALUES = STYLE_OPTIONS.map((item) => item.value);
const DEFAULT_SETTINGS: LocalSettings = {
    generateCount: 3,
    stylePreference: "chinese_modern",
    autoCopy: true,
    theme: "light",
    fontSize: "medium",
    animation: true,
    retentionTime: "30天",
    autoClean: false,
    cloudSync: true,
};

const isLogin = ref(false);
const userInfo = reactive({
    nickname: "用户名",
    phone: "",
    avatar: "",
    vip: false,
    isAdmin: false,
});
const maskedPhone = computed(() => maskPhoneNumber(userInfo.phone));

const settings = reactive({
    ...DEFAULT_SETTINGS,
});

const styles = STYLE_OPTIONS.map((item) => item.label);
const styleIndex = ref(0);

// 接入后端：可用API与健康、统计
const apiBaseUrl = getApiBaseUrl();
const apiOptions = ref<string[]>([]);
const apiIndex = ref(0);
const apiLabelMap: Record<string, string> = {
    paiou: "派欧",
    aistudio: "Aistudio",
    baidu: "百度千帆",
    baishan: "白山智算",
    siliconflow: "SiliconFlow",
    aliyun: "阿里云",
    mock: "模拟接口",
};
const apiOptionLabels = computed(() =>
    apiOptions.value.map((k) => apiLabelMap[k] || k),
);

const health = ref({ ok: false, version: "", loading: false });
const stats = ref<BackendStats | null>(null);

const themes = [
    { name: "浅色", value: "light" },
    { name: "深色", value: "dark" },
    { name: "自动", value: "auto" },
];

const fontSizes: LocalSettings["fontSize"][] = ["small", "medium", "large"];
const fontSizeIndex = ref(1);

const retentionTimes = ["7天", "30天", "永久"] as const;
const retentionIndex = ref(1);
const themePalette = ref<ThemePalette>(getRuntimeThemePalette());
const themeVars = computed(() => createThemeCssVars(themePalette.value));

const syncTheme = () => {
    themePalette.value = getRuntimeThemePalette();
};

const persistSettings = () => {
    try {
        uni.setStorageSync(SETTINGS_STORAGE_KEY, { ...settings });
    } catch (e) {}
};

const restoreSettings = () => {
    try {
        const stored = uni.getStorageSync(SETTINGS_STORAGE_KEY);
        if (!stored || typeof stored !== "object") {
            return;
        }
        const settingsRecord = stored as Partial<Record<keyof LocalSettings, unknown>>;

        settings.generateCount =
            typeof settingsRecord.generateCount === "number"
                ? Math.min(10, Math.max(1, settingsRecord.generateCount))
                : DEFAULT_SETTINGS.generateCount;
        settings.stylePreference =
            typeof settingsRecord.stylePreference === "string" &&
            STYLE_VALUES.includes(settingsRecord.stylePreference)
            ? settingsRecord.stylePreference
            : DEFAULT_SETTINGS.stylePreference;
        settings.autoCopy =
            typeof settingsRecord.autoCopy === "boolean"
                ? settingsRecord.autoCopy
                : DEFAULT_SETTINGS.autoCopy;
        settings.theme =
            settingsRecord.theme === "light" ||
            settingsRecord.theme === "dark" ||
            settingsRecord.theme === "auto"
                ? settingsRecord.theme
                : DEFAULT_SETTINGS.theme;
        settings.fontSize =
            settingsRecord.fontSize === "small" ||
            settingsRecord.fontSize === "medium" ||
            settingsRecord.fontSize === "large"
            ? settingsRecord.fontSize
            : DEFAULT_SETTINGS.fontSize;
        settings.animation =
            typeof settingsRecord.animation === "boolean"
                ? settingsRecord.animation
                : DEFAULT_SETTINGS.animation;
        settings.retentionTime =
            settingsRecord.retentionTime === "7天" ||
            settingsRecord.retentionTime === "30天" ||
            settingsRecord.retentionTime === "永久"
            ? settingsRecord.retentionTime
            : DEFAULT_SETTINGS.retentionTime;
        settings.autoClean =
            typeof settingsRecord.autoClean === "boolean"
                ? settingsRecord.autoClean
                : DEFAULT_SETTINGS.autoClean;
        settings.cloudSync =
            typeof settingsRecord.cloudSync === "boolean"
                ? settingsRecord.cloudSync
                : DEFAULT_SETTINGS.cloudSync;
    } catch (e) {}
};

const syncUiStateFromSettings = () => {
    styleIndex.value = Math.max(
        0,
        STYLE_VALUES.indexOf(settings.stylePreference),
    );
    fontSizeIndex.value = Math.max(0, fontSizes.indexOf(settings.fontSize));
    retentionIndex.value = Math.max(
        0,
        retentionTimes.indexOf(settings.retentionTime),
    );
};

const handleUserClick = () => {
    if (!isLogin.value) {
        handleLogin();
    } else {
        // 跳转到用户详情页
    }
};

const handleLogin = () => {
    uni.navigateTo({
        url: "/pages/Auth/Auth",
    });
};

const applyAuthUser = (user: AuthUser | null | undefined) => {
    if (!user || !user.phone) {
        isLogin.value = false;
        userInfo.phone = "";
        userInfo.isAdmin = false;
        return;
    }
    isLogin.value = true;
    userInfo.phone = String(user.phone);
    userInfo.isAdmin = user.role === "admin";
};

const syncAuthState = async () => {
    const cachedUser = getAuthUser();
    applyAuthUser(cachedUser);
    if (!cachedUser) return;

    try {
        const res = await authMe();
        if (res.success && res.user) {
            setAuthUser(res.user);
            applyAuthUser(res.user);
            return;
        }
    } catch (e) {}

    clearAuthToken();
    applyAuthUser(null);
};

const handleStyleChange = (e: SegmentedControlClickEvent) => {
    styleIndex.value = e.currentIndex;
    settings.stylePreference =
        STYLE_VALUES[e.currentIndex] || DEFAULT_SETTINGS.stylePreference;
    persistSettings();
};

const handleGenerateCountChange = (value: number | { value?: number }) => {
    const nextValue =
        typeof value === "number" ? value : Number(value?.value ?? settings.generateCount);
    settings.generateCount = Math.min(10, Math.max(1, nextValue || DEFAULT_SETTINGS.generateCount));
    persistSettings();
};

const handleAutoCopyChange = (e: ToggleChangeEvent) => {
    settings.autoCopy = e.detail.value;
    persistSettings();
};

const syncThemeFromStorage = () => {
    const storedTheme = getStoredTheme();
    settings.theme = storedTheme;
    applyTheme(storedTheme);
    syncTheme();
};

const handleThemeChange = (e: RadioGroupChangeEvent) => {
    const value = (e?.detail?.value ?? "light") as ThemeMode;
    settings.theme = value;
    applyTheme(value);
    syncTheme();
    persistSettings();
};

const handleFontSizeChange = (e: RangeChangeEvent) => {
    fontSizeIndex.value = e.detail.value;
    settings.fontSize = fontSizes[e.detail.value] || DEFAULT_SETTINGS.fontSize;
    persistSettings();
};

const handleAnimationChange = (e: ToggleChangeEvent) => {
    settings.animation = e.detail.value;
    persistSettings();
};

const handleRetentionChange = (e: PickerChangeEvent) => {
    retentionIndex.value = Number(e.detail.value) || 0;
    settings.retentionTime =
        retentionTimes[retentionIndex.value] || DEFAULT_SETTINGS.retentionTime;
    persistSettings();
};

const handleAutoCleanChange = (e: ToggleChangeEvent) => {
    settings.autoClean = e.detail.value;
    persistSettings();
};

const handleBackup = () => {
    uni.showToast({
        title: "备份恢复功能开发中",
        icon: "none",
    });
};

const handleCloudSyncChange = (e: ToggleChangeEvent) => {
    settings.cloudSync = e.detail.value;
    persistSettings();
    uni.showToast({
        title: "仅保存同步偏好，云端同步暂未接入",
        icon: "none",
    });
};

const handleLogout = async () => {
    try {
        await authLogout();
    } catch (e) {}
    clearAuthToken();
    applyAuthUser(null);
    uni.showToast({
        title: "已退出登录",
        icon: "success",
    });
};

const goAdmin = () => {
    uni.navigateTo({
        url: "/pages/Admin/Admin",
    });
};

const handleViewStats = () => {
    // 显示简要统计信息
    if (!stats.value) {
        uni.showToast({ title: "暂无统计数据", icon: "none" });
        return;
    }
    uni.showModal({
        title: "系统统计",
        content: `可用API：${stats.value.available_apis}\n缓存条目：${stats.value.cache_stats?.active_entries ?? "-"}\nAPI状态：${Object.keys(stats.value.api_status || {}).length} 个`,
        showCancel: false,
    });
};

const handleClearCache = () => {
    uni.showModal({
        title: "提示",
        content: "确定要清除缓存吗？",
        success: (res: ModalConfirmResult) => {
            if (res.confirm) {
                // 目前后端未提供清理接口，可在此扩展/cache/clear
                uni.showToast({ title: "暂不支持，后端待扩展", icon: "none" });
            }
        },
    });
};

const handleUserAgreement = () => {
    uni.navigateTo({
        url: "/pages/agreement/agreement?type=user",
    });
};

const handlePrivacyPolicy = () => {
    uni.navigateTo({
        url: "/pages/agreement/agreement?type=privacy",
    });
};

const handleFeedback = () => {
    uni.navigateTo({
        url: "/pages/feedback/feedback",
    });
};

const handleShareApp = () => {
    if (typeof uni.share !== "function") {
        uni.showToast({
            title: "当前环境暂不支持分享",
            icon: "none",
        });
        return;
    }

    uni.share({
        provider: "weixin",
        type: 0,
        title: "分享应用",
        success: () => {
            uni.showToast({
                title: "分享成功",
                icon: "success",
            });
        },
    });
};

// 载入后端选项、健康与统计
const loadOptions = async () => {
    try {
        const res = await fetchBackendOptions();
        if (res.success && res.options) {
            apiOptions.value = res.options.apis || [];
            // 从本地读取默认API（如果存在）
            const saved = uni.getStorageSync("preferred_api");
            if (typeof saved === "string" && apiOptions.value.length) {
                const idx = apiOptions.value.indexOf(saved);
                apiIndex.value = idx >= 0 ? idx : 0;
            }
        }
    } catch (e) {}
};

const loadStats = async () => {
    try {
        const res = await fetchBackendStats();
        if (res.success) {
            stats.value = res.stats;
        }
    } catch (e) {}
};

const refreshHealth = async () => {
    try {
        health.value.loading = true;
        const res = await fetchHealth();
        health.value.ok = res?.status === "healthy";
        health.value.version = res?.version || "";
    } catch (e) {
        health.value.ok = false;
    } finally {
        health.value.loading = false;
    }
};

const handleApiChange = (e: PickerChangeEvent) => {
    apiIndex.value = Number(e.detail.value) || 0;
    const value = apiOptions.value[apiIndex.value];
    if (value) {
        uni.setStorageSync("preferred_api", value);
        uni.showToast({
            title: `默认API已设为：${apiLabelMap[value] || value}`,
            icon: "none",
        });
    }
};

onLoad(() => {
    restoreSettings();
    syncUiStateFromSettings();
    syncThemeFromStorage();
    syncAuthState();
    loadOptions();
    loadStats();
    refreshHealth();
});

onShow(() => {
    syncTheme();
    syncAuthState();
});

onMounted(() => {
    if (typeof uni.$on === "function") {
        uni.$on("theme-changed", syncTheme);
    }
});

onUnmounted(() => {
    if (typeof uni.$off === "function") {
        uni.$off("theme-changed", syncTheme);
    }
});
</script>

<style>
page {
    height: 100%;
}

.settings-container {
    padding-bottom: 40rpx;
    background-color: var(--page-bg);
}

.user-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40rpx 0;
    background-color: var(--surface);
    margin-bottom: 20rpx;
}

.user-avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    background-color: var(--surface-muted);
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20rpx;
    overflow: hidden;
}

.avatar-image {
    width: 100%;
    height: 100%;
}

.user-info {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.user-name {
    font-size: 36rpx;
    font-weight: bold;
    color: var(--text-primary);
    margin-bottom: 10rpx;
}

.login-text {
    font-size: 36rpx;
    color: var(--accent);
    font-weight: bold;
}

.vip-tag {
    font-size: 24rpx;
    color: var(--accent-contrast);
    background-color: var(--warning);
    padding: 4rpx 16rpx;
    border-radius: 20rpx;
}

.member-tag {
    font-size: 24rpx;
    color: var(--text-secondary);
    background-color: var(--surface-muted);
    padding: 4rpx 16rpx;
    border-radius: 20rpx;
}

.settings-group {
    background-color: var(--surface);
    margin-bottom: 20rpx;
    border-radius: 12rpx;
    overflow: hidden;
}

.group-title {
    display: block;
    padding: 24rpx 32rpx;
    font-size: 28rpx;
    color: var(--text-secondary);
    background-color: var(--surface-soft);
}

.settings-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 28rpx 32rpx;
    border-bottom: 1rpx solid var(--border-color);
}

.settings-item:last-child {
    border-bottom: none;
}

.item-label {
    font-size: 32rpx;
    color: var(--text-primary);
}

.item-value {
    font-size: 32rpx;
    color: var(--text-secondary);
}

.picker-value {
    display: flex;
    align-items: center;
    color: var(--text-secondary);
}

.radio-item {
    margin-right: 40rpx;
    display: inline-flex;
    align-items: center;
}

.radio-item text {
    margin-left: 10rpx;
    font-size: 28rpx;
    color: var(--text-primary);
}

.slider-labels {
    display: flex;
    justify-content: space-between;
    width: 100%;
    margin-top: 10rpx;
}

.slider-labels text {
    font-size: 24rpx;
    color: var(--text-secondary);
}

.backup-btn,
.stats-btn,
.clear-btn,
.config-btn {
    border: 1rpx solid var(--accent);
    color: var(--accent);
    background-color: transparent;
    border-radius: 40rpx;
    padding: 0 24rpx;
    height: 56rpx;
    line-height: 56rpx;
}

.config-btn.danger {
    border-color: var(--danger);
    color: var(--danger);
}

.backup-btn:active,
.stats-btn:active,
.clear-btn:active,
.config-btn:active {
    background-color: var(--interactive-active-bg);
}

.config-btn.danger:active {
    background-color: var(--surface-muted);
}
</style>
