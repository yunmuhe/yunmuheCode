<template>
    <view class="page-container" :style="themeVars">
        <CustomNavBar title="反馈与帮助" />

        <view class="content-card">
            <text class="section-title">我们正在完善反馈入口</text>
            <text class="section-text">
                当前版本暂未接入在线工单系统。你可以先整理遇到的问题、操作步骤和期望结果，后续会接入正式反馈通道。
            </text>

            <view class="tips-list">
                <text class="tip-item">1. 记录页面名称和操作步骤</text>
                <text class="tip-item">2. 标注是否与登录、收藏、历史记录有关</text>
                <text class="tip-item">3. 如能复现，补充复现频率与时间</text>
            </view>
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

const themePalette = ref<ThemePalette>(getRuntimeThemePalette());
const themeVars = computed(() => createThemeCssVars(themePalette.value));

const syncTheme = () => {
    themePalette.value = getRuntimeThemePalette();
};

onLoad(() => {
    syncTheme();
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
    font-size: var(--font-rpx-2xl);
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 20rpx;
}

.section-text,
.tip-item {
    display: block;
    font-size: var(--font-rpx-md);
    line-height: 1.8;
    color: var(--text-secondary);
}

.tips-list {
    margin-top: 24rpx;
    padding: 20rpx 24rpx;
    border-radius: 12rpx;
    background-color: var(--accent-soft);
}

.tip-item + .tip-item {
    margin-top: 8rpx;
}
</style>
