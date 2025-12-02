<template>
	<view class="generate-page">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<view class="nav-content">
				<button class="back-btn" @click="handleBack">
					<uni-icons type="arrowleft" size="24" color="#333"></uni-icons>
				</button>
				<text class="page-title">姓名生成助手</text>
				<button class="batch-btn" @click="handleBatchGenerate">
					<uni-icons type="list" size="24" color="#333"></uni-icons>
				</button>
			</view>
		</view>
		<!-- 后端连接状态 -->
		<view class="health-bar">
			<view class="health-info">
				<view :class="['dot', health.ok ? 'ok' : 'bad']"></view>
				<text class="health-text">{{ health.ok ? '已连接' : '未连接' }}</text>
				<text class="health-sub" v-if="health.version">v{{ health.version }}</text>
			</view>
			<button class="refresh-btn" @click="refreshHealth" :disabled="health.loading">
				<uni-icons v-if="!health.loading" type="refresh" size="20" color="#333"></uni-icons>
				<uni-load-more v-else status="loading" iconType="circle" :showText="false" />
			</button>
		</view>
		<!-- 生成参数设置 -->
		<view class="options-panel">
			<view class="option-row">
				<picker mode="selector" :range="styleLabels" :value="styleIndex" @change="handleStyleChange">
					<view class="option-item">
						<text class="option-label">风格</text>
						<text class="option-value">{{ currentStyleLabel }}</text>
					</view>
				</picker>
				<picker mode="selector" :range="genderLabels" :value="genderIndex" @change="handleGenderChange">
					<view class="option-item">
						<text class="option-label">性别</text>
						<text class="option-value">{{ currentGenderLabel }}</text>
					</view>
				</picker>
			</view>
			<view class="option-row">
				<picker mode="selector" :range="ageLabels" :value="ageIndex" @change="handleAgeChange">
					<view class="option-item">
						<text class="option-label">年龄</text>
						<text class="option-value">{{ currentAgeLabel }}</text>
					</view>
				</picker>
				<picker mode="selector" :range="countLabels" :value="countIndex" @change="handleCountChange">
					<view class="option-item">
						<text class="option-label">数量</text>
						<text class="option-value">{{ currentCountLabel }}</text>
					</view>
				</picker>
			</view>
			<view class="option-row">
				<picker mode="selector" :range="apiLabels" :value="apiIndex" @change="handleApiChange">
					<view class="option-item">
						<text class="option-label">API</text>
						<text class="option-value">{{ currentApiLabel }}</text>
					</view>
				</picker>
				<view class="option-item readonly">
					<text class="option-label">接口地址</text>
					<text class="option-value base-url">{{ apiBaseUrl }}</text>
				</view>
			</view>
		</view>
		<!-- 聊天区域 -->
		<view class="chat-container">
			<scroll-view scroll-y class="messages-container" id="messagesContainer" :scroll-into-view="scrollIntoViewId">
				<!-- 系统欢迎消息 -->
				<view class="message system-message">
					<view class="message-bubble">
						<text class="message-text">您好！我是您的姓名生成助手，请告诉我您想要什么样的名字？</text>
					</view>
				</view>
				<!-- 用户最新请求 -->
				<view class="message user-message" v-if="lastQuery">
					<view class="message-bubble">
						<text class="message-text">{{ lastQuery }}</text>
					</view>
				</view>
				<!-- AI回复 -->
				<view class="message ai-message" v-if="generatedNames.length">
					<view class="avatar">
						<uni-icons type="person" size="24" color="#fff"></uni-icons>
					</view>
					<view class="message-content">
						<view class="message-bubble">
							<text class="message-text">为您推荐以下{{ generatedNames.length }}个姓名：</text>
							<view class="meta-info" v-if="apiMeta.apiName || apiMeta.model">
								<text v-if="apiMeta.apiName">API：{{ apiMeta.apiName }}</text>
								<text v-if="apiMeta.model">模型：{{ apiMeta.model }}</text>
							</view>
						</view>
						<view class="name-suggestions">
							<view class="suggestion-card" v-for="(name, index) in generatedNames" :key="name.id || index" :id="name.domId">
								<view class="card-header">
									<text class="name-text">{{ name.name }}</text>
									<view class="actions">
										<button class="action-btn" @click="toggleFavorite(index)">
											<uni-icons :type="name.isFavorite ? 'heart-filled' : 'heart'" size="20"
												:color="name.isFavorite ? '#ff6b6b' : '#999'"></uni-icons>
										</button>
									</view>
								</view>
								<text class="meaning-text">{{ name.meaning }}</text>
								<view class="tags">
									<view class="tag">{{ name.style }}</view>
									<view class="tag" v-if="name.source">来源：{{ name.source }}</view>
								</view>
								<view class="features" v-if="name.features && Object.keys(name.features).length">
									<text class="feature-pill" v-for="(value, key) in name.features" :key="key">
										{{ formatFeatureLabel(key, value) }}
									</text>
								</view>
							</view>
						</view>
					</view>
				</view>
				<view class="empty-state" v-else-if="!isGenerating">
					<uni-icons type="light" size="24" color="#999"></uni-icons>
					<text class="empty-text">输入描述并点击发送即可生成姓名</text>
				</view>
			</scroll-view>
		</view>
		<!-- 底部输入区域 -->
		<view class="input-area">
			<view class="input-container">
				<textarea v-model="description" placeholder="请输入您希望生成姓名的相关描述..." class="description-input"
					:auto-height="true" maxlength="500" />
				<view class="char-count">{{ description.length }}/500</view>
			</view>
			<button class="send-btn" @click="handleGenerate" :disabled="!description.trim() || isGenerating">
				<uni-icons v-if="!isGenerating" type="paperplane" size="24" color="#fff"></uni-icons>
				<uni-load-more v-else status="loading" iconType="circle" :showText="false" />
			</button>
		</view>
	</view>
