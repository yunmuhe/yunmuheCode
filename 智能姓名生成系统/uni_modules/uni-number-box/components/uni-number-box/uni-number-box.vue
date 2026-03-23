<template>
	<view class="uni-number-box">
		<button class="uni-number-box__minus" @click="onMinus" :disabled="disabled || value <= min">-</button>
		<input class="uni-number-box__value" type="number" :value="value" @input="onInput" :disabled="disabled" />
		<button class="uni-number-box__plus" @click="onPlus" :disabled="disabled || value >= max">+</button>
	</view>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
	modelValue: {
		type: Number,
		default: 1
	},
	min: {
		type: Number,
		default: 0
	},
	max: {
		type: Number,
		default: 100
	},
	step: {
		type: Number,
		default: 1
	},
	disabled: {
		type: Boolean,
		default: false
	}
});

const emit = defineEmits(['update:modelValue', 'change']);

const value = ref(props.modelValue);

watch(() => props.modelValue, (newVal) => {
	value.value = newVal;
});

const onMinus = () => {
	if (value.value > props.min) {
		value.value -= props.step;
		emit('update:modelValue', value.value);
		emit('change', value.value);
	}
};

const onPlus = () => {
	if (value.value < props.max) {
		value.value += props.step;
		emit('update:modelValue', value.value);
		emit('change', value.value);
	}
};

const onInput = (e) => {
	let val = parseInt(e.detail.value);
	if (isNaN(val)) val = props.min;
	if (val < props.min) val = props.min;
	if (val > props.max) val = props.max;
	value.value = val;
	emit('update:modelValue', val);
	emit('change', val);
};
</script>

<style scoped>
.uni-number-box {
	display: flex;
	align-items: center;
	border: 1px solid #e5e5e5;
	border-radius: 4px;
	overflow: hidden;
	width: fit-content;
}

.uni-number-box__minus,
.uni-number-box__plus {
	width: 35px;
	height: 35px;
	display: flex;
	align-items: center;
	justify-content: center;
	background-color: #f5f5f5;
	border: none;
	color: #333;
	font-size: 20px;
	cursor: pointer;
	padding: 0;
	margin: 0;
}

.uni-number-box__minus:active,
.uni-number-box__plus:active {
	background-color: #e5e5e5;
}

.uni-number-box__minus[disabled],
.uni-number-box__plus[disabled] {
	color: #ccc;
	cursor: not-allowed;
	background-color: #f8f8f8;
}

.uni-number-box__value {
	width: 50px;
	height: 35px;
	text-align: center;
	border: none;
	border-left: 1px solid #e5e5e5;
	border-right: 1px solid #e5e5e5;
	font-size: 14px;
	color: #333;
}

.uni-number-box__value[disabled] {
	background-color: #f8f8f8;
	color: #ccc;
}
</style>
