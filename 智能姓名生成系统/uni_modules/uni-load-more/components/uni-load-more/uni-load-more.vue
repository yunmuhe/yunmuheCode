<template>
	<view class="uni-load-more" :class="{ 'uni-load-more--circle': iconType === 'circle' }">
		<view v-if="status === 'loading'" class="uni-load-more__loading">
			<view class="uni-load-more__spinner" :class="{'uni-load-more__spinner--circle': iconType === 'circle'}">
				<view v-if="iconType === 'circle'" class="uni-load-more__circle"></view>
				<view v-else class="uni-load-more__dot"></view>
			</view>
			<text v-if="showText" class="uni-load-more__text">{{ loadingText }}</text>
		</view>
		<view v-else-if="status === 'noMore'" class="uni-load-more__content">
			<text class="uni-load-more__text">{{ contentText.contentnomore }}</text>
		</view>
	</view>
</template>

<script setup>
const props = defineProps({
	status: {
		type: String,
		default: 'more' // more/loading/noMore
	},
	showText: {
		type: Boolean,
		default: true
	},
	iconType: {
		type: String,
		default: 'auto' // auto/circle
	},
	contentText: {
		type: Object,
		default: () => ({
			contentdown: '上拉显示更多',
			contentrefresh: '正在加载...',
			contentnomore: '没有更多数据了'
		})
	}
});

const loadingText = props.contentText.contentrefresh || '正在加载...';
</script>

<style scoped>
.uni-load-more {
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 20rpx;
}

.uni-load-more__loading {
	display: flex;
	align-items: center;
	justify-content: center;
}

.uni-load-more__spinner {
	display: inline-block;
	margin-right: 10rpx;
}

.uni-load-more__spinner--circle .uni-load-more__circle {
	width: 30rpx;
	height: 30rpx;
	border: 3rpx solid #e5e5e5;
	border-top-color: #999;
	border-radius: 50%;
	animation: uni-loading 1s linear infinite;
}

.uni-load-more__dot {
	width: 30rpx;
	height: 30rpx;
	border-radius: 50%;
	background-color: #999;
	animation: uni-fade 1s ease-in-out infinite;
}

.uni-load-more__text {
	font-size: 28rpx;
	color: #999;
}

.uni-load-more__content {
	text-align: center;
}

@keyframes uni-loading {
	0% {
		transform: rotate(0deg);
	}
	100% {
		transform: rotate(360deg);
	}
}

@keyframes uni-fade {
	0%, 100% {
		opacity: 0.3;
	}
	50% {
		opacity: 1;
	}
}
</style>