</template>
<script lang="ts" setup>
	import { ref, computed, nextTick } from 'vue';
	import { onLoad } from '@dcloudio/uni-app';
	import {
		fetchBackendOptions,
		generateNames as generateNamesApi,
		getApiBaseUrl,
		fetchHealth,
		addFavorite,
		deleteFavorites,
		type GeneratedName,
	} from '../../common/api';

	interface NameCard extends GeneratedName {
		isFavorite: boolean;
		style: string;
		domId: string;
	}

	const description = ref('');
	const isGenerating = ref(false);
	const lastQuery = ref('');
	const generatedNames = ref<NameCard[]>([]);
	const scrollIntoViewId = ref('');

	const availableStyles = ref<string[]>([]);
	const availableGenders = ref<string[]>([]);
	const availableAges = ref<string[]>([]);
	const availableApis = ref<string[]>([]);

	const styleIndex = ref(0);
	const genderIndex = ref(0);
	const ageIndex = ref(0);
	const apiIndex = ref(0);
	const countIndex = ref(4); // 默认5个

	const countValues = ref<number[]>([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

	const apiMeta = ref({
		apiName: '',
		model: '',
	});

	const apiBaseUrl = getApiBaseUrl();

	const health = ref({
		ok: false,
		version: '',
		loading: false,
	});

	const styleLabelMap: Record<string, string> = {
		chinese_modern: '现代中文',
		chinese_traditional: '传统中文',
		chinese_classic: '古典中文',
		fantasy: '奇幻风格',
		western: '西方风格',
		japanese: '日式风格',
	};

	const genderLabelMap: Record<string, string> = {
		male: '男性',
		female: '女性',
		neutral: '中性',
	};

	const ageLabelMap: Record<string, string> = {
		child: '儿童',
		teen: '青少年',
		adult: '成年人',
		elder: '长者',
	};

	const apiLabelMap: Record<string, string> = {
		paiou: '派欧云',
		aistudio: 'Aistudio',
		baidu: '百度千帆',
		siliconflow: 'SiliconFlow',
		aliyun: '阿里云',
		mock: '模拟接口',
	};

	const styleLabels = computed(() => availableStyles.value.map((style) => styleLabelMap[style] || style));
	const genderLabels = computed(() => availableGenders.value.map((gender) => genderLabelMap[gender] || gender));
	const ageLabels = computed(() => availableAges.value.map((age) => ageLabelMap[age] || age));
	const apiLabels = computed(() =>
		availableApis.value.length
			? availableApis.value.map((api) => apiLabelMap[api] || api)
			: ['自动选择'],
	);
	const countLabels = computed(() => countValues.value.map((value) => `${value}个`));

	const currentStyle = computed(
		() => availableStyles.value[styleIndex.value] || availableStyles.value[0] || 'chinese_modern',
	);
	const currentGender = computed(
		() => availableGenders.value[genderIndex.value] || availableGenders.value[0] || 'neutral',
	);
	const currentAge = computed(() => availableAges.value[ageIndex.value] || availableAges.value[0] || 'adult');
	const currentApi = computed(() => availableApis.value[apiIndex.value]);
	const currentCount = computed(() => countValues.value[countIndex.value] || 5);

	const currentStyleLabel = computed(() => styleLabelMap[currentStyle.value] || currentStyle.value);
	const currentGenderLabel = computed(() => genderLabelMap[currentGender.value] || currentGender.value);
	const currentAgeLabel = computed(() => ageLabelMap[currentAge.value] || currentAge.value);
	const currentApiLabel = computed(() => {
		if (!availableApis.value.length) return '自动选择';
		const api = currentApi.value;
		return api ? apiLabelMap[api] || api : '自动选择';
	});
	const currentCountLabel = computed(() => `${currentCount.value}个`);

	const ensureDefaultOptions = () => {
		if (!availableStyles.value.length) {
			availableStyles.value = ['chinese_modern', 'chinese_traditional', 'fantasy'];
		}
		if (!availableGenders.value.length) {
			availableGenders.value = ['male', 'female', 'neutral'];
		}
		if (!availableAges.value.length) {
			availableAges.value = ['child', 'adult', 'elder'];
		}
	};

	const buildDomId = (value: string | undefined, index: number) => {
		const base = value && value.trim().length ? value : `name_${Date.now()}_${index}`;
		return `generated-${base.replace(/[^a-zA-Z0-9_-]/g, '')}`;
	};

	const loadOptions = async () => {
		try {
			const res = await fetchBackendOptions();
			if (res.success && res.options) {
				availableStyles.value = res.options.cultural_styles || [];
				availableGenders.value = res.options.genders || [];
				availableAges.value = res.options.ages || [];
				availableApis.value = res.options.apis || [];

				ensureDefaultOptions();

				// 读取设置页保存的默认 API（preferred_api），如果可用则默认选中
				try {
					const saved = uni.getStorageSync('preferred_api');
					if (saved && availableApis.value.length) {
						const idx = availableApis.value.indexOf(saved);
						if (idx >= 0) {
							apiIndex.value = idx;
						}
					}
				} catch (e) {}

				if (styleIndex.value >= availableStyles.value.length) {
					styleIndex.value = 0;
				}
				if (genderIndex.value >= availableGenders.value.length) {
					genderIndex.value = 0;
				}
				if (ageIndex.value >= availableAges.value.length) {
					ageIndex.value = 0;
				}
				if (availableApis.value.length === 0) {
					apiIndex.value = 0;
				} else if (apiIndex.value >= availableApis.value.length) {
					apiIndex.value = 0;
				}
			} else {
				throw new Error(res.error || '未能获取可用选项');
			}
		} catch (error) {
			console.warn('加载可用选项失败:', error);
			ensureDefaultOptions();
			uni.showToast({
				title: '选项加载失败，已使用默认配置',
				icon: 'none',
				duration: 2000,
			});
		}
	};

	onLoad(() => {
		// 加载可用选项
		loadOptions();

		// 刷新健康状态
		refreshHealth();
	});

	const handleBack = () => {
		uni.navigateBack();
	};
	const handleBatchGenerate = () => {
		// 批量生成功能逻辑
		console.log('进入批量生成页面');
	};
	const handleGenerate = async () => {
		if (!description.value.trim()) {
			uni.showToast({
				title: '请输入描述内容',
				icon: 'none',
			});
			return;
		}
		const promptText = description.value.trim();
		isGenerating.value = true;
		uni.showLoading({
			title: '生成中...',
			mask: true,
		});

		try {
			const payload = {
				description: promptText,
				count: currentCount.value,
				cultural_style: currentStyle.value,
				gender: currentGender.value,
				age: currentAge.value,
				preferred_api: currentApi.value,
				use_cache: true,
			};

			const res = await generateNamesApi(payload);

			if (!res.success) {
				throw new Error(res.error || '生成姓名失败');
			}

			const styleLabel = currentStyleLabel.value;

			generatedNames.value = (res.names || []).map((item, index) => ({
				id: item.id,
				name: item.name || '未命名',
				meaning: item.meaning || '暂无释义',
				source: item.source || res.api_name || '未知来源',
				features: item.features,
				isFavorite: false,
				style: styleLabel,
				domId: buildDomId(item.id, index),
			}));

			apiMeta.value = {
				apiName: res.api_name || '',
				model: res.model || '',
			};

			lastQuery.value = promptText;
			description.value = '';

			nextTick(() => {
				const lastCard = generatedNames.value[generatedNames.value.length - 1];
				scrollIntoViewId.value = lastCard ? lastCard.domId : '';
			});

			if (!generatedNames.value.length) {
				uni.showToast({
					title: '未获取到姓名结果',
					icon: 'none',
				});
			}
		} catch (error : any) {
				uni.showToast({
					title: error?.message || '生成失败，请稍后再试',
					icon: 'none',
					duration: 2000,
				});
		} finally {
			isGenerating.value = false;
			uni.hideLoading();
		}
	};
	const toggleFavorite = (index : number) => {
		if (!generatedNames.value[index]) return;
		const item = generatedNames.value[index];
		item.isFavorite = !item.isFavorite;
		if (item.isFavorite) {
			// 添加收藏
			addFavorite({
				id: item.id,
				name: item.name,
				meaning: item.meaning,
				style: item.style,
				gender: currentGenderLabel.value,
				source: item.source || apiMeta.value.apiName,
			}).catch(() => {
				uni.showToast({ title: '收藏失败', icon: 'none' });
				item.isFavorite = false;
			});
		} else {
			// 取消收藏
			deleteFavorites(item.id).catch(() => {
				uni.showToast({ title: '取消失败', icon: 'none' });
				item.isFavorite = true;
			});
		}
	};

	const handleStyleChange = (e : any) => {
		styleIndex.value = Number(e.detail.value) || 0;
	};
	const handleGenderChange = (e : any) => {
		genderIndex.value = Number(e.detail.value) || 0;
	};
	const handleAgeChange = (e : any) => {
		ageIndex.value = Number(e.detail.value) || 0;
	};
	const handleApiChange = (e : any) => {
		if (!availableApis.value.length) {
			apiIndex.value = 0;
			return;
		}
		apiIndex.value = Number(e.detail.value) || 0;
	};
	const handleCountChange = (e : any) => {
		countIndex.value = Number(e.detail.value) || 0;
	};

	const formatFeatureLabel = (key : string, value : any) => {
		const labelMap: Record<string, string> = {
			length: '长度',
			character_count: '字符数',
			word_count: '单词数',
			has_space: '含空格',
			is_chinese: '中文名',
			is_english: '英文名',
			tone_pattern: '音韵',
			stroke_count: '笔画',
		};

		const label = labelMap[key] || key;
		if (typeof value === 'boolean') {
			return `${label}:${value ? '是' : '否'}`;
		}

		return `${label}:${value}`;
	};

	const refreshHealth = async () => {
		try {
			health.value.loading = true;
			const res = await fetchHealth();
			health.value.ok = res?.status === 'healthy';
			health.value.version = res?.version || '';
		} catch (e) {
			health.value.ok = false;
		} finally {
			health.value.loading = false;
		}
	};
</script>
<style>
	page {
		height: 100%;
	}

	.generate-page {
		display: flex;
		flex-direction: column;
		height: 100%;
		background-color: #f0f0f0;
	}

	.nav-bar {
		height: 88rpx;
		background-color: #ffffff;
		border-bottom: 1px solid #eee;
		padding: 0 20rpx;
		box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
	}

	.nav-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 100%;
	}

	.health-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 10rpx 20rpx;
		background-color: #fff;
		border-bottom: 1px solid #eee;
	}

	.health-info {
		display: flex;
		align-items: center;
	}

	.dot {
		width: 16rpx;
		height: 16rpx;
		border-radius: 50%;
		margin-right: 12rpx;
		background-color: #ccc;
	}
	.dot.ok {
		background-color: #2ecc71;
	}
	.dot.bad {
		background-color: #e74c3c;
	}

	.health-text {
		font-size: 26rpx;
		color: #333;
		margin-right: 10rpx;
	}
	.health-sub {
		font-size: 22rpx;
		color: #999;
	}

	.refresh-btn {
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		background: none;
		border: none;
	}

	.options-panel {
		padding: 20rpx;
		background-color: #ffffff;
		border-bottom: 1px solid #eee;
	}

	.option-row {
		display: flex;
		justify-content: space-between;
		margin-bottom: 12rpx;
	}

	.option-row:last-child {
		margin-bottom: 0;
	}

	.option-item {
		flex: 1;
		background-color: #f6f6f6;
		border-radius: 12rpx;
		padding: 16rpx 20rpx;
		margin-right: 12rpx;
		display: flex;
		flex-direction: column;
	}

	.option-item:last-child {
		margin-right: 0;
	}

	.option-label {
		font-size: 24rpx;
		color: #888;
		margin-bottom: 8rpx;
	}

	.option-value {
		font-size: 28rpx;
		color: #333;
	}

	.option-item.readonly {
		background-color: #fff8e6;
	}

	.option-value.base-url {
		font-size: 24rpx;
		color: #ad8b00;
		word-break: break-all;
	}

	.page-title {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
	}

	.back-btn,
	.batch-btn {
		width: 60rpx;
		height: 60rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		background: none;
		padding: 0;
		margin: 0;
	}

	.chat-container {
		flex: 1;
		overflow: hidden;
		padding: 20rpx;
	}

	.messages-container {
		height: 100%;
	}

	.message {
		display: flex;
		margin-bottom: 30rpx;
	}

	.system-message {
		justify-content: center;
	}

	.user-message {
		justify-content: flex-end;
	}

	.ai-message {
		justify-content: flex-start;
	}

	.avatar {
		width: 60rpx;
		height: 60rpx;
		border-radius: 50%;
		background-color: #4a90e2;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 20rpx;
		flex-shrink: 0;
	}

	.message-content {
		max-width: 70%;
	}

	.message-bubble {
		background-color: #fff;
		border-radius: 16rpx;
		padding: 20rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.03);
	}

	.system-message .message-bubble {
		background-color: #e0e0e0;
	}

	.user-message .message-bubble {
		background-color: #4a90e2;
		color: #fff;
	}

	.ai-message .message-bubble {
		background-color: #fff;
	}

	.message-text {
		font-size: 28rpx;
		line-height: 40rpx;
	}

	.name-suggestions {
		margin-top: 20rpx;
	}

	.suggestion-card {
		background-color: #f8f8f8;
		border-radius: 16rpx;
		padding: 20rpx;
		margin-bottom: 20rpx;
	}

	.card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 15rpx;
	}

	.name-text {
		font-size: 32rpx;
		font-weight: bold;
		color: #333;
	}

	.actions {
		display: flex;
	}

	.action-btn {
		width: 50rpx;
		height: 50rpx;
		display: flex;
		align-items: center;
		justify-content: center;
		border: none;
		background: none;
		padding: 0;
	}

	.meaning-text {
		font-size: 26rpx;
		color: #666;
		line-height: 40rpx;
		margin-bottom: 15rpx;
	}

	.tags {
		display: flex;
		flex-wrap: wrap;
		gap: 12rpx;
	}

	.tag {
		font-size: 22rpx;
		color: #4a90e2;
		background-color: #eaf4ff;
		padding: 6rpx 16rpx;
		border-radius: 8rpx;
	}

	.features {
		margin-top: 12rpx;
		display: flex;
		flex-wrap: wrap;
		gap: 8rpx;
	}

	.feature-pill {
		font-size: 22rpx;
		color: #666;
		background-color: #f0f0f0;
		padding: 6rpx 14rpx;
		border-radius: 16rpx;
	}

	.meta-info {
		margin-top: 12rpx;
		display: flex;
		flex-direction: column;
		font-size: 24rpx;
		color: #666;
	}

	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 80rpx 20rpx;
		color: #999;
	}

	.empty-text {
		margin-top: 20rpx;
		font-size: 26rpx;
	}

	/* 底部输入区域 */
	.input-area {
		display: flex;
		align-items: flex-end;
		padding: 20rpx;
		background-color: #fff;
		border-top: 1px solid #eee;
	}

	.input-container {
		flex: 1;
		background-color: #f0f0f0;
		border-radius: 10rpx;
		padding: 15rpx;
		margin-right: 20rpx;
	}

	.description-input {
		width: 100%;
		min-height: 40rpx;
		max-height: 200rpx;
		font-size: 28rpx;
		line-height: 40rpx;
		color: #333;
		padding: 10rpx 0;
	}

	.char-count {
		text-align: right;
		font-size: 20rpx;
		color: #999;
		margin-top: 10rpx;
	}

	.send-btn {
		width: 80rpx;
		height: 80rpx;
		background-color: #4a90e2;
		color: #fff;
		border-radius: 50%;
		border: none;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.send-btn[disabled] {
		background-color: #ccc;
	}
</style>