<template>
	<view class="auth-page">
		<view class="bg-shape shape-1"></view>
		<view class="bg-shape shape-2"></view>

		<view class="auth-card">
			<view class="brand">
				<text class="brand-title">{{ copy.brandTitle }}</text>
				<text class="brand-subtitle">{{ copy.brandSubtitle }}</text>
			</view>

			<view class="tabs">
				<view class="tab" :class="{ active: mode === 'login' }" @click="switchMode('login')">
					<text>{{ copy.login }}</text>
				</view>
				<view class="tab" :class="{ active: mode === 'register' }" @click="switchMode('register')">
					<text>{{ copy.register }}</text>
				</view>
			</view>

			<view class="form">
				<view class="field">
					<text class="label">{{ copy.phone }}</text>
					<input
						v-model.trim="form.phone"
						class="input"
						type="number"
						maxlength="11"
						:placeholder="copy.phonePlaceholder"
					/>
				</view>

				<view class="field">
					<text class="label">{{ copy.password }}</text>
					<view class="password-wrap">
						<input
							v-model="form.password"
							class="input password-input"
							:password="!showPassword"
							maxlength="20"
							:placeholder="copy.passwordPlaceholder"
						/>
						<text class="toggle-eye" @click="showPassword = !showPassword">
							{{ showPassword ? copy.hide : copy.show }}
						</text>
					</view>
				</view>

				<view class="field" v-if="mode === 'register'">
					<text class="label">{{ copy.confirmPassword }}</text>
					<view class="password-wrap">
						<input
							v-model="form.confirmPassword"
							class="input password-input"
							:password="!showConfirmPassword"
							maxlength="20"
							:placeholder="copy.confirmPasswordPlaceholder"
						/>
						<text class="toggle-eye" @click="showConfirmPassword = !showConfirmPassword">
							{{ showConfirmPassword ? copy.hide : copy.show }}
						</text>
					</view>
				</view>

				<view class="field" v-if="mode === 'register'">
					<text class="label">{{ copy.code }}</text>
					<view class="code-wrap">
						<input
							v-model.trim="form.code"
							class="input code-input"
							type="number"
							maxlength="6"
							:placeholder="copy.codePlaceholder"
						/>
						<button class="code-btn" :disabled="codeCountDown > 0" @click="sendCode">
							{{ codeCountDown > 0 ? codeCountDown + 's' : copy.sendCode }}
						</button>
					</view>
				</view>

				<checkbox-group class="protocol" @change="onProtocolChange" v-if="mode === 'register'">
					<label class="protocol-label">
						<checkbox value="agree" :checked="agreeProtocol" color="#0ea5e9" />
						<text>{{ copy.protocol }}</text>
					</label>
				</checkbox-group>

				<button class="submit-btn" :disabled="loading" @click="handleSubmit">
					{{ loading ? copy.processing : mode === 'login' ? copy.loginNow : copy.registerNow }}
				</button>
			</view>

			<view class="footer-tip">
				<text v-if="mode === 'login'">{{ copy.noAccount }}</text>
				<text v-else>{{ copy.hasAccount }}</text>
				<text class="jump-link" @click="switchMode(mode === 'login' ? 'register' : 'login')">
					{{ mode === 'login' ? copy.goRegister : copy.goLogin }}
				</text>
			</view>
		</view>
	</view>
</template>

<script>
import {
	authLogin,
	authMe,
	authRegister,
	clearAuthToken,
	getAuthToken,
	setAuthToken,
	setAuthUser,
} from '../../common/api';

