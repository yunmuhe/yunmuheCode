<template>
	<view class="uni-navbar" :class="{ 'uni-navbar-fixed': fixed }">
		<view class="uni-navbar__content">
			<view class="uni-navbar__left" @click="onClickLeft">
				<text v-if="leftIcon" class="uni-navbar__icon">{{ leftIcon === 'left' ? '←' : leftIcon }}</text>
				<text v-if="leftText" class="uni-navbar__text">{{ leftText }}</text>
			</view>
			<view class="uni-navbar__header">
				<view class="uni-navbar__header-container">
					<text class="uni-navbar__header-title">{{ title }}</text>
				</view>
			</view>
			<view class="uni-navbar__right" @click="onClickRight">
				<text v-if="rightIcon" class="uni-navbar__icon">{{ rightIcon }}</text>
				<text v-if="rightText" class="uni-navbar__text">{{ rightText }}</text>
			</view>
		</view>
	</view>
</template>

<script setup>
const props = defineProps({
	title: {
		type: String,
		default: ''
	},
	leftIcon: {
		type: String,
		default: ''
	},
	leftText: {
		type: String,
		default: ''
	},
	rightIcon: {
		type: String,
		default: ''
	},
	rightText: {
		type: String,
		default: ''
	},
	fixed: {
		type: Boolean,
		default: false
	}
});

const emit = defineEmits(['clickLeft', 'clickRight']);

const onClickLeft = () => {
	emit('clickLeft');
};

const onClickRight = () => {
	emit('clickRight');
};
</script>

<style scoped>
.uni-navbar {
	display: flex;
	flex-direction: row;
	align-items: center;
	height: 44px;
	background-color: #fff;
	border-bottom: 1px solid #e5e5e5;
}

.uni-navbar-fixed {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	z-index: 999;
}

.uni-navbar__content {
	display: flex;
	flex-direction: row;
	align-items: center;
	height: 100%;
	width: 100%;
	padding: 0 15px;
}

.uni-navbar__left,
.uni-navbar__right {
	display: flex;
	align-items: center;
	min-width: 60px;
	cursor: pointer;
}

.uni-navbar__left {
	justify-content: flex-start;
}

.uni-navbar__right {
	justify-content: flex-end;
}

.uni-navbar__header {
	flex: 1;
	display: flex;
	justify-content: center;
	align-items: center;
}

.uni-navbar__header-container {
	display: flex;
	justify-content: center;
	align-items: center;
}

.uni-navbar__header-title {
	font-size: 16px;
	font-weight: bold;
	color: #333;
}

.uni-navbar__icon {
	font-size: 24px;
	color: #333;
	margin-right: 5px;
}

.uni-navbar__text {
	font-size: 14px;
	color: #333;
}
</style>
