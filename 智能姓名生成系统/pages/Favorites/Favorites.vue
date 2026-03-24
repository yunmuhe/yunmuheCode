<template>
	<view class="page-container" :style="themeVars">
		<!-- 顶部导航栏 -->
		<CustomNavBar title="我的收藏">
			<template #right>
				<view class="nav-edit" @click="toggleEditMode">
					<uni-icons type="compose" size="20" :color="themePalette.textPrimary"></uni-icons>
				</view>
			</template>
		</CustomNavBar>

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
				<image class="empty-image" src="/static/common/favorites-empty.svg" mode="aspectFit" />
				<view class="empty-text">暂无收藏内容，快去生成页发现你喜欢的名字吧！</view>
				<button class="empty-button" type="primary" @click="goToGenerate">去生成名字</button>
			</view>
			<view v-else-if="filteredFavorites.length === 0" class="empty-state">
				<view class="empty-text">当前筛选下暂无收藏，试试切换标签看看。</view>
				<button class="empty-button secondary" @click="resetFilters">重置筛选</button>
			</view>

			<!-- 收藏列表 -->
			<view v-else class="favorites-grid">
				<view v-for="(item, index) in filteredFavorites" :key="item.id" class="favorite-card"
					:class="{ selected: selectedItems.includes(item.id) }">
					<view class="card-header">
						<text class="name">{{ item.name }}</text>
						<view v-if="!editMode" class="favorite-icon" @click="toggleFavorite(item.id)">
							<uni-icons type="heart-filled" size="20" :color="themePalette.danger"></uni-icons>
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
	import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
	import { onLoad, onShow } from '@dcloudio/uni-app';
	import { getFavorites, deleteFavorites, type FavoriteItem } from '../../common/api';
	import { createThemeCssVars, getRuntimeThemePalette, type ThemePalette } from '../../common/theme';
	import CustomNavBar from '../../components/CustomNavBar.vue';
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
	const themePalette = ref<ThemePalette>(getRuntimeThemePalette());
	const themeVars = computed(() => createThemeCssVars(themePalette.value));

	const syncTheme = () => {
		themePalette.value = getRuntimeThemePalette();
	};

	// 收藏列表数据（从后端获取）
	const favorites = ref<FavoriteItem[]>([]);

	const normalizeValue = (value: unknown) => String(value || '').trim().toLowerCase();

	const getItemTagValues = (item: FavoriteItem) => {
		const tags = new Set<string>();
		const style = normalizeValue(item?.style);
		const gender = normalizeValue(item?.gender);

		const styleAliasMap: Record<string, string[]> = {
			classic: ['classic'],
			'古典': ['classic'],
			'古典中文': ['classic', 'chinese'],
			traditional: ['classic'],
			'传统中文': ['classic', 'chinese'],
			modern: ['modern'],
			'现代': ['modern'],
			'现代中文': ['modern', 'chinese'],
			fantasy: ['fantasy'],
			'奇幻': ['fantasy'],
			'奇幻风格': ['fantasy'],
			chinese: ['chinese'],
			'中式': ['chinese'],
			'中文': ['chinese'],
			western: ['western'],
			'西式': ['western'],
			'西方': ['western'],
			'西方风格': ['western'],
			japanese: ['japanese'],
			'日式': ['japanese'],
			'日式风格': ['japanese'],
		};

		const genderAliasMap: Record<string, string[]> = {
			male: ['male'],
			'男性': ['male'],
			female: ['female'],
			'女性': ['female'],
			neutral: ['unisex'],
			unisex: ['unisex'],
			'中性': ['unisex'],
		};

		(styleAliasMap[style] || []).forEach((tag) => tags.add(tag));
		(genderAliasMap[gender] || []).forEach((tag) => tags.add(tag));

		if (!tags.size) {
			if (style) {
				tags.add(style);
			}
			if (gender) {
				tags.add(gender);
			}
		}

		return tags;
	};

	// 过滤后的收藏列表
	const filteredFavorites = computed(() => {
		if (selectedTags.value.includes('all')) {
			return favorites.value;
		}

		return favorites.value.filter(item => {
			const itemTags = getItemTagValues(item);
			return selectedTags.value.some((tag) => itemTags.has(tag));
		});
	});

	const visibleFavoriteIds = computed(() => filteredFavorites.value.map((item) => item.id));

	// 是否全选
	const isAllSelected = computed(() => {
		return filteredFavorites.value.length > 0 && selectedItems.value.length === filteredFavorites.value.length;
	});

	watch(visibleFavoriteIds, (ids) => {
		selectedItems.value = selectedItems.value.filter((id) => ids.includes(id));
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

	const resetFilters = () => {
		selectedTags.value = ['all'];
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
		const exportData = filteredFavorites.value.filter(item => selectedItems.value.includes(item.id));
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

	const goToGenerate = () => {
		uni.navigateTo({
			url: '/pages/Generate/Generate'
		});
	};

	onLoad(() => {
		syncTheme();
		loadFavorites();
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
</script>

<style>
	page {
		height: 100%;
	}

	.page-container {
		display: flex;
		flex-direction: column;
		height: 100%;
		background-color: var(--page-bg);
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
		background-color: var(--surface);
		border-bottom: 1px solid var(--border-color);
	}

	.tag-item {
		display: inline-flex;
		padding: 8rpx 24rpx;
		margin-right: 16rpx;
		border-radius: 40rpx;
		font-size: var(--font-px-sm);
		color: var(--text-secondary);
		background-color: var(--surface-muted);
	}

	.tag-item.active {
		color: var(--accent-contrast);
		background-color: var(--accent);
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
		font-size: var(--font-px-base);
		color: var(--text-secondary);
		margin-bottom: 32rpx;
		text-align: center;
		line-height: 1.6;
	}

	.empty-button {
		width: 320rpx;
		height: 80rpx;
		line-height: 80rpx;
		font-size: var(--font-rpx-xl);
		border-radius: 40rpx;
		background-color: var(--accent);
		color: var(--accent-contrast);
		border: none;
	}

	.empty-button.secondary {
		background-color: var(--accent-soft);
		color: var(--accent);
	}

	.favorites-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 24rpx;
	}

	.favorite-card {
		background-color: var(--surface);
		border-radius: 12rpx;
		padding: 24rpx;
		box-shadow: var(--shadow-soft);
		position: relative;
	}

	.favorite-card.selected {
		background-color: var(--accent-soft);
		border: 1px solid var(--accent);
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16rpx;
	}

	.name {
		font-size: var(--font-px-lg);
		font-weight: 500;
		color: var(--text-primary);
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
		font-size: var(--font-px-md);
		color: var(--text-secondary);
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
		font-size: var(--font-px-2xs);
		border-radius: 4px;
		margin-right: 8rpx;
	}

	.style-tag {
		color: var(--accent);
		background-color: var(--accent-soft);
	}

	.gender-tag {
		color: var(--success);
		background-color: var(--surface-soft);
	}

	.time {
		font-size: var(--font-px-xs);
		color: var(--text-secondary);
	}

	.batch-actions {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		display: flex;
		align-items: center;
		padding: 16rpx 24rpx;
		background-color: var(--surface);
		box-shadow: var(--shadow-soft);
		z-index: 100;
	}

	.select-all {
		display: flex;
		align-items: center;
		margin-right: 24rpx;
	}

	.select-text {
		font-size: var(--font-px-base);
		color: var(--text-primary);
		margin-left: 8rpx;
	}

	.selected-count {
		font-size: var(--font-px-sm);
		color: var(--text-secondary);
		flex: 1;
	}

	.batch-button {
		margin-left: 16rpx;
		padding: 0 24rpx;
		height: 64rpx;
		line-height: 64rpx;
		font-size: var(--font-px-base);
		border-radius: 32rpx;
	}
</style>
