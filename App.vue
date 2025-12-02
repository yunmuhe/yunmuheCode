<script>
	import { applyTheme, getStoredTheme } from './common/theme'

	export default {
		onLaunch() {
			const theme = getStoredTheme();
			applyTheme(theme)
			console.log('App Launch')
		},
		onShow() {
			const theme = getStoredTheme();
			applyTheme(theme)
			console.log('App Show')
		},
		onHide() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/*每个页面公共css */
</style>
