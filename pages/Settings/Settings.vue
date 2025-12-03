<template>
	<view class="settings-container">
		<!-- 顶部导航栏 -->
		<view class="nav-bar">
			<button class="back-btn" @click="handleBack">
				<uni-icons type="arrowleft" size="24" color="#333"></uni-icons>
			</button>
			<text class="page-title">设置</text>
			<view class="placeholder"></view>
		</view>

		<!-- 用户信息区域 -->
		<view class="user-section">
			<view class="user-avatar" @click="handleUserClick">
				<image v-if="isLogin" class="avatar-image"
					:src="userInfo.avatar || 'https://ai-public.mastergo.com/ai/img_res/ab95285ae27e91c77528f5798b063ad2.jpg'"
					mode="aspectFill" />
				<uni-icons v-else type="contact" size="60" color="#999" />
			</view>
			<view class="user-info">
				<text v-if="isLogin" class="user-name">{{ userInfo.nickname }}</text>
				<text v-else class="login-text" @click="handleLogin">点击登录</text>
				<text v-if="isLogin && userInfo.vip" class="vip-tag">高级会员</text>
				<text v-else-if="isLogin" class="member-tag">普通会员</text>
			</view>
		</view>

		<!-- 智能体连接与状态 -->
		<view class="settings-group">
			<text class="group-title">智能体连接</text>
			<view class="settings-item">
				<text class="item-label">当前地址</text>
				<text class="item-value" style="font-size: 24rpx; word-break: break-all;">{{ apiBaseUrl }}</text>
			</view>
			<view class="settings-item">
				<text class="item-label">连接状态</text>
				<view style="display:flex;align-items:center;">
					<view :style="{width:'14rpx',height:'14rpx',borderRadius:'50%',backgroundColor:health.ok?'#2ecc71':'#e74c3c',marginRight:'12rpx'}"></view>
					<text class="item-value">{{ health.ok ? '已连接' : '未连接' }}</text>
					<text v-if="health.version" style="margin-left:12rpx;color:#999;">v{{ health.version }}</text>
					<button class="stats-btn" style="margin-left:16rpx;" size="mini" @click="refreshHealth" :disabled="health.loading">
						{{ health.loading ? '检查中...' : '重新检查' }}
					</button>
				</view>
			</view>
		</view>

		<!-- 偏好设置分组（含默认API提供商） -->
		<view class="settings-group">
			<text class="group-title">偏好设置</text>
			<view class="settings-item">
				<text class="item-label">默认生成数量</text>
				<uni-number-box v-model="settings.generateCount" :min="1" :max="10" />
			</view>
			<view class="settings-item" v-if="apiOptions.length">
				<text class="item-label">默认API提供商</text>
				<picker mode="selector" :range="apiOptionLabels" :value="apiIndex" @change="handleApiChange">
					<view class="picker-value">{{ apiOptionLabels[apiIndex] }}</view>
				</picker>
			</view>
			<view class="settings-item">
				<text class="item-label">默认风格偏好</text>
				<uni-segmented-control :current="styleIndex" :values="styles" @clickItem="handleStyleChange" />
			</view>
			<view class="settings-item">
				<text class="item-label">自动复制结果</text>
				<switch :checked="settings.autoCopy" @change="handleAutoCopyChange" color="#4a90e2" />
			</view>
		</view>

		<!-- 显示设置分组 -->
		<view class="settings-group">
			<text class="group-title">显示设置</text>
			<view class="settings-item">
				<text class="item-label">主题模式</text>
				<radio-group @change="handleThemeChange">
					<label class="radio-item" v-for="item in themes" :key="item.value">
						<radio :value="item.value" :checked="settings.theme === item.value" />
						<text>{{ item.name }}</text>
					</label>
				</radio-group>
			</view>
			<view class="settings-item">
				<text class="item-label">字体大小</text>
				<slider :value="fontSizeIndex" :min="0" :max="2" @change="handleFontSizeChange" :step="1"
					activeColor="#4a90e2" />
				<view class="slider-labels">
					<text>小</text>
					<text>中</text>
					<text>大</text>
				</view>
			</view>
			<view class="settings-item">
				<text class="item-label">动画效果</text>
				<switch :checked="settings.animation" @change="handleAnimationChange" color="#4a90e2" />
			</view>
		</view>

		<!-- 存储设置分组 -->
		<view class="settings-group">
			<text class="group-title">存储设置</text>
			<view class="settings-item">
				<text class="item-label">历史记录保留时间</text>
				<picker mode="selector" :range="retentionTimes" :value="retentionIndex" @change="handleRetentionChange">
					<view class="picker-value">
						{{ retentionTimes[retentionIndex] }}
						<uni-icons type="arrowright" size="16" color="#999" />
					</view>
				</picker>
			</view>
			<view class="settings-item">
				<text class="item-label">自动清理设置</text>
				<switch :checked="settings.autoClean" @change="handleAutoCleanChange" color="#4a90e2" />
			</view>
			<view class="settings-item">
				<text class="item-label">数据备份与恢复</text>
				<button type="default" size="mini" @click="handleBackup" class="backup-btn">备份</button>
			</view>
		</view>

		<!-- 账户与数据分组 -->
		<view class="settings-group">
			<text class="group-title">账户与数据</text>
			<view class="settings-item">
				<text class="item-label">云端同步</text>
				<switch :checked="settings.cloudSync" @change="handleCloudSyncChange" color="#4a90e2" />
			</view>
			<view class="settings-item">
				<text class="item-label">数据统计</text>
				<button type="default" size="mini" @click="handleViewStats" class="stats-btn">查看</button>
			</view>
			<view class="settings-item">
				<text class="item-label">清除缓存</text>
				<button type="default" size="mini" @click="handleClearCache" class="clear-btn">清除</button>
			</view>
		</view>

		<!-- 关于与支持分组 -->
		<view class="settings-group">
			<text class="group-title">关于与支持</text>
			<view class="settings-item">
				<text class="item-label">应用版本</text>
				<text class="item-value">v1.2.0</text>
			</view>
			<view class="settings-item" @click="handleUserAgreement">
				<text class="item-label">用户协议</text>
				<uni-icons type="arrowright" size="16" color="#999" />
			</view>
			<view class="settings-item" @click="handlePrivacyPolicy">
				<text class="item-label">隐私政策</text>
				<uni-icons type="arrowright" size="16" color="#999" />
			</view>
			<view class="settings-item" @click="handleFeedback">
				<text class="item-label">反馈与帮助</text>
				<uni-icons type="arrowright" size="16" color="#999" />
			</view>
			<view class="settings-item" @click="handleShareApp">
				<text class="item-label">分享应用</text>
				<uni-icons type="arrowright" size="16" color="#999" />
			</view>
		</view>
	</view>
