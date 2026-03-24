import assert from 'node:assert/strict';
import { createThemeCssVars } from '../common/theme';

const vars = createThemeCssVars({
	navFront: '#000000',
	navBackground: '#FFFFFF',
	tabColor: '#7A7E83',
	tabSelected: '#4A90E2',
	tabBackground: '#FFFFFF',
	tabBorder: 'black',
	pageBackground: '#F8F8F8',
	surface: '#FFFFFF',
	surfaceMuted: '#F3F5F7',
	surfaceSoft: '#FAFBFC',
	borderColor: '#E6E8EB',
	textPrimary: '#333333',
	textSecondary: '#8A9099',
	accent: '#4A90E2',
	accentSoft: '#EAF4FF',
	accentContrast: '#FFFFFF',
	success: '#2ECC71',
	danger: '#E74C3C',
	warning: '#FF8F4D',
	shadowSoft: '0 2rpx 10rpx rgba(0, 0, 0, 0.05)',
	interactiveActiveBg: '#EAF4FF',
	warningSoft: '#FFF7E8',
	warningBorder: '#FFD8A8',
	disabledBg: '#E6E8EB',
	disabledText: '#A8B0BA',
	disabledIcon: '#C1C7D0',
});

assert.equal(vars['--warning-soft'], '#FFF7E8');
assert.equal(vars['--warning-border'], '#FFD8A8');
assert.equal(vars['--disabled-bg'], '#E6E8EB');
assert.equal(vars['--disabled-text'], '#A8B0BA');
assert.equal(vars['--disabled-icon'], '#C1C7D0');

console.log('theme token tests passed');
