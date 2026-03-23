<template>
	<view class="history-page" :style="themeVars">
		<CustomNavBar title="历史记录" />

		<view class="filter-bar">
			<view class="search-box">
				<uni-icons type="search" size="20" :color="themePalette.textSecondary"></uni-icons>
				<input
					class="search-input"
					placeholder="搜索描述内容"
					:placeholder-style="`color:${themePalette.textSecondary};font-size:14px`"
					v-model="draftSearchText"
					@confirm="handleSearch"
				/>
				<text v-if="draftSearchText" class="search-action" @click="handleSearch">搜索</text>
			</view>
			<view class="filter-options">
				<picker mode="selector" :range="timeRange" range-key="label" @change="handleTimeChange">
					<view class="filter-item">
						<text>{{ timeRange[timeIndex].label }}</text>
						<uni-icons type="arrowdown" size="14" :color="themePalette.textSecondary"></uni-icons>
					</view>
				</picker>
				<picker mode="selector" :range="sortRange" range-key="label" @change="handleSortChange">
					<view class="filter-item">
						<text>{{ sortRange[sortIndex].label }}</text>
						<uni-icons type="arrowdown" size="14" :color="themePalette.textSecondary"></uni-icons>
					</view>
				</picker>
				<view v-if="hasActiveFilters" class="filter-reset" @click="resetFilters">
					重置筛选
				</view>
			</view>
		</view>

		<scroll-view
			class="history-list"
			scroll-y
			@scrolltolower="loadMore"
			:style="{ height: scrollHeight + 'px' }"
		>
			<view class="empty-state" v-if="historyList.length === 0">
				<image class="empty-image" src="/static/common/history-empty.svg" mode="aspectFit" />
				<view class="empty-text">暂无历史记录，快去生成页创造属于你的名字吧！</view>
				<button class="empty-btn" type="primary" @click="goToGenerate">去生成名字</button>
			</view>
			<view class="empty-state" v-else-if="filteredHistoryList.length === 0">
				<view class="empty-text">当前筛选条件下暂无历史记录，试试调整搜索词或时间范围。</view>
				<button class="empty-btn secondary" @click="resetFilters">重置筛选</button>
			</view>

			<template v-for="(group, index) in groupedList" :key="index">
				<view class="time-group" v-if="group.items.length > 0">
					<text class="group-title">{{ group.title }}</text>
					<view v-for="(item, i) in group.items" :key="i">
						<view class="history-item" @click="toggleExpand(item)">
							<view class="item-content">
								<text class="item-desc" :class="{ expanded: item.expanded }">
									{{ item.description }}
								</text>
								<view class="item-meta">
									<text class="item-time">{{ formatTime(item.time) }}</text>
									<text class="item-count">生成 {{ item.count }} 个</text>
								</view>
							</view>
							<uni-icons
								:type="item.expanded ? 'arrowup' : 'arrowdown'"
								size="16"
								:color="themePalette.textSecondary"
							></uni-icons>
						</view>

						<view class="expanded-content" v-if="item.expanded">
							<view class="name-item" v-for="(name, n) in item.names" :key="n">
								<text>{{ name }}</text>
							</view>
						</view>
					</view>
				</view>
			</template>

			<view class="load-more" v-if="filteredHistoryList.length > 0 && !noMore">
				<text>{{ loading ? '加载中...' : '上拉加载更多' }}</text>
			</view>
		</scroll-view>
	</view>
</template>

