<template>
	<view class="uni-segmented-control">
		<view
			v-for="(item, index) in values"
			:key="index"
			class="uni-segmented-control__item"
			:class="{ 'uni-segmented-control__item--active': current === index }"
			@click="onItemClick(index)"
		>
			<text class="uni-segmented-control__text">{{ item }}</text>
		</view>
	</view>
</template>

<script setup>
const props = defineProps({
	current: {
		type: Number,
		default: 0
	},
	values: {
		type: Array,
		default: () => []
	},
	styleType: {
		type: String,
		default: 'button' // button/text
	}
});

const emit = defineEmits(['clickItem']);

const onItemClick = (index) => {
	emit('clickItem', { currentIndex: index });
};
</script>

<style scoped>
.uni-segmented-control {
	display: flex;
	align-items: center;
	background-color: #f5f5f5;
	border-radius: 4px;
	padding: 2px;
	width: fit-content;
}

.uni-segmented-control__item {
	flex: 1;
	padding: 6px 15px;
	text-align: center;
	cursor: pointer;
	border-radius: 3px;
	transition: all 0.3s;
	white-space: nowrap;
}

.uni-segmented-control__item--active {
	background-color: #fff;
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.uni-segmented-control__text {
	font-size: 14px;
	color: #666;
}

.uni-segmented-control__item--active .uni-segmented-control__text {
	color: #333;
	font-weight: 500;
}
</style>
