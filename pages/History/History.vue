<template>
	<view class="history-page">
		<!-- 顶部筛选栏 -->
		<view class="filter-bar">
			<view class="search-box">
				<uni-icons type="search" size="20" color="#999"></uni-icons>
				<input class="search-input" placeholder="搜索描述内容" placeholder-style="color:#999;font-size:14px"
					v-model="searchText" @confirm="handleSearch" />
			</view>
			<view class="filter-options">
				<picker mode="selector" :range="timeRange" range-key="label" @change="handleTimeChange">
					<view class="filter-item">
						<text>{{ timeRange[timeIndex].label }}</text>
						<uni-icons type="arrowdown" size="14" color="#666"></uni-icons>
					</view>
				</picker>
				<picker mode="selector" :range="sortRange" range-key="label" @change="handleSortChange">
					<view class="filter-item">
						<text>{{ sortRange[sortIndex].label }}</text>
						<uni-icons type="arrowdown" size="14" color="#666"></uni-icons>
					</view>
				</picker>
			</view>
		</view>

		<!-- 历史记录列表 -->
		<scroll-view class="history-list" scroll-y @scrolltolower="loadMore" :style="{height: scrollHeight + 'px'}">
			<!-- 空状态 -->
			<view class="empty-state" v-if="historyList.length === 0">
				<image class="empty-image"
					src="https://ai-public.mastergo.com/ai/img_res/adc2c67b429ff3c75b0aad8484dc1139.jpg"
					mode="aspectFit" />
				<text class="empty-text">暂无历史记录</text>
				<button class="empty-btn" @click="goToGenerate">去生成姓名</button>
			</view>

			<!-- 分组列表 -->
			<template v-for="(group, index) in groupedList" :key="index">
				<view class="time-group" v-if="group.items.length > 0">
					<text class="group-title">{{ group.title }}</text>
					<view class="history-item" v-for="(item, i) in group.items" :key="i" @click="toggleExpand(item)">
						<view class="item-content">
							<text class="item-desc" :class="{expanded: item.expanded}">
								{{ item.description }}
							</text>
							<view class="item-meta">
								<text class="item-time">{{ formatTime(item.time) }}</text>
								<text class="item-count">生成 {{ item.count }} 个</text>
							</view>
						</view>
						<uni-icons :type="item.expanded ? 'arrowup' : 'arrowdown'" size="16" color="#999"></uni-icons>
					</view>

					<!-- 展开内容 -->
					<view class="expanded-content" v-if="item.expanded" v-for="(item, i) in group.items"
						:key="'expanded-'+i">
						<view class="name-item" v-for="(name, n) in item.names" :key="n">
							<text>{{ name }}</text>
						</view>
					</view>
				</view>
			</template>

			<!-- 加载更多 -->
			<view class="load-more" v-if="historyList.length > 0 && !noMore">
				<text>{{ loading ? '加载中...' : '上拉加载更多' }}</text>
			</view>
		</scroll-view>
	</view>
</template>

<script lang="ts" setup>
	import { ref, computed, onMounted } from 'vue';
	import { onLoad } from '@dcloudio/uni-app';
	import { getHistoryList } from '../../common/api';

	// 筛选选项
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

	// 数据状态
	const timeIndex = ref(0);
	const sortIndex = ref(0);
	const searchText = ref('');
	const historyList = ref<any[]>([]);
	const loading = ref(false);
	const noMore = ref(false);
	const page = ref(1);
	const pageSize = ref(10);
	const scrollHeight = ref(0);

	// 计算分组后的列表
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

		historyList.value.forEach(item => {
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

	// 初始化
	onLoad(() => {
		getSystemInfo();
		fetchHistory();
	});

	// 获取系统信息计算滚动高度
	const getSystemInfo = () => {
		uni.getSystemInfo({
			success: (res) => {
				const query = uni.createSelectorQuery().in(this);
				query.select('.filter-bar').boundingClientRect(data => {
					scrollHeight.value = res.windowHeight - data.height;
				}).exec();
			}
		});
	};

	// 获取历史记录
	const fetchHistory = async () => {
		if (loading.value || noMore.value) return;
		loading.value = true;
		try {
			const res = await getHistoryList({
				page: page.value,
				page_size: pageSize.value,
				q: searchText.value.trim(),
			});
			if (res.success) {
				const items = (res.items || []).map((it : any) => ({
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

	// 处理搜索
	const handleSearch = () => {
		page.value = 1;
		noMore.value = false;
		fetchHistory();
	};

	// 处理时间筛选
	const handleTimeChange = (e : any) => {
		timeIndex.value = e.detail.value;
		page.value = 1;
		noMore.value = false;
		fetchHistory();
	};

	// 处理排序
	const handleSortChange = (e : any) => {
		sortIndex.value = e.detail.value;
		page.value = 1;
		noMore.value = false;
		fetchHistory();
	};

	// 切换展开状态
	const toggleExpand = (item : any) => {
		item.expanded = !item.expanded;
	};

	// 加载更多
	const loadMore = () => {
		fetchHistory();
	};

	// 格式化时间
	const formatTime = (timestamp : number) => {
		const date = new Date(timestamp);
		return `${date.getFullYear()}-${padZero(date.getMonth() + 1)}-${padZero(date.getDate())} ${padZero(date.getHours())}:${padZero(date.getMinutes())}`;
	};

	const padZero = (num : number) => {
		return num < 10 ? `0${num}` : num;
	};

	// 跳转到生成页面
	const goToGenerate = () => {
		uni.navigateTo({
			url: '/pages/Generate/Generate'
		});
	};
</script>

<style>
	page {
		height: 100%;
		background-color: #f5f5f5;
	}

	.history-page {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	/* 筛选栏 */
	.filter-bar {
		background-color: #fff;
		padding: 20rpx 30rpx;
		box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
	}

	.search-box {
		display: flex;
		align-items: center;
		background-color: #f5f5f5;
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

	.filter-options {
		display: flex;
		justify-content: space-between;
	}

	.filter-item {
		display: flex;
		align-items: center;
		font-size: 26rpx;
		color: #666;
		padding: 10rpx 20rpx;
		background-color: #f5f5f5;
		border-radius: 30rpx;
	}

	/* 历史记录列表 */
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
		color: #999;
		margin: 30rpx 0 20rpx;
	}

	.history-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		background-color: #fff;
		border-radius: 16rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
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
		color: #333;
		margin-bottom: 10rpx;
	}

	.item-desc.expanded {
		-webkit-line-clamp: 999;
	}

	.item-meta {
		display: flex;
		font-size: 24rpx;
		color: #999;
	}

	.item-time {
		margin-right: 20rpx;
	}

	/* 展开内容 */
	.expanded-content {
		background-color: #fff;
		border-radius: 0 0 16rpx 16rpx;
		padding: 20rpx 30rpx;
		margin-top: -20rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
	}

	.name-item {
		padding: 15rpx 0;
		font-size: 28rpx;
		color: #666;
		border-bottom: 1rpx solid #f5f5f5;
	}

	.name-item:last-child {
		border-bottom: none;
	}

	/* 空状态 */
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
		font-size: 30rpx;
		color: #999;
		margin-bottom: 40rpx;
	}

	.empty-btn {
		width: 300rpx;
		height: 80rpx;
		line-height: 80rpx;
		font-size: 28rpx;
		color: #fff;
		background-color: #2979ff;
		border-radius: 40rpx;
		margin: 0;
	}

	/* 加载更多 */
	.load-more {
		text-align: center;
		font-size: 26rpx;
		color: #999;
		padding: 30rpx 0;
	}
</style>