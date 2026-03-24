<template>
	<view class="custom-nav-bar" :style="themeVars">
		<view class="custom-nav-bar__inner">
			<button
				v-if="showBack"
				class="custom-nav-bar__back"
				@click="handleBack"
			>
				<uni-icons type="arrowleft" size="24" :color="themePalette.textPrimary"></uni-icons>
			</button>
			<view v-else class="custom-nav-bar__placeholder"></view>
			<text class="custom-nav-bar__title">{{ title }}</text>
			<view v-if="hasRightSlot" class="custom-nav-bar__right">
				<slot name="right"></slot>
			</view>
			<view v-else class="custom-nav-bar__placeholder"></view>
		</view>
	</view>
</template>

<script lang="ts" setup>
import { computed, nextTick, onMounted, onUnmounted, ref, useSlots, watch } from 'vue';
import { createThemeCssVars, getRuntimeThemePalette, type ThemePalette } from '../common/theme';
import { syncH5PageTitle } from '../common/pageTitle';
import uniIcons from '@/uni_modules/uni-icons/components/uni-icons/uni-icons.vue';

type FallbackMode = 'navigateTo' | 'reLaunch';

const props = withDefaults(
	defineProps<{
		title: string;
		showBack?: boolean;
		fallbackUrl?: string;
		fallbackMode?: FallbackMode;
	}>(),
	{
		showBack: true,
		fallbackUrl: '',
		fallbackMode: 'navigateTo',
	},
);

const slots = useSlots();
const hasRightSlot = computed(() => Boolean(slots.right));
const themePalette = ref<ThemePalette>(getRuntimeThemePalette());
const themeVars = computed(() => createThemeCssVars(themePalette.value));

const syncTheme = () => {
	themePalette.value = getRuntimeThemePalette();
};

const syncTitle = (title: string) => {
	syncH5PageTitle(title);

	if (typeof window === 'undefined') {
		return;
	}

	nextTick(() => {
		syncH5PageTitle(title);
		window.setTimeout(() => syncH5PageTitle(title), 0);
	});
};

onMounted(() => {
	syncTheme();
	syncTitle(props.title);
	if (typeof uni.$on === 'function') {
		uni.$on('theme-changed', syncTheme);
	}
});

watch(
	() => props.title,
	(title) => {
		syncTitle(title);
	},
	{ immediate: true, flush: 'post' },
);

onUnmounted(() => {
	if (typeof uni.$off === 'function') {
		uni.$off('theme-changed', syncTheme);
	}
});

const handleBack = () => {
	const pages = getCurrentPages();
	if (pages.length > 1) {
		uni.navigateBack();
		return;
	}

	if (!props.fallbackUrl) {
		return;
	}

	if (props.fallbackMode === 'reLaunch') {
		uni.reLaunch({
			url: props.fallbackUrl,
		});
		return;
	}

	uni.navigateTo({
		url: props.fallbackUrl,
	});
};
</script>

<style>
.custom-nav-bar {
	min-height: 44px;
	padding-top: env(safe-area-inset-top);
	background-color: var(--surface);
	border-bottom: 1px solid var(--border-color);
	box-shadow: var(--shadow-soft);
}

.custom-nav-bar__inner {
	min-height: 44px;
	padding: 0 10px;
	display: flex;
	align-items: center;
	justify-content: space-between;
}

.custom-nav-bar__back,
.custom-nav-bar__placeholder,
.custom-nav-bar__right {
	width: 30px;
	min-width: 30px;
	height: 30px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.custom-nav-bar__back {
	border: none;
	background: none;
	padding: 0;
	margin: 0;
}

.custom-nav-bar__title {
	flex: 1;
	font-size: var(--font-px-lg);
	font-weight: bold;
	color: var(--text-primary);
	text-align: center;
}
</style>
