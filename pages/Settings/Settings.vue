<template>
    <view class="settings-container">
        <!-- 椤堕儴瀵艰埅鏍?-->
        <view class="nav-bar">
            <button class="back-btn" @click="handleBack">
                <uni-icons type="arrowleft" size="24" color="#333"></uni-icons>
            </button>
            <text class="page-title">璁剧疆</text>
            <view class="placeholder"></view>
        </view>

        <!-- 鐢ㄦ埛淇℃伅鍖哄煙 -->
        <view class="user-section">
            <view class="user-avatar" @click="handleUserClick">
                <image
                    v-if="isLogin"
                    class="avatar-image"
                    :src="
                        userInfo.avatar ||
                        'https://ai-public.mastergo.com/ai/img_res/ab95285ae27e91c77528f5798b063ad2.jpg'
                    "
                    mode="aspectFill"
                />
                <uni-icons v-else type="contact" size="60" color="#999" />
            </view>
            <view class="user-info">
                <text v-if="isLogin" class="user-name">{{
                    maskedPhone
                }}</text>
                <text v-else class="login-text" @click="handleLogin"
                    >鐐瑰嚮鐧诲綍</text
                >
                <text v-if="isLogin && userInfo.isAdmin" class="vip-tag"
                    >绠＄悊鍛?/text
                >
                <text v-else-if="isLogin" class="member-tag">鏅€氫細鍛?/text>
            </view>
        </view>

        <!-- 鏅鸿兘浣撹繛鎺ヤ笌鐘舵€?-->
        <view class="settings-group">
            <text class="group-title">鏅鸿兘浣撹繛鎺?/text>
            <view class="settings-item">
                <text class="item-label">褰撳墠鍦板潃</text>
                <text
                    class="item-value"
                    style="font-size: 24rpx; word-break: break-all"
                    >{{ apiBaseUrl }}</text
                >
            </view>
            <view class="settings-item">
                <text class="item-label">杩炴帴鐘舵€?/text>
                <view style="display: flex; align-items: center">
                    <view
                        :style="{
                            width: '14rpx',
                            height: '14rpx',
                            borderRadius: '50%',
                            backgroundColor: health.ok ? '#2ecc71' : '#e74c3c',
                            marginRight: '12rpx',
                        }"
                    ></view>
                    <text class="item-value">{{
                        health.ok ? "宸茶繛鎺? : "鏈繛鎺?
                    }}</text>
                    <text
                        v-if="health.version"
                        style="margin-left: 12rpx; color: #999"
                        >v{{ health.version }}</text
                    >
                    <button
                        class="stats-btn"
                        style="margin-left: 16rpx"
                        size="mini"
                        @click="refreshHealth"
                        :disabled="health.loading"
                    >
                        {{ health.loading ? "妫€鏌ヤ腑..." : "閲嶆柊妫€鏌? }}
                    </button>
                </view>
            </view>
        </view>

        <!-- 鍋忓ソ璁剧疆鍒嗙粍锛堝惈榛樿API鎻愪緵鍟嗭級 -->
        <view class="settings-group">
            <text class="group-title">鍋忓ソ璁剧疆</text>
            <view class="settings-item">
                <text class="item-label">榛樿鐢熸垚鏁伴噺</text>
                <uni-number-box
                    v-model="settings.generateCount"
                    :min="1"
                    :max="10"
                />
            </view>
            <view class="settings-item" v-if="apiOptions.length">
                <text class="item-label">榛樿API鎻愪緵鍟?/text>
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
                <text class="item-label">榛樿椋庢牸鍋忓ソ</text>
                <uni-segmented-control
                    :current="styleIndex"
                    :values="styles"
                    @clickItem="handleStyleChange"
                />
            </view>
            <view class="settings-item">
                <text class="item-label">鑷姩澶嶅埗缁撴灉</text>
                <switch
                    :checked="settings.autoCopy"
                    @change="handleAutoCopyChange"
                    color="#4a90e2"
                />
            </view>
        </view>

        <!-- 鏄剧ず璁剧疆鍒嗙粍 -->
        <view class="settings-group">
            <text class="group-title">鏄剧ず璁剧疆</text>
            <view class="settings-item">
                <text class="item-label">涓婚妯″紡</text>
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
                <text class="item-label">瀛椾綋澶у皬</text>
                <slider
                    :value="fontSizeIndex"
                    :min="0"
                    :max="2"
                    @change="handleFontSizeChange"
                    :step="1"
                    activeColor="#4a90e2"
                />
                <view class="slider-labels">
                    <text>灏?/text>
                    <text>涓?/text>
                    <text>澶?/text>
                </view>
            </view>
            <view class="settings-item">
                <text class="item-label">鍔ㄧ敾鏁堟灉</text>
                <switch
                    :checked="settings.animation"
                    @change="handleAnimationChange"
                    color="#4a90e2"
                />
            </view>
        </view>

        <!-- 瀛樺偍璁剧疆鍒嗙粍 -->
        <view class="settings-group">
            <text class="group-title">瀛樺偍璁剧疆</text>
            <view class="settings-item">
                <text class="item-label">鍘嗗彶璁板綍淇濈暀鏃堕棿</text>
                <picker
                    mode="selector"
                    :range="retentionTimes"
                    :value="retentionIndex"
                    @change="handleRetentionChange"
                >
                    <view class="picker-value">
                        {{ retentionTimes[retentionIndex] }}
                        <uni-icons type="arrowright" size="16" color="#999" />
                    </view>
                </picker>
            </view>
            <view class="settings-item">
                <text class="item-label">鑷姩娓呯悊璁剧疆</text>
                <switch
                    :checked="settings.autoClean"
                    @change="handleAutoCleanChange"
                    color="#4a90e2"
                />
            </view>
            <view class="settings-item">
                <text class="item-label">鏁版嵁澶囦唤涓庢仮澶?/text>
                <button
                    type="default"
                    size="mini"
                    @click="handleBackup"
                    class="backup-btn"
                >
                    澶囦唤
                </button>
            </view>
        </view>

        <!-- 璐︽埛涓庢暟鎹垎缁?-->
        <view class="settings-group">
            <text class="group-title">璐︽埛涓庢暟鎹?/text>
            <view class="settings-item">
                <text class="item-label">鐢ㄦ埛鍚?/text>
                <text class="item-value">{{
                    isLogin ? maskedPhone : "未登录"
                }}</text>
            </view>
            <view class="settings-item" v-if="isLogin && userInfo.isAdmin">
                <text class="item-label">鍚庡彴绠＄悊</text>
                <button
                    type="default"
                    size="mini"
                    @click="goAdmin"
                    class="stats-btn"
                >
                    杩涘叆
                </button>
            </view>
            <view class="settings-item">
                <text class="item-label">{{
                    isLogin ? "閫€鍑虹櫥褰? : "璐﹀彿鐧诲綍"
                }}</text>
                <button
                    type="default"
                    size="mini"
                    @click="isLogin ? handleLogout() : handleLogin()"
                    class="clear-btn"
                >
                    {{ isLogin ? "閫€鍑? : "鐧诲綍" }}
                </button>
            </view>
            <view class="settings-item">
                <text class="item-label">浜戠鍚屾</text>
                <switch
                    :checked="settings.cloudSync"
                    @change="handleCloudSyncChange"
                    color="#4a90e2"
                />
            </view>
            <view class="settings-item">
                <text class="item-label">鏁版嵁缁熻</text>
                <button
                    type="default"
                    size="mini"
                    @click="handleViewStats"
                    class="stats-btn"
                >
                    鏌ョ湅
                </button>
            </view>
            <view class="settings-item">
                <text class="item-label">娓呴櫎缂撳瓨</text>
                <button
                    type="default"
                    size="mini"
                    @click="handleClearCache"
                    class="clear-btn"
                >
                    娓呴櫎
                </button>
            </view>
        </view>

        <!-- 鍏充簬涓庢敮鎸佸垎缁?-->
        <view class="settings-group">
            <text class="group-title">鍏充簬涓庢敮鎸?/text>
            <view class="settings-item">
                <text class="item-label">搴旂敤鐗堟湰</text>
                <text class="item-value">v1.2.0</text>
            </view>
            <view class="settings-item" @click="handleUserAgreement">
                <text class="item-label">鐢ㄦ埛鍗忚</text>
                <uni-icons type="arrowright" size="16" color="#999" />
            </view>
            <view class="settings-item" @click="handlePrivacyPolicy">
                <text class="item-label">闅愮鏀跨瓥</text>
                <uni-icons type="arrowright" size="16" color="#999" />
            </view>
            <view class="settings-item" @click="handleFeedback">
                <text class="item-label">鍙嶉涓庡府鍔?/text>
                <uni-icons type="arrowright" size="16" color="#999" />
            </view>
            <view class="settings-item" @click="handleShareApp">
                <text class="item-label">鍒嗕韩搴旂敤</text>
                <uni-icons type="arrowright" size="16" color="#999" />
            </view>
        </view>
    </view>
</template>

<script lang="ts" setup>
import { ref, reactive, computed } from "vue";
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
} from "../../common/api";
import { applyTheme, getStoredTheme, ThemeKey } from "../../common/theme";
import { maskPhoneNumber } from "../../common/phoneMask";
import uniIcons from "@/uni_modules/uni-icons/components/uni-icons/uni-icons.vue";
import uniNumberBox from "@/uni_modules/uni-number-box/components/uni-number-box/uni-number-box.vue";
import uniSegmentedControl from "@/uni_modules/uni-segmented-control/components/uni-segmented-control/uni-segmented-control.vue";

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
    generateCount: 3,
    aiModel: "gpt-4",
    stylePreference: "realistic",
    autoCopy: true,
    theme: "light",
    fontSize: "medium",
    animation: true,
    retentionTime: "30澶?,
    autoClean: false,
    cloudSync: true,
});

const styles = ["鍐欏疄", "鍗￠€?, "鎶借薄"];
const styleIndex = ref(0);

// 鎺ュ叆鍚庣锛氬彲鐢ˋPI涓庡仴搴枫€佺粺璁?const apiBaseUrl = getApiBaseUrl();
const apiOptions = ref<string[]>([]);
const apiIndex = ref(0);
const apiLabelMap: Record<string, string> = {
    paiou: "娲炬浜?,
    aistudio: "Aistudio",
    baidu: "鐧惧害鍗冨竼",
    baishan: "白山智算",
    siliconflow: "SiliconFlow",
    aliyun: "闃块噷浜?,
    mock: "妯℃嫙鎺ュ彛",
};
const apiOptionLabels = computed(() =>
    apiOptions.value.map((k) => apiLabelMap[k] || k),
);

const health = ref({ ok: false, version: "", loading: false });
const stats = ref<any>(null);

const themes = [
    { name: "娴呰壊", value: "light" },
    { name: "娣辫壊", value: "dark" },
    { name: "鑷姩", value: "auto" },
    { name: "钃濊壊", value: "blue" },
    { name: "缁胯壊", value: "green" },
    { name: "绮夎壊", value: "pink" },
    { name: "绱壊", value: "purple" },
];

const fontSizes = ["small", "medium", "large"];
const fontSizeIndex = ref(1);

const retentionTimes = ["7澶?, "30澶?, "姘镐箙"];
const retentionIndex = ref(1);

const handleBack = () => {
    uni.navigateBack();
};

const handleUserClick = () => {
    if (!isLogin.value) {
        handleLogin();
    } else {
        // 璺宠浆鍒扮敤鎴疯鎯呴〉
    }
};

const handleLogin = () => {
    uni.navigateTo({
        url: "/pages/Auth/Auth",
    });
};

const applyAuthUser = (user: any) => {
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

const handleStyleChange = (e: any) => {
    styleIndex.value = e.currentIndex;
    settings.stylePreference = ["realistic", "cartoon", "abstract"][
        e.currentIndex
    ];
};

const handleAutoCopyChange = (e: any) => {
    settings.autoCopy = e.detail.value;
};

const syncThemeFromStorage = () => {
    const stored = getStoredTheme();
    settings.theme = stored;
    applyTheme(stored);
};

const handleThemeChange = (e: any) => {
    const value = (e?.detail?.value ?? "light") as ThemeKey;
    settings.theme = value;
    applyTheme(value);
};

const handleFontSizeChange = (e: any) => {
    fontSizeIndex.value = e.detail.value;
    settings.fontSize = fontSizes[e.detail.value];
};

const handleAnimationChange = (e: any) => {
    settings.animation = e.detail.value;
};

const handleRetentionChange = (e: any) => {
    retentionIndex.value = e.detail.value;
    settings.retentionTime = retentionTimes[e.detail.value];
};

const handleAutoCleanChange = (e: any) => {
    settings.autoClean = e.detail.value;
};

const handleBackup = () => {
    uni.showToast({
        title: "澶囦唤鎴愬姛",
        icon: "success",
    });
};

const handleCloudSyncChange = (e: any) => {
    settings.cloudSync = e.detail.value;
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
    // 鏄剧ず绠€瑕佺粺璁′俊鎭?    if (!stats.value) {
        uni.showToast({ title: "鏆傛棤缁熻鏁版嵁", icon: "none" });
        return;
    }
    uni.showModal({
        title: "绯荤粺缁熻",
        content: `鍙敤API锛?{stats.value.available_apis}\n缂撳瓨鏉＄洰锛?{stats.value.cache_stats?.active_entries ?? "-"}\nAPI鐘舵€侊細${Object.keys(stats.value.api_status || {}).length} 涓猔,
        showCancel: false,
    });
};

const handleClearCache = () => {
    uni.showModal({
        title: "鎻愮ず",
        content: "纭畾瑕佹竻闄ょ紦瀛樺悧锛?,
        success: (res) => {
            if (res.confirm) {
                // 鐩墠鍚庣鏈彁渚涙竻鐞嗘帴鍙ｏ紝鍙湪姝ゆ墿灞?/cache/clear
                uni.showToast({ title: "鏆備笉鏀寔锛屽悗绔緟鎵╁睍", icon: "none" });
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
    uni.share({
        provider: "weixin",
        type: 0,
        title: "鍒嗕韩搴旂敤",
        success: () => {
            uni.showToast({
                title: "鍒嗕韩鎴愬姛",
                icon: "success",
            });
        },
    });
};

// 杞藉叆鍚庣閫夐」銆佸仴搴蜂笌缁熻
const loadOptions = async () => {
    try {
        const res = await fetchBackendOptions();
        if (res.success && res.options) {
            apiOptions.value = res.options.apis || [];
            // 浠庢湰鍦拌鍙栭粯璁PI锛堝鏋滃瓨鍦級
            const saved = uni.getStorageSync("preferred_api");
            if (saved && apiOptions.value.length) {
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

const handleApiChange = (e: any) => {
    apiIndex.value = Number(e.detail.value) || 0;
    const value = apiOptions.value[apiIndex.value];
    if (value) {
        uni.setStorageSync("preferred_api", value);
        uni.showToast({
            title: `榛樿API宸茶涓猴細${apiLabelMap[value] || value}`,
            icon: "none",
        });
    }
};

onLoad(() => {
    syncThemeFromStorage();
    syncAuthState();
    loadOptions();
    loadStats();
    refreshHealth();
});

onShow(() => {
    syncAuthState();
});
</script>

<style>
page {
    height: 100%;
    background-color: #f5f5f5;
}

.settings-container {
    padding-bottom: 40rpx;
}

.nav-bar {
    height: 44px;
    background-color: #ffffff;
    border-bottom: 1px solid #eee;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 10px;
    flex-shrink: 0;
}

.back-btn {
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: none;
    padding: 0;
}

.page-title {
    flex: 1;
    font-size: 16px;
    font-weight: bold;
    color: #333;
    text-align: center;
}

.placeholder {
    width: 30px;
}

.user-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40rpx 0;
    background-color: #fff;
    margin-bottom: 20rpx;
}

.user-avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    background-color: #f0f0f0;
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
    color: #333;
    margin-bottom: 10rpx;
}

.login-text {
    font-size: 36rpx;
    color: #4a90e2;
    font-weight: bold;
}

.vip-tag {
    font-size: 24rpx;
    color: #fff;
    background-color: #ff9500;
    padding: 4rpx 16rpx;
    border-radius: 20rpx;
}

.member-tag {
    font-size: 24rpx;
    color: #999;
    background-color: #f0f0f0;
    padding: 4rpx 16rpx;
    border-radius: 20rpx;
}

.settings-group {
    background-color: #fff;
    margin-bottom: 20rpx;
    border-radius: 12rpx;
    overflow: hidden;
}

.group-title {
    display: block;
    padding: 24rpx 32rpx;
    font-size: 28rpx;
    color: #999;
    background-color: #f9f9f9;
}

.settings-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 28rpx 32rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.settings-item:last-child {
    border-bottom: none;
}

.item-label {
    font-size: 32rpx;
    color: #333;
}

.item-value {
    font-size: 32rpx;
    color: #999;
}

.picker-value {
    display: flex;
    align-items: center;
    color: #999;
}

.radio-item {
    margin-right: 40rpx;
    display: inline-flex;
    align-items: center;
}

.radio-item text {
    margin-left: 10rpx;
    font-size: 28rpx;
    color: #333;
}

.slider-labels {
    display: flex;
    justify-content: space-between;
    width: 100%;
    margin-top: 10rpx;
}

.slider-labels text {
    font-size: 24rpx;
    color: #999;
}

.backup-btn,
.stats-btn,
.clear-btn,
.config-btn {
    border: 1rpx solid #4a90e2;
    color: #4a90e2;
    background-color: transparent;
    border-radius: 40rpx;
    padding: 0 24rpx;
    height: 56rpx;
    line-height: 56rpx;
}

.config-btn.danger {
    border-color: #e74c3c;
    color: #e74c3c;
}

.backup-btn:active,
.stats-btn:active,
.clear-btn:active,
.config-btn:active {
    background-color: rgba(74, 144, 226, 0.1);
}

.config-btn.danger:active {
    background-color: rgba(231, 76, 60, 0.1);
}
</style>