</template>

<script lang="ts" setup>
	import { ref, reactive, computed } from 'vue';
	import { onLoad } from '@dcloudio/uni-app';
	import {
		fetchBackendOptions,
		fetchBackendStats,
		fetchHealth,
		getApiBaseUrl
	} from '../../common/api';
	import { applyTheme, getStoredTheme, ThemeKey } from '../../common/theme';
	import uniIcons from '@/uni_modules/uni-icons/components/uni-icons/uni-icons.vue';
	import uniNumberBox from '@/uni_modules/uni-number-box/components/uni-number-box/uni-number-box.vue';
	import uniSegmentedControl from '@/uni_modules/uni-segmented-control/components/uni-segmented-control/uni-segmented-control.vue';

	const isLogin = ref(false);
	const userInfo = reactive({
		nickname: '用户名',
		avatar: '',
		vip: false
	});

	const settings = reactive({
		generateCount: 3,
		aiModel: 'gpt-4',
		stylePreference: 'realistic',
		autoCopy: true,
		theme: 'light',
		fontSize: 'medium',
		animation: true,
		retentionTime: '30天',
		autoClean: false,
		cloudSync: true
	});

	const styles = ['写实', '卡通', '抽象'];
	const styleIndex = ref(0);

	// 接入后端：可用API与健康、统计
	const apiBaseUrl = getApiBaseUrl();
	const apiOptions = ref<string[]>([]);
	const apiIndex = ref(0);
	const apiLabelMap: Record<string, string> = {
		paiou: '派欧云',
		aistudio: 'Aistudio',
		baidu: '百度千帆',
		siliconflow: 'SiliconFlow',
		aliyun: '阿里云',
		mock: '模拟接口',
	};
	const apiOptionLabels = computed(() => apiOptions.value.map(k => apiLabelMap[k] || k));

	const health = ref({ ok: false, version: '', loading: false });
	const stats = ref<any>(null);

	const themes = [
		{ name: '浅色', value: 'light' },
		{ name: '深色', value: 'dark' },
		{ name: '自动', value: 'auto' },
		{ name: '蓝色', value: 'blue' },
		{ name: '绿色', value: 'green' },
		{ name: '粉色', value: 'pink' },
		{ name: '紫色', value: 'purple' }
	];

	const fontSizes = ['small', 'medium', 'large'];
	const fontSizeIndex = ref(1);

	const retentionTimes = ['7天', '30天', '永久'];
	const retentionIndex = ref(1);

	const handleBack = () => {
		uni.navigateBack();
	};

	const handleUserClick = () => {
		if (!isLogin.value) {
			handleLogin();
		} else {
			// 跳转到用户详情页
		}
	};

	const handleLogin = () => {
		uni.navigateTo({
			url: '/pages/login/login'
		});
	};

	const handleStyleChange = (e : any) => {
		styleIndex.value = e.currentIndex;
		settings.stylePreference = ['realistic', 'cartoon', 'abstract'][e.currentIndex];
	};

	const handleAutoCopyChange = (e : any) => {
		settings.autoCopy = e.detail.value;
	};

	const syncThemeFromStorage = () => {
		const stored = getStoredTheme();
		settings.theme = stored;
		applyTheme(stored);
	};

	const handleThemeChange = (e : any) => {
		const value = (e?.detail?.value ?? 'light') as ThemeKey;
		settings.theme = value;
		applyTheme(value);
	};

	const handleFontSizeChange = (e : any) => {
		fontSizeIndex.value = e.detail.value;
		settings.fontSize = fontSizes[e.detail.value];
	};

	const handleAnimationChange = (e : any) => {
		settings.animation = e.detail.value;
	};

	const handleRetentionChange = (e : any) => {
		retentionIndex.value = e.detail.value;
		settings.retentionTime = retentionTimes[e.detail.value];
	};

	const handleAutoCleanChange = (e : any) => {
		settings.autoClean = e.detail.value;
	};

	const handleBackup = () => {
		uni.showToast({
			title: '备份成功',
			icon: 'success'
		});
	};

	const handleCloudSyncChange = (e : any) => {
		settings.cloudSync = e.detail.value;
	};

	const handleViewStats = () => {
		// 显示简要统计信息
		if (!stats.value) {
			uni.showToast({ title: '暂无统计数据', icon: 'none' });
			return;
		}
		uni.showModal({
			title: '系统统计',
			content: `可用API：${stats.value.available_apis}\n缓存条目：${stats.value.cache_stats?.active_entries ?? '-'}\nAPI状态：${Object.keys(stats.value.api_status || {}).length} 个`,
			showCancel: false
		});
	};

	const handleClearCache = () => {
		uni.showModal({
			title: '提示',
			content: '确定要清除缓存吗？',
			success: (res) => {
				if (res.confirm) {
					// 目前后端未提供清理接口，可在此扩展 /cache/clear
					uni.showToast({ title: '暂不支持，后端待扩展', icon: 'none' });
				}
			}
		});
	};

	const handleUserAgreement = () => {
		uni.navigateTo({
			url: '/pages/agreement/agreement?type=user'
		});
	};

	const handlePrivacyPolicy = () => {
		uni.navigateTo({
			url: '/pages/agreement/agreement?type=privacy'
		});
	};

	const handleFeedback = () => {
		uni.navigateTo({
			url: '/pages/feedback/feedback'
		});
	};

	const handleShareApp = () => {
		uni.share({
			provider: 'weixin',
			type: 0,
			title: '分享应用',
			success: () => {
				uni.showToast({
					title: '分享成功',
					icon: 'success'
				});
			}
		});
	};

	// 载入后端选项、健康与统计
	const loadOptions = async () => {
		try {
			const res = await fetchBackendOptions();
			if (res.success && res.options) {
				apiOptions.value = res.options.apis || [];
				// 从本地读取默认API（如果存在）
				const saved = uni.getStorageSync('preferred_api');
				if (saved && apiOptions.value.length) {
					const idx = apiOptions.value.indexOf(saved);
					apiIndex.value = idx >= 0 ? idx : 0;
				}
			}
		} catch (e) {}
	};

	const loadStats = async () => {
		try {
			const res = await fetchBackendStats();
			if (res.success) {
				stats.value = res.stats;
			}
		} catch (e) {}
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

	const handleApiChange = (e : any) => {
		apiIndex.value = Number(e.detail.value) || 0;
		const value = apiOptions.value[apiIndex.value];
		if (value) {
			uni.setStorageSync('preferred_api', value);
			uni.showToast({ title: `默认API已设为：${apiLabelMap[value] || value}`, icon: 'none' });
		}
	};

	onLoad(() => {
		syncThemeFromStorage();
		loadOptions();
		loadStats();
		refreshHealth();
	});
</script>

<style>
	page {
		height: 100%;
		background-color: #f5f5f5;
	}

	.settings-container {
		padding-bottom: 40rpx;
	}

	.nav-bar {
		height: 44px;
		background-color: #ffffff;
		border-bottom: 1px solid #eee;
		display: flex;
		align-items: center;
		justify-content: space-between;
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

	.page-title {
		flex: 1;
		font-size: 16px;
		font-weight: bold;
		color: #333;
		text-align: center;
	}

	.placeholder {
		width: 30px;
	}

	.user-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 40rpx 0;
		background-color: #fff;
		margin-bottom: 20rpx;
	}

	.user-avatar {
		width: 120rpx;
		height: 120rpx;
		border-radius: 50%;
		background-color: #f0f0f0;
		display: flex;
		justify-content: center;
		align-items: center;
		margin-bottom: 20rpx;
		overflow: hidden;
	}

	.avatar-image {
		width: 100%;
		height: 100%;
	}

	.user-info {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.user-name {
		font-size: 36rpx;
		font-weight: bold;
		color: #333;
		margin-bottom: 10rpx;
	}

	.login-text {
		font-size: 36rpx;
		color: #4a90e2;
		font-weight: bold;
	}

	.vip-tag {
		font-size: 24rpx;
		color: #fff;
		background-color: #ff9500;
		padding: 4rpx 16rpx;
		border-radius: 20rpx;
	}

	.member-tag {
		font-size: 24rpx;
		color: #999;
		background-color: #f0f0f0;
		padding: 4rpx 16rpx;
		border-radius: 20rpx;
	}

	.settings-group {
		background-color: #fff;
		margin-bottom: 20rpx;
		border-radius: 12rpx;
		overflow: hidden;
	}

	.group-title {
		display: block;
		padding: 24rpx 32rpx;
		font-size: 28rpx;
		color: #999;
		background-color: #f9f9f9;
	}

	.settings-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 28rpx 32rpx;
		border-bottom: 1rpx solid #f0f0f0;
	}

	.settings-item:last-child {
		border-bottom: none;
	}

	.item-label {
		font-size: 32rpx;
		color: #333;
	}

	.item-value {
		font-size: 32rpx;
		color: #999;
	}

	.picker-value {
		display: flex;
		align-items: center;
		color: #999;
	}

	.radio-item {
		margin-right: 40rpx;
		display: inline-flex;
		align-items: center;
	}

	.radio-item text {
		margin-left: 10rpx;
		font-size: 28rpx;
		color: #333;
	}

	.slider-labels {
		display: flex;
		justify-content: space-between;
		width: 100%;
		margin-top: 10rpx;
	}

	.slider-labels text {
		font-size: 24rpx;
		color: #999;
	}

	.backup-btn,
	.stats-btn,
	.clear-btn,
	.config-btn {
		border: 1rpx solid #4a90e2;
		color: #4a90e2;
		background-color: transparent;
		border-radius: 40rpx;
		padding: 0 24rpx;
		height: 56rpx;
		line-height: 56rpx;
	}

	.config-btn.danger {
		border-color: #e74c3c;
		color: #e74c3c;
	}

	.backup-btn:active,
	.stats-btn:active,
	.clear-btn:active,
	.config-btn:active {
		background-color: rgba(74, 144, 226, 0.1);
	}

	.config-btn.danger:active {
		background-color: rgba(231, 76, 60, 0.1);
	}
</style>