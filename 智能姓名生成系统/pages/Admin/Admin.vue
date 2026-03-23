<template>
    <view class="page-container" :style="themeVars">
        <CustomNavBar
            title="后台管理"
            fallback-url="/pages/Index/Index"
            fallback-mode="reLaunch"
        />

        <view class="content-card">
            <text class="section-title">后台管理入口已预留</text>
            <text class="section-text">
                当前版本仅提供管理员入口页，用于确认账号权限和后续扩展管理功能。完整管理面板仍在建设中。
            </text>
            <text class="status-tag">当前状态：最小可用占位页</text>
        </view>
    </view>
</template>

<script lang="ts" setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import { getAuthUser } from "../../common/api";
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
    const user = getAuthUser();
    if (user?.role === "admin") {
        return;
    }

    uni.showToast({
        title: "仅管理员可访问",
        icon: "none",
    });

    setTimeout(() => {
        uni.reLaunch({
            url: "/pages/Index/Index",
        });
    }, 300);
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
.status-tag {
    display: block;
    font-size: 28rpx;
    line-height: 1.8;
    color: var(--text-secondary);
}

.status-tag {
    margin-top: 24rpx;
    color: var(--accent);
}
</style>
