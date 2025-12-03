<template>
	<text class="uni-icons" :style="{color: color, fontSize: size + 'px'}" @click="onClick">{{ iconText }}</text>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
	type: {
		type: String,
		default: ''
	},
	color: {
		type: String,
		default: '#333'
	},
	size: {
		type: [Number, String],
		default: 16
	}
});

const emit = defineEmits(['click']);

const iconMap = {
	'home': '🏠',
	'arrowleft': '←',
	'arrowright': '→',
	'arrowup': '↑',
	'arrowdown': '↓',
	'heart': '♡',
	'heart-filled': '♥',
	'person': '👤',
	'contact': '👤',
	'search': '🔍',
	'refresh': '🔄',
	'list': '☰',
	'paperplane': '✈',
	'light': '💡',
	'compose': '✏'
};

const iconText = computed(() => iconMap[props.type] || '?');

const onClick = () => {
	emit('click');
};
</script>

<style scoped>
.uni-icons {
	font-style: normal;
	display: inline-block;
	vertical-align: middle;
}
</style>
