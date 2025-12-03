<template>
	<view class="page-container">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<button class="back-btn" @click="goBack">
				<uni-icons type="arrowleft" size="24" color="#333"></uni-icons>
			</button>
			<view class="nav-title">我的收藏</view>
			<view class="nav-edit" @click="toggleEditMode">
				<uni-icons type="compose" size="20" color="#333"></uni-icons>
			</view>
		</view>

		<!-- 标签筛选区 -->
		<scroll-view class="tag-container" scroll-x>
			<view v-for="tag in tags" :key="tag.value" class="tag-item"
				:class="{ active: selectedTags.includes(tag.value) }" @click="toggleTag(tag.value)">
				{{ tag.label }}
			</view>
		</scroll-view>

		<!-- 内容区域 -->
		<scroll-view class="content-container" scroll-y>
			<!-- 空状态 -->
			<view v-if="favorites.length === 0" class="empty-state">
				<image class="empty-image"
					src="https://ai-public.mastergo.com/ai/img_res/aae7c630a469d167b534dbe4c3fa9c0a.jpg"
					mode="aspectFit" />
				<view class="empty-text">暂无收藏内容，快去生成页发现你喜欢的名字吧！</view>
				<button class="empty-button" type="primary" @click="goToGenerate">去生成名字</button>
			</view>

			<!-- 收藏列表 -->
			<view v-else class="favorites-grid">
				<view v-for="(item, index) in filteredFavorites" :key="item.id" class="favorite-card"
					:class="{ selected: selectedItems.includes(item.id) }">
					<view class="card-header">
						<text class="name">{{ item.name }}</text>
						<view v-if="!editMode" class="favorite-icon" @click="toggleFavorite(item.id)">
							<uni-icons type="heart-filled" size="20" color="#ff4d4f"></uni-icons>
						</view>
						<checkbox v-else class="select-checkbox" :checked="selectedItems.includes(item.id)"
							@click="toggleSelect(item.id)" />
					</view>
					<text class="meaning">{{ item.meaning }}</text>
					<view class="tags-container">
						<view class="style-tag">{{ item.style }}</view>
						<view class="gender-tag">{{ item.gender }}</view>
					</view>
					<view class="card-footer">
						<text class="time">{{ item.time }}</text>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 批量操作栏 -->
		<view v-if="editMode" class="batch-actions">
			<view class="select-all">
				<checkbox :checked="isAllSelected" @click="toggleSelectAll" />
				<text class="select-text">全选</text>
			</view>
			<text class="selected-count">已选 {{ selectedItems.length }} 项</text>
			<button class="batch-button" @click="batchRemove">批量取消收藏</button>
			<button class="batch-button" type="primary" @click="batchExport">批量导出</button>
		</view>
	</view>
</template>

<script lang="ts" setup>
	import { ref, computed } from 'vue';
	import { onLoad } from '@dcloudio/uni-app';
	import uniIcons from '@/uni_modules/uni-icons/components/uni-icons/uni-icons.vue';

	// 标签数据
	const tags = ref([
		{ label: '全部收藏', value: 'all' },
		{ label: '古典', value: 'classic' },
		{ label: '现代', value: 'modern' },
		{ label: '奇幻', value: 'fantasy' },
		{ label: '中式', value: 'chinese' },
		{ label: '西式', value: 'western' },
		{ label: '男性', value: 'male' },
		{ label: '女性', value: 'female' },
		{ label: '中性', value: 'unisex' }
	]);

	// 选中的标签
	const selectedTags = ref<string[]>(['all']);

	// 编辑模式
	const editMode = ref(false);

	// 选中的项目
	const selectedItems = ref<string[]>([]);

	// 收藏列表数据（从后端获取）
	import { getFavorites, deleteFavorites } from '../../common/api';
	const favorites = ref<any[]>([]);

	// 过滤后的收藏列表
	const filteredFavorites = computed(() => {
		if (selectedTags.value.includes('all')) {
			return favorites.value;
		}

		return favorites.value.filter(item => {
			const styleMatch = selectedTags.value.includes(item.style.toLowerCase());
			const genderMatch = selectedTags.value.includes(item.gender.toLowerCase());
			return styleMatch || genderMatch;
		});
	});

	// 是否全选
	const isAllSelected = computed(() => {
		return selectedItems.value.length === filteredFavorites.value.length;
	});

	// 切换标签
	const toggleTag = (tag : string) => {
		if (tag === 'all') {
			selectedTags.value = ['all'];
			return;
		}

		const index = selectedTags.value.indexOf(tag);
		if (index > -1) {
			selectedTags.value.splice(index, 1);
		} else {
			selectedTags.value.push(tag);
		}

		// 如果选择了其他标签，移除all标签
		const allIndex = selectedTags.value.indexOf('all');
		if (allIndex > -1 && selectedTags.value.length > 1) {
			selectedTags.value.splice(allIndex, 1);
		}

		// 如果没有选中任何标签，自动选中all
		if (selectedTags.value.length === 0) {
			selectedTags.value = ['all'];
		}
	};

	// 切换编辑模式
	const toggleEditMode = () => {
		editMode.value = !editMode.value;
		if (!editMode.value) {
			selectedItems.value = [];
		}
	};

	// 切换收藏状态
	const toggleFavorite = async (id : string) => {
		try {
			await deleteFavorites(id);
			uni.showToast({ title: '已取消收藏', icon: 'success' });
			loadFavorites();
		} catch (e) {
			uni.showToast({ title: '操作失败', icon: 'none' });
		}
	};

	// 切换选中状态
	const toggleSelect = (id : string) => {
		const index = selectedItems.value.indexOf(id);
		if (index > -1) {
			selectedItems.value.splice(index, 1);
		} else {
			selectedItems.value.push(id);
		}
	};

	// 全选/取消全选
	const toggleSelectAll = () => {
		if (isAllSelected.value) {
			selectedItems.value = [];
		} else {
			selectedItems.value = filteredFavorites.value.map(item => item.id);
		}
	};

	// 批量取消收藏
	const batchRemove = async () => {
		if (selectedItems.value.length === 0) {
			uni.showToast({ title: '请选择要取消的收藏', icon: 'none' });
			return;
		}
		try {
			await deleteFavorites(selectedItems.value);
			uni.showToast({ title: '已批量取消', icon: 'success' });
			selectedItems.value = [];
			editMode.value = false;
			loadFavorites();
		} catch (e) {
			uni.showToast({ title: '操作失败', icon: 'none' });
		}
	};

	// 批量导出
	const batchExport = () => {
		const exportData = favorites.value.filter(item => selectedItems.value.includes(item.id));
		console.log('导出数据:', exportData);
		uni.showToast({
			title: `已导出${exportData.length}项`,
			icon: 'success'
		});
		selectedItems.value = [];
		editMode.value = false;
	};

	const loadFavorites = async () => {
		try {
			const res = await getFavorites();
			if (res.success) {
				favorites.value = res.items || [];
			}
		} catch (e) {
			uni.showToast({ title: '加载失败', icon: 'none' });
		}
	};

	const goBack = () => {
		uni.navigateBack();
	};

	const goToGenerate = () => {
		uni.navigateTo({
			url: '/pages/Generate/Generate'
		});
	};

	onLoad(() => {
		loadFavorites();
	});
