interface UniRouterLike {
	navigateTo: (options: { url: string }) => void;
	redirectTo: (options: { url: string }) => void;
	switchTab: (options: { url: string }) => void;
	reLaunch: (options: { url: string }) => void;
}

declare const uni: UniRouterLike;

export const routes = {
	index: '/pages/Index/Index',
	auth: '/pages/Auth/Auth',
	generate: '/pages/Generate/Generate',
	favorites: '/pages/Favorites/Favorites',
	history: '/pages/History/History',
	settings: '/pages/Settings/Settings'
} as const;

export const navigateTo = (url: string) => {
	uni.navigateTo({ url });
};

export const redirectTo = (url: string) => {
	uni.redirectTo({ url });
};

export const switchTab = (url: string) => {
	uni.switchTab({ url });
};

export const reLaunch = (url: string) => {
	uni.reLaunch({ url });
};