export default {
	data() {
		return {
			mode: 'login',
			loading: false,
			showPassword: false,
			showConfirmPassword: false,
			agreeProtocol: false,
			codeCountDown: 0,
			codeTimer: null,
			form: {
				phone: '',
				password: '',
				confirmPassword: '',
				code: '',
			},
			copy: {
				brandTitle: '\u667a\u80fd\u59d3\u540d\u751f\u6210\u7cfb\u7edf',
				brandSubtitle: '\u767b\u5f55\u540e\u53ef\u540c\u6b65\u5386\u53f2\u8bb0\u5f55\u4e0e\u6536\u85cf',
				login: '\u767b\u5f55',
				register: '\u6ce8\u518c',
				phone: '\u624b\u673a\u53f7',
				phonePlaceholder: '\u8bf7\u8f93\u5165 11 \u4f4d\u624b\u673a\u53f7',
				password: '\u5bc6\u7801',
				passwordPlaceholder: '\u8bf7\u8f93\u5165\u5bc6\u7801\uff08\u81f3\u5c11 6 \u4f4d\uff09',
				confirmPassword: '\u786e\u8ba4\u5bc6\u7801',
				confirmPasswordPlaceholder: '\u8bf7\u518d\u6b21\u8f93\u5165\u5bc6\u7801',
				code: '\u9a8c\u8bc1\u7801',
				codePlaceholder: '\u8bf7\u8f93\u5165 6 \u4f4d\u9a8c\u8bc1\u7801',
				sendCode: '\u83b7\u53d6\u9a8c\u8bc1\u7801',
				hide: '\u9690\u85cf',
				show: '\u663e\u793a',
				protocol: '\u6211\u5df2\u9605\u8bfb\u5e76\u540c\u610f\u300a\u7528\u6237\u534f\u8bae\u300b\u548c\u300a\u9690\u79c1\u653f\u7b56\u300b',
				processing: '\u5904\u7406\u4e2d...',
				loginNow: '\u7acb\u5373\u767b\u5f55',
				registerNow: '\u7acb\u5373\u6ce8\u518c',
				noAccount: '\u8fd8\u6ca1\u6709\u8d26\u53f7\uff1f',
				hasAccount: '\u5df2\u6709\u8d26\u53f7\uff1f',
				goRegister: '\u53bb\u6ce8\u518c',
				goLogin: '\u53bb\u767b\u5f55',
			},
		};
	},
	onLoad() {
		this.tryAutoLogin();
	},
	onUnload() {
		this.clearCodeTimer();
	},
	methods: {
		async tryAutoLogin() {
			const token = getAuthToken();
			if (!token) return;
			try {
				const res = await authMe();
				if (res.success && res.user) {
					setAuthUser(res.user);
					uni.reLaunch({ url: '/pages/Index/Index' });
				} else {
					clearAuthToken();
				}
			} catch (error) {
				clearAuthToken();
			}
		},
		switchMode(mode) {
			this.mode = mode;
			this.loading = false;
			this.form.password = '';
			this.form.confirmPassword = '';
			this.form.code = '';
			this.agreeProtocol = false;
		},
		onProtocolChange(e) {
			this.agreeProtocol = (e.detail.value || []).indexOf('agree') !== -1;
		},
		isValidPhone(phone) {
			return /^1\d{10}$/.test(phone);
		},
		sendCode() {
			if (!this.isValidPhone(this.form.phone)) {
				uni.showToast({
					title: '\u8bf7\u5148\u8f93\u5165\u6b63\u786e\u624b\u673a\u53f7',
					icon: 'none',
				});
				return;
			}
			if (this.codeCountDown > 0) return;

			this.codeCountDown = 60;
			this.codeTimer = setInterval(() => {
				this.codeCountDown -= 1;
				if (this.codeCountDown <= 0) {
					this.clearCodeTimer();
				}
			}, 1000);

			uni.showToast({
				title: '\u9a8c\u8bc1\u7801\u5df2\u53d1\u9001\uff08\u6f14\u793a\uff09',
				icon: 'none',
			});
		},
		clearCodeTimer() {
			if (this.codeTimer) {
				clearInterval(this.codeTimer);
				this.codeTimer = null;
			}
			this.codeCountDown = 0;
		},
		validateLogin() {
			if (!this.isValidPhone(this.form.phone)) {
				return '\u8bf7\u8f93\u5165\u6b63\u786e\u7684\u624b\u673a\u53f7';
			}
			if (!this.form.password || this.form.password.length < 6) {
				return '\u5bc6\u7801\u81f3\u5c11 6 \u4f4d';
			}
			return '';
		},
		validateRegister() {
			if (!this.isValidPhone(this.form.phone)) {
				return '\u8bf7\u8f93\u5165\u6b63\u786e\u7684\u624b\u673a\u53f7';
			}
			if (!this.form.password || this.form.password.length < 6) {
				return '\u5bc6\u7801\u81f3\u5c11 6 \u4f4d';
			}
			if (this.form.password !== this.form.confirmPassword) {
				return '\u4e24\u6b21\u8f93\u5165\u5bc6\u7801\u4e0d\u4e00\u81f4';
			}
			if (!/^\d{6}$/.test(this.form.code)) {
				return '\u8bf7\u8f93\u5165 6 \u4f4d\u9a8c\u8bc1\u7801';
			}
			if (!this.agreeProtocol) {
				return '\u8bf7\u5148\u540c\u610f\u7528\u6237\u534f\u8bae\u548c\u9690\u79c1\u653f\u7b56';
			}
			return '';
		},
		async handleSubmit() {
			const validateError = this.mode === 'login' ? this.validateLogin() : this.validateRegister();
			if (validateError) {
				uni.showToast({ title: validateError, icon: 'none' });
				return;
			}

			this.loading = true;
			try {
				if (this.mode === 'register') {
					const registerRes = await authRegister({
						phone: this.form.phone,
						password: this.form.password,
						code: this.form.code,
					});
					if (!registerRes.success) {
						throw new Error(registerRes.error || '\u6ce8\u518c\u5931\u8d25');
					}
					uni.showToast({
						title: '\u6ce8\u518c\u6210\u529f\uff0c\u8bf7\u767b\u5f55',
						icon: 'success',
					});
					this.switchMode('login');
					return;
				}

				const loginRes = await authLogin({
					phone: this.form.phone,
					password: this.form.password,
				});
				if (!loginRes.success || !loginRes.token) {
					throw new Error(loginRes.error || '\u767b\u5f55\u5931\u8d25');
				}

				setAuthToken(loginRes.token);
				if (loginRes.user) {
					setAuthUser(loginRes.user);
				}

				uni.showToast({
					title: '\u767b\u5f55\u6210\u529f',
					icon: 'success',
				});
				setTimeout(() => {
					uni.reLaunch({ url: '/pages/Index/Index' });
				}, 300);
			} catch (error) {
				uni.showToast({
					title: error?.message || '\u8bf7\u6c42\u5931\u8d25',
					icon: 'none',
				});
			} finally {
				this.loading = false;
			}
		},
	},
};
</script>

