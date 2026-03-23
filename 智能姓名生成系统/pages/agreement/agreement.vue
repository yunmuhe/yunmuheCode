<template>
    <view class="page-container" :style="themeVars">
        <CustomNavBar :title="pageTitle" />

        <view class="content-card">
            <text class="section-title">{{ heading }}</text>
            <text class="section-text">{{ content }}</text>
            <text class="section-tip">如需进一步说明，可在“反馈与帮助”页面联系我们。</text>
        </view>
    </view>
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import {
    createThemeCssVars,
    getRuntimeThemePalette,
    type ThemePalette,
} from "../../common/theme";
import CustomNavBar from "../../components/CustomNavBar.vue";

const type = ref("user");
const themePalette = ref<ThemePalette>(getRuntimeThemePalette());
const themeVars = computed(() => createThemeCssVars(themePalette.value));

const syncTheme = () => {
    themePalette.value = getRuntimeThemePalette();
};

const pageTitle = computed(() =>
    type.value === "privacy" ? "隐私政策" : "用户协议",
);
const heading = computed(() =>
    type.value === "privacy" ? "隐私保护说明" : "用户使用说明",
);
const content = computed(() =>
    type.value === "privacy"
        ? "我们当前仅在提供登录、收藏、历史记录和接口偏好设置等功能时保存必要数据。数据仅用于支撑功能本身，不会在未告知的情况下用于其他目的。"
        : "本应用用于智能姓名生成与结果管理，请在合法合规场景下使用。登录、收藏、历史记录等功能会结合后端服务提供，请勿输入敏感或违法内容。",
);

onLoad((options) => {
    syncTheme();
    const pageType = typeof options?.type === "string" ? options.type : "user";
    type.value = pageType === "privacy" ? "privacy" : "user";
});

onShow(() => {
    syncTheme();
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
    background-color: transparent;
}

.page-container {
    min-height: 100%;
    background-color: var(--page-bg);
}

.content-card {
    margin: 24rpx;
    padding: 32rpx;
    background-color: var(--surface);
    border-radius: 16rpx;
    box-shadow: var(--shadow-soft);
}

.section-title {
    display: block;
    font-size: 34rpx;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 20rpx;
}

.section-text,
.section-tip {
    display: block;
    font-size: 28rpx;
    line-height: 1.8;
    color: var(--text-secondary);
}

.section-tip {
    margin-top: 24rpx;
    color: var(--accent);
}
</style>
