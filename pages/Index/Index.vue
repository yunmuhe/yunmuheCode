<template>
	<view class="container">
		<view class="header">
			<image class="logo" src="https://ai-public.mastergo.com/ai/img_res/2d3ed915be78aa2c71847331419318e5.jpg" />
			<text class="title">智能姓名生成器</text>
			<text class="subtitle">AI驱动的个性化姓名创作工具</text>
		</view>
		<view class="grid-container">
			<view class="grid-item" @click="navigateTo('generate')">
				<image class="icon"
					src="https://ai-public.mastergo.com/ai/img_res/3489a834b81cae92568a6e392af265a9.jpg" />
				<text class="label">开始生成</text>
			</view>
			<view class="grid-item" @click="navigateTo('history')">
				<image class="icon"
					src="https://ai-public.mastergo.com/ai/img_res/c70c8d36a5d2324a72a274226c912d67.jpg" />
				<text class="label">生成历史</text>
			</view>
			<view class="grid-item" @click="navigateTo('favorites')">
				<image class="icon"
					src="https://ai-public.mastergo.com/ai/img_res/994c6b548030f3f9e102d49139840ca1.jpg" />
				<text class="label">我的收藏</text>
			</view>
			<view class="grid-item" @click="navigateTo('settings')">
				<image class="icon"
					src="https://ai-public.mastergo.com/ai/img_res/74d7216e8525f9d4e0dc2597a5ea728c.jpg" />
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
const isLoggedIn = ref(true);
const stats = ref({
	generated: 128,
	favorites: 24,
	today: 5
});
const examples = ref([
	{ text: '古代文人雅士', category: 'ancient' },
	{ text: '奇幻世界魔法师', category: 'fantasy' },
	{ text: '现代科技公司CEO', category: 'modern' },
	{ text: '科幻星际战士', category: 'sci-fi' },
	{ text: '武侠江湖侠客', category: 'martial' }
]);
const navigateTo = (page: string) => {
	if (page === 'generate') {
		uni.navigateTo({ url: '/pages/generate/generate' });
	} else {
		uni.navigateTo({ url: `/pages/${page}/${page}` });
	}
};
const fillExample = (example: { text: string }) => {
	uni.navigateTo({
		url: `/pages/generate/generate?preset=${encodeURIComponent(example.text)}`
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
	display: flex;
	flex-wrap: wrap;
	justify-content: space-between;
	margin-bottom: 50rpx;
}

.grid-item {
	width: 48%;
	background: white;
	border-radius: 20rpx;
	padding: 40rpx 20rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	box-shadow: 0 10rpx 20rpx rgba(0, 0, 0, 0.05);
	margin-bottom: 30rpx;
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