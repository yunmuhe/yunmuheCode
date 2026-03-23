type PromiseLikeTuple<T> = Promise<[unknown, T] | T>;

uni.addInterceptor({
  returnValue<T>(res: T | PromiseLikeTuple<T>) {
    if (!(!!res && (typeof res === 'object' || typeof res === 'function') && typeof (res as PromiseLikeTuple<T>).then === 'function')) {
      return res;
    }

    return new Promise<T>((resolve, reject) => {
      (res as PromiseLikeTuple<T>).then((nextRes) => {
        if (!nextRes) {
          resolve(nextRes as T);
          return;
        }

        if (Array.isArray(nextRes)) {
          nextRes[0] ? reject(nextRes[0]) : resolve(nextRes[1] as T);
          return;
        }

        resolve(nextRes as T);
      });
    });
  },
});