</script>

<style>
	page {
		height: 100%;
	}

	.page-container {
		display: flex;
		flex-direction: column;
		height: 100%;
		background-color: #f5f5f5;
	}

	.nav-bar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		height: 44px;
		background-color: #fff;
		box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.05);
		padding: 0 10px;
		flex-shrink: 0;
	}

	.back-btn {
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		background: none;
		padding: 0;
	}

	.nav-title {
		flex: 1;
		font-size: 16px;
		font-weight: bold;
		color: #333;
		text-align: center;
	}

	.nav-edit {
		width: 30px;
		height: 30px;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.tag-container {
		white-space: nowrap;
		padding: 20rpx 24rpx;
		background-color: #fff;
		border-bottom: 1px solid #f0f0f0;
	}

	.tag-item {
		display: inline-flex;
		padding: 8rpx 24rpx;
		margin-right: 16rpx;
		border-radius: 40rpx;
		font-size: 12px;
		color: #666;
		background-color: #f5f5f5;
	}

	.tag-item.active {
		color: #fff;
		background-color: #1890ff;
	}

	.content-container {
		flex: 1;
		overflow: auto;
		padding: 24rpx;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 70vh;
	}

	.empty-image {
		width: 200rpx;
		height: 200rpx;
		margin-bottom: 32rpx;
	}

	.empty-text {
		font-size: 14px;
		color: #999;
		margin-bottom: 32rpx;
	}

	.empty-button {
		width: 320rpx;
		height: 80rpx;
		line-height: 80rpx;
		font-size: 32rpx;
		border-radius: 40rpx;
		background-color: #4a90e2;
		color: white;
		border: none;
	}

	.favorites-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 24rpx;
	}

	.favorite-card {
		background-color: #fff;
		border-radius: 12rpx;
		padding: 24rpx;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
		position: relative;
	}

	.favorite-card.selected {
		background-color: #f0f9ff;
		border: 1px solid #1890ff;
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16rpx;
	}

	.name {
		font-size: 16px;
		font-weight: 500;
		color: #333;
		flex: 1;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.favorite-icon {
		width: 40rpx;
		height: 40rpx;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.select-checkbox {
		transform: scale(0.8);
	}

	.meaning {
		display: block;
		font-size: 13px;
		color: #666;
		margin-bottom: 16rpx;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.tags-container {
		display: flex;
		margin-bottom: 16rpx;
	}

	.style-tag,
	.gender-tag {
		padding: 4rpx 12rpx;
		font-size: 10px;
		border-radius: 4px;
		margin-right: 8rpx;
	}

	.style-tag {
		color: #722ed1;
		background-color: #f9f0ff;
	}

	.gender-tag {
		color: #13c2c2;
		background-color: #e6fffb;
	}

	.time {
		font-size: 11px;
		color: #999;
	}

	.batch-actions {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		display: flex;
		align-items: center;
		padding: 16rpx 24rpx;
		background-color: #fff;
		box-shadow: 0 -2rpx 8rpx rgba(0, 0, 0, 0.05);
		z-index: 100;
	}

	.select-all {
		display: flex;
		align-items: center;
		margin-right: 24rpx;
	}

	.select-text {
		font-size: 14px;
		color: #333;
		margin-left: 8rpx;
	}

	.selected-count {
		font-size: 12px;
		color: #666;
		flex: 1;
	}

	.batch-button {
		margin-left: 16rpx;
		padding: 0 24rpx;
		height: 64rpx;
		line-height: 64rpx;
		font-size: 14px;
		border-radius: 32rpx;
	}
</style>