<style>
page {
	height: 100%;
}

.auth-page {
	position: relative;
	min-height: 100%;
	padding: 50rpx 36rpx 40rpx;
	box-sizing: border-box;
	background: linear-gradient(160deg, #e0f2fe 0%, #f0f9ff 45%, #ecfeff 100%);
	overflow: hidden;
}

.bg-shape {
	position: absolute;
	border-radius: 999rpx;
	opacity: 0.35;
}

.shape-1 {
	width: 420rpx;
	height: 420rpx;
	background: linear-gradient(145deg, #7dd3fc, #22d3ee);
	top: -120rpx;
	right: -120rpx;
}

.shape-2 {
	width: 300rpx;
	height: 300rpx;
	background: linear-gradient(145deg, #38bdf8, #34d399);
	left: -110rpx;
	bottom: 40rpx;
}

.auth-card {
	position: relative;
	z-index: 1;
	margin-top: 40rpx;
	background: rgba(255, 255, 255, 0.95);
	backdrop-filter: blur(8px);
	border-radius: 28rpx;
	padding: 40rpx 34rpx;
	box-shadow: 0 20rpx 60rpx rgba(12, 74, 110, 0.15);
}

.brand {
	margin-bottom: 36rpx;
}

.brand-title {
	display: block;
	font-size: 42rpx;
	font-weight: 700;
	color: #0f172a;
	letter-spacing: 1rpx;
}

.brand-subtitle {
	display: block;
	margin-top: 12rpx;
	font-size: 25rpx;
	color: #475569;
}

.tabs {
	display: flex;
	background: #f1f5f9;
	border-radius: 20rpx;
	padding: 8rpx;
	margin-bottom: 34rpx;
}

.tab {
	flex: 1;
	text-align: center;
	padding: 16rpx 0;
	border-radius: 14rpx;
	color: #64748b;
	font-size: 28rpx;
	font-weight: 600;
	transition: all 0.2s ease;
}

.tab.active {
	background: #ffffff;
	color: #0ea5e9;
	box-shadow: 0 8rpx 18rpx rgba(14, 165, 233, 0.18);
}

.field {
	margin-bottom: 24rpx;
}

.label {
	display: block;
	font-size: 24rpx;
	color: #334155;
	margin-bottom: 10rpx;
}

.input {
	height: 84rpx;
	background: #f8fafc;
	border: 2rpx solid #e2e8f0;
	border-radius: 16rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #0f172a;
	box-sizing: border-box;
}

.password-wrap {
	position: relative;
}

.password-input {
	padding-right: 110rpx;
}

.toggle-eye {
	position: absolute;
	right: 24rpx;
	top: 50%;
	transform: translateY(-50%);
	font-size: 24rpx;
	color: #0284c7;
}

.code-wrap {
	display: flex;
	align-items: center;
}

.code-input {
	flex: 1;
	margin-right: 16rpx;
}

.code-btn {
	width: 190rpx;
	height: 84rpx;
	line-height: 84rpx;
	padding: 0;
	border-radius: 16rpx;
	background: linear-gradient(135deg, #0ea5e9, #06b6d4);
	color: #ffffff;
	font-size: 24rpx;
}

.code-btn[disabled] {
	background: #cbd5e1;
	color: #64748b;
}

.protocol {
	margin: 4rpx 0 26rpx;
}

.protocol-label {
	display: flex;
	align-items: center;
	font-size: 23rpx;
	color: #475569;
}

.submit-btn {
	height: 90rpx;
	line-height: 90rpx;
	border-radius: 18rpx;
	background: linear-gradient(135deg, #0284c7, #14b8a6);
	color: #ffffff;
	font-size: 30rpx;
	font-weight: 600;
}

.submit-btn[disabled] {
	background: #94a3b8;
	color: #e2e8f0;
}

.footer-tip {
	margin-top: 30rpx;
	text-align: center;
	font-size: 24rpx;
	color: #64748b;
}

.jump-link {
	margin-left: 8rpx;
	color: #0369a1;
	font-weight: 600;
}
</style>