<script lang="ts" setup>
	import { computed, onMounted, onUnmounted, ref } from 'vue';
	import { onLoad, onShow } from '@dcloudio/uni-app';
	import { getHistoryList } from '../../common/api';
	import { createThemeCssVars, getRuntimeThemePalette, type ThemePalette } from '../../common/theme';
	import CustomNavBar from '../../components/CustomNavBar.vue';
	import uniIcons from '@/uni_modules/uni-icons/components/uni-icons/uni-icons.vue';

	const timeRange = ref([
		{ label: '今天', value: 1 },
		{ label: '近7天', value: 7 },
		{ label: '近30天', value: 30 },
		{ label: '全部', value: 0 }
	]);
	const sortRange = ref([
		{ label: '按时间', value: 'time' },
		{ label: '按数量', value: 'count' }
	]);

	const defaultTimeIndex = 0;
	const timeIndex = ref(defaultTimeIndex);
	const sortIndex = ref(0);
	const draftSearchText = ref('');
	const submittedSearchText = ref('');
	const historyList = ref<any[]>([]);
	const loading = ref(false);
	const noMore = ref(false);
	const page = ref(1);
	const pageSize = ref(10);
	const scrollHeight = ref(0);
	const themePalette = ref<ThemePalette>(getRuntimeThemePalette());
	const themeVars = computed(() => createThemeCssVars(themePalette.value));

	const syncTheme = () => {
		themePalette.value = getRuntimeThemePalette();
	};

	const filteredHistoryList = computed(() => {
		const keyword = submittedSearchText.value.trim().toLowerCase();
		const days = timeRange.value[timeIndex.value]?.value ?? 0;
		const now = Date.now();

		const filtered = historyList.value.filter((item) => {
			const matchKeyword =
				!keyword ||
				String(item.description || '').toLowerCase().includes(keyword) ||
				(item.names || []).some((name: string) => String(name).toLowerCase().includes(keyword));
			if (!matchKeyword) {
				return false;
			}

			if (!days) {
				return true;
			}

			const diff = now - Number(item.time);
			return diff >= 0 && diff <= days * 24 * 60 * 60 * 1000;
		});

		return filtered.slice().sort((a, b) => {
			if (sortRange.value[sortIndex.value]?.value === 'count') {
				if (b.count === a.count) {
					return b.time - a.time;
				}
				return b.count - a.count;
			}
			return b.time - a.time;
		});
	});

	const groupedList = computed(() => {
		const today = new Date();
		today.setHours(0, 0, 0, 0);

		const yesterday = new Date(today);
		yesterday.setDate(yesterday.getDate() - 1);

		const groups = [
			{ title: '今天', items: [] as any[] },
			{ title: '昨天', items: [] as any[] },
			{ title: '更早', items: [] as any[] }
		];

		filteredHistoryList.value.forEach((item) => {
			const itemDate = new Date(item.time);
			if (itemDate >= today) {
				groups[0].items.push(item);
			} else if (itemDate >= yesterday) {
				groups[1].items.push(item);
			} else {
				groups[2].items.push(item);
			}
		});

		return groups;
	});

	const hasActiveFilters = computed(() => {
		return (
			draftSearchText.value.trim().length > 0 ||
			submittedSearchText.value.trim().length > 0 ||
			timeIndex.value !== defaultTimeIndex ||
			sortIndex.value !== 0
		);
	});

	onLoad(() => {
		syncTheme();
		getSystemInfo();
		fetchHistory();
	});

	onShow(() => {
		syncTheme();
	});

	onMounted(() => {
		if (typeof uni.$on === 'function') {
			uni.$on('theme-changed', syncTheme);
		}
	});

	onUnmounted(() => {
		if (typeof uni.$off === 'function') {
			uni.$off('theme-changed', syncTheme);
		}
	});

	const getSystemInfo = () => {
		uni.getSystemInfo({
			success: (res) => {
				const query = uni.createSelectorQuery();
				query
					.select('.filter-bar')
					.boundingClientRect((data) => {
						if (data) {
							scrollHeight.value = res.windowHeight - data.height - 44;
						} else {
							scrollHeight.value = res.windowHeight - 100;
						}
					})
					.exec();
			}
		});
	};

	const fetchHistory = async () => {
		if (loading.value || noMore.value) return;
		loading.value = true;
		try {
			const res = await getHistoryList({
				page: page.value,
				page_size: pageSize.value,
				q: submittedSearchText.value.trim(),
			});
			if (res.success) {
				const items = (res.items || []).map((it: any) => ({
					...it,
					expanded: false,
					time: new Date(it.time).getTime()
				}));
				if (page.value === 1) {
					historyList.value = items;
				} else {
					historyList.value = [...historyList.value, ...items];
				}
				if (items.length < pageSize.value) {
					noMore.value = true;
				}
				page.value++;
			}
		} finally {
			loading.value = false;
		}
	};

	const handleSearch = () => {
		submittedSearchText.value = draftSearchText.value.trim();
		page.value = 1;
		noMore.value = false;
		fetchHistory();
	};

	const handleTimeChange = (e: any) => {
		timeIndex.value = Number(e.detail.value) || 0;
	};

	const handleSortChange = (e: any) => {
		sortIndex.value = Number(e.detail.value) || 0;
	};

	const resetFilters = () => {
		draftSearchText.value = '';
		submittedSearchText.value = '';
		timeIndex.value = defaultTimeIndex;
		sortIndex.value = 0;
		page.value = 1;
		noMore.value = false;
		fetchHistory();
	};

	const toggleExpand = (item: any) => {
		item.expanded = !item.expanded;
	};

	const loadMore = () => {
		fetchHistory();
	};

	const formatTime = (timestamp: number) => {
		const date = new Date(timestamp);
		return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())} ${padZero(date.getHours())}:${padZero(date.getMinutes())}`;
	};

	const padZero = (num: number) => {
		return num < 10 ? `0${num}` : num;
	};

	const goToGenerate = () => {
		uni.navigateTo({
			url: '/pages/Generate/Generate'
		});
	};

</script>

<style>
	page {
		height: 100%;
	}

	.history-page {
		display: flex;
		flex-direction: column;
		height: 100%;
		background-color: var(--page-bg);
	}

	.filter-bar {
		background-color: var(--surface);
		padding: 20rpx 30rpx;
		box-shadow: var(--shadow-soft);
	}

	.search-box {
		display: flex;
		align-items: center;
		background-color: var(--surface-muted);
		border-radius: 40rpx;
		padding: 10rpx 20rpx;
		margin-bottom: 20rpx;
	}

	.search-input {
		flex: 1;
		height: 60rpx;
		font-size: 28rpx;
		margin-left: 10rpx;
	}

	.search-action {
		margin-left: 16rpx;
		font-size: 24rpx;
		color: var(--accent);
	}

	.filter-options {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12rpx;
		flex-wrap: wrap;
	}

	.filter-item {
		display: flex;
		align-items: center;
		font-size: 26rpx;
		color: var(--text-secondary);
		padding: 10rpx 20rpx;
		background-color: var(--surface-muted);
		border-radius: 30rpx;
	}

	.filter-reset {
		padding: 10rpx 20rpx;
		font-size: 24rpx;
		color: var(--accent);
		background-color: var(--accent-soft);
		border-radius: 30rpx;
	}

	.history-list {
		flex: 1;
		overflow: auto;
		padding: 0 30rpx;
		box-sizing: border-box;
	}

	.time-group {
		margin-bottom: 30rpx;
	}

	.group-title {
		display: block;
		font-size: 26rpx;
		color: var(--text-secondary);
		margin: 30rpx 0 20rpx;
	}

	.history-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		background-color: var(--surface);
		border-radius: 16rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		box-shadow: var(--shadow-soft);
	}

	.item-content {
		flex: 1;
		margin-right: 20rpx;
	}

	.item-desc {
		display: -webkit-box;
		-webkit-line-clamp: 1;
		-webkit-box-orient: vertical;
		overflow: hidden;
		font-size: 28rpx;
		color: var(--text-primary);
		margin-bottom: 10rpx;
	}

	.item-desc.expanded {
		-webkit-line-clamp: 999;
	}

	.item-meta {
		display: flex;
		font-size: 24rpx;
		color: var(--text-secondary);
	}

	.item-time {
		margin-right: 20rpx;
	}

	.expanded-content {
		background-color: var(--surface);
		border-radius: 0 0 16rpx 16rpx;
		padding: 20rpx 30rpx;
		margin-top: -20rpx;
		margin-bottom: 20rpx;
		box-shadow: var(--shadow-soft);
	}

	.name-item {
		padding: 15rpx 0;
		font-size: 28rpx;
		color: var(--text-secondary);
		border-bottom: 1rpx solid var(--border-color);
	}

	.name-item:last-child {
		border-bottom: none;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 60vh;
	}

	.empty-image {
		width: 300rpx;
		height: 300rpx;
		margin-bottom: 30rpx;
	}

	.empty-text {
		font-size: 28rpx;
		color: var(--text-secondary);
		margin-bottom: 32rpx;
		text-align: center;
		padding: 0 40rpx;
		line-height: 1.6;
	}

	.empty-btn {
		width: 320rpx;
		height: 80rpx;
		line-height: 80rpx;
		font-size: 32rpx;
		color: var(--accent-contrast);
		background-color: var(--accent);
		border-radius: 40rpx;
		border: none;
		margin: 0;
	}

	.empty-btn.secondary {
		background-color: var(--accent-soft);
		color: var(--accent);
	}

	.load-more {
		text-align: center;
		font-size: 26rpx;
		color: var(--text-secondary);
		padding: 30rpx 0;
	}
</style>
