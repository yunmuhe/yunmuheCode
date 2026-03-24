const DEFAULT_APP_TITLE = '智能姓名生成器';

export const syncH5PageTitle = (title?: string): void => {
	if (typeof document === 'undefined') {
		return;
	}

	const nextTitle = String(title || '').trim() || DEFAULT_APP_TITLE;
	if (document.title !== nextTitle) {
		document.title = nextTitle;
	}
};
