<script lang="ts">
	import { defineComponent } from 'vue';
	import { applyFontScale, getStoredFontSize } from './common/fontScale';
	import { applyTheme, getStoredTheme } from './common/theme';

	const syncStoredTheme = (): void => {
		applyTheme(getStoredTheme());
	};

	const syncStoredPreferences = (): void => {
		syncStoredTheme();
		applyFontScale(getStoredFontSize());
	};

	export default defineComponent({
		onLaunch() {
			syncStoredPreferences();
			console.log('App Launch');
		},
		onShow() {
			syncStoredPreferences();
			console.log('App Show');
		},
		onHide() {
			console.log('App Hide');
		},
	});
</script>

<style>
	:root,
	html[data-font-scale='medium'],
	body[data-font-scale='medium'] {
		--font-px-2xs: 10px;
		--font-px-xs: 11px;
		--font-px-sm: 12px;
		--font-px-md: 13px;
		--font-px-base: 14px;
		--font-px-lg: 16px;
		--font-rpx-2xs: 23rpx;
		--font-rpx-xs: 24rpx;
		--font-rpx-sm: 26rpx;
		--font-rpx-md: 28rpx;
		--font-rpx-lg: 30rpx;
		--font-rpx-xl: 32rpx;
		--font-rpx-2xl: 36rpx;
		--font-rpx-3xl: 42rpx;
		--font-rpx-4xl: 48rpx;
	}

	html[data-font-scale='small'],
	body[data-font-scale='small'] {
		--font-px-2xs: 9px;
		--font-px-xs: 10px;
		--font-px-sm: 11px;
		--font-px-md: 12px;
		--font-px-base: 13px;
		--font-px-lg: 15px;
		--font-rpx-2xs: 21rpx;
		--font-rpx-xs: 22rpx;
		--font-rpx-sm: 24rpx;
		--font-rpx-md: 26rpx;
		--font-rpx-lg: 28rpx;
		--font-rpx-xl: 30rpx;
		--font-rpx-2xl: 34rpx;
		--font-rpx-3xl: 38rpx;
		--font-rpx-4xl: 44rpx;
	}

	html[data-font-scale='large'],
	body[data-font-scale='large'] {
		--font-px-2xs: 11px;
		--font-px-xs: 12px;
		--font-px-sm: 13px;
		--font-px-md: 14px;
		--font-px-base: 15px;
		--font-px-lg: 17px;
		--font-rpx-2xs: 25rpx;
		--font-rpx-xs: 26rpx;
		--font-rpx-sm: 28rpx;
		--font-rpx-md: 30rpx;
		--font-rpx-lg: 32rpx;
		--font-rpx-xl: 34rpx;
		--font-rpx-2xl: 38rpx;
		--font-rpx-3xl: 46rpx;
		--font-rpx-4xl: 52rpx;
	}

	html,
	body,
	#app,
	uni-app,
	uni-page-wrapper,
	uni-page-body {
		width: 100%;
		min-height: 100%;
		overflow-x: hidden;
	}

	body {
		margin: 0;
		background: var(--page-bg, #f8f8f8);
	}

	/*每个页面公共css */
</style>
