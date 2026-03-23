<template>
	<view class="container">
		<view class="header">
			<image class="logo" src="/static/home/logo.jpg" />
			<text class="title">智能姓名生成器</text>
			<text class="subtitle">AI驱动的个性化姓名创作工具</text>
		</view>
		<view class="grid-container">
			<view class="grid-item" @click="navigateTo('generate')">
				<image class="icon" src="/static/home/generate.jpg" />
				<text class="label">开始生成</text>
			</view>
			<view class="grid-item" @click="navigateTo('history')">
				<image class="icon" src="/static/home/history.jpg" />
				<text class="label">生成历史</text>
			</view>
			<view class="grid-item" @click="navigateTo('favorites')">
				<image class="icon" src="/static/home/favorites.jpg" />
				<text class="label">我的收藏</text>
			</view>
			<view class="grid-item" @click="navigateTo('settings')">
				<image class="icon" src="/static/home/settings.jpg" />
				<text class="label">系统设置</text>
			</view>
		</view>
		<scroll-view class="examples-container" scroll-x>
			<view class="examples-wrapper">
				<view class="example-card" v-for="(example, index) in examples" :key="index"
					@click="fillExample(example)">
					<text class="example-text">{{ example.text }}</text>
				</view>
			</view>
		</scroll-view>
		<view class="stats-container" v-if="isLoggedIn">
			<view class="stat-item">
				<text class="stat-number">{{ stats.generated }}</text>
				<text class="stat-label">已生成</text>
			</view>
			<view class="stat-item">
				<text class="stat-number">{{ stats.favorites }}</text>
				<text class="stat-label">已收藏</text>
			</view>
			<view class="stat-item">
				<text class="stat-number">{{ stats.today }}</text>
				<text class="stat-label">今日生成</text>
			</view>
		</view>
	</view>
</template>
<script lang="ts" setup>
import { ref } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { getAuthUser, fetchBackendStats, getHistoryList, getFavorites } from '../../common/api';

const isLoggedIn = ref(false);
const stats = ref({
    generated: 0,
    favorites: 0,
    today: 0,
});
const isLoadingStats = ref(false);
let latestStatsRequestId = 0;
const examples = ref([
    { text: "古代文人雅士", category: "ancient" },
    { text: "奇幻世界魔法师", category: "fantasy" },
    { text: "现代科技公司CEO", category: "modern" },
    { text: "科幻星际战士", category: "sci-fi" },
    { text: "武侠江湖侠客", category: "martial" },
]);

const resetStats = () => {
    stats.value = {
        generated: 0,
        favorites: 0,
        today: 0,
    };
};

const syncLoginState = () => {
    const user = getAuthUser();
    isLoggedIn.value = Boolean(user && user.phone);
};

// 加载统计数据
const loadStats = async () => {
	syncLoginState();
	if (!isLoggedIn.value) {
		resetStats();
		return;
	}

	if (isLoadingStats.value) {
		return;
	}

	isLoadingStats.value = true;
	const requestId = ++latestStatsRequestId;
	const nextStats = {
		generated: 0,
		favorites: 0,
		today: 0,
	};

	try {
		const [statsResult, historyResult, favoritesResult] = await Promise.allSettled([
			fetchBackendStats(),
			getHistoryList({ page: 1, page_size: 1 }),
			getFavorites(),
		]);

		if (statsResult.status === 'fulfilled' && statsResult.value.success) {
			nextStats.today = Number(statsResult.value.stats?.today_generated || 0);
		} else if (statsResult.status === 'rejected') {
			console.error('加载系统统计失败:', statsResult.reason);
		}

		if (historyResult.status === 'fulfilled' && historyResult.value.success) {
			nextStats.generated = historyResult.value.total || 0;
		} else if (historyResult.status === 'rejected') {
			console.error('加载历史统计失败:', historyResult.reason);
		}

		if (favoritesResult.status === 'fulfilled' && favoritesResult.value.success) {
			nextStats.favorites = favoritesResult.value.items?.length || 0;
		} else if (favoritesResult.status === 'rejected') {
			console.error('加载收藏统计失败:', favoritesResult.reason);
		}

		if (requestId === latestStatsRequestId) {
			stats.value = nextStats;
		}
	} finally {
		if (requestId === latestStatsRequestId) {
			isLoadingStats.value = false;
		}
	}
};

onShow(() => {
	loadStats();
});

const navigateTo = (page: string) => {
	const pageMap: Record<string, string> = {
		'generate': '/pages/Generate/Generate',
		'history': '/pages/History/History',
		'favorites': '/pages/Favorites/Favorites',
		'settings': '/pages/Settings/Settings'
	};

    const url = pageMap[page];
    if (url) {
        uni.navigateTo({ url });
    }
};
const fillExample = (example: { text: string }) => {
    uni.navigateTo({
        url: `/pages/Generate/Generate?preset=${encodeURIComponent(example.text)}`,
    });
};
</script>
<style>
page {
    height: 100%;
}


.container {
    display: flex;
    flex-direction: column;
    padding: 40rpx;
    background-color: #f8f9fa;
    min-height: 100%;
}

.header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 60rpx;
}

.logo {
    width: 160rpx;
    height: 160rpx;
    margin-bottom: 20rpx;
}

.title {
    font-size: 48rpx;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 10rpx;
}

.subtitle {
    font-size: 28rpx;
    color: #7f8c8d;
}

.grid-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 30rpx;
    margin-bottom: 50rpx;
}

.grid-item {
    background: white;
    border-radius: 20rpx;
    padding: 40rpx 20rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 10rpx 20rpx rgba(0, 0, 0, 0.05);
    aspect-ratio: 1;
    justify-content: center;
    transition: all 0.3s ease;
    cursor: pointer;
}

.grid-item:active {
    transform: scale(0.95);
    box-shadow: 0 5rpx 10rpx rgba(0, 0, 0, 0.1);
}

.icon {
    width: 120rpx;
    height: 120rpx;
    margin-bottom: 20rpx;
}

.label {
    font-size: 32rpx;
    color: #2c3e50;
    font-weight: 500;
}

.examples-container {
    white-space: nowrap;
    margin-bottom: 50rpx;
    padding: 20rpx 0;
}

.examples-wrapper {
    display: inline-flex;
}

.example-card {
    display: inline-block;
    background: white;
    border-radius: 15rpx;
    padding: 25rpx 40rpx;
    margin-right: 20rpx;
    box-shadow: 0 5rpx 15rpx rgba(0, 0, 0, 0.08);
    min-width: 200rpx;
}

.example-text {
    font-size: 26rpx;
    color: #34495e;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.stats-container {
    display: flex;
    justify-content: space-around;
    background: white;
    border-radius: 20rpx;
    padding: 30rpx 0;
    box-shadow: 0 10rpx 20rpx rgba(0, 0, 0, 0.05);
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-number {
    font-size: 40rpx;
    font-weight: bold;
    color: #3498db;
    margin-bottom: 10rpx;
}

.stat-label {
    font-size: 24rpx;
    color: #7f8c8d;
}
</style>
