import assert from "node:assert/strict";
import * as settingsModule from "../common/appSettings.ts";

const {
    DEFAULT_SETTINGS,
    readAppSettings,
    updateAppSettings,
} = (settingsModule.default ?? settingsModule) as {
    DEFAULT_SETTINGS: typeof import("../common/appSettings.ts").DEFAULT_SETTINGS;
    readAppSettings: typeof import("../common/appSettings.ts").readAppSettings;
    updateAppSettings: typeof import("../common/appSettings.ts").updateAppSettings;
};

type StorageMap = Record<string, unknown>;

const storage: StorageMap = {};

const uniMock = {
    getStorageSync(key: string) {
        return storage[key];
    },
    setStorageSync(key: string, value: unknown) {
        storage[key] = value;
    },
};

Object.assign(globalThis, { uni: uniMock });

const resetStorage = () => {
    Object.keys(storage).forEach((key) => {
        delete storage[key];
    });
};

const testReadDefaults = () => {
    resetStorage();

    const settings = readAppSettings();

    assert.deepEqual(settings, DEFAULT_SETTINGS);
};

const testRepairInvalidStoredValues = () => {
    resetStorage();
    storage.app_settings = {
        generateCount: 99,
        stylePreference: "unknown",
        autoCopy: "yes",
        theme: "neon",
        fontSize: "huge",
        animation: null,
        retentionTime: "365天",
        autoClean: "nope",
        cloudSync: 1,
    };

    const settings = readAppSettings();

    assert.equal(settings.generateCount, 10);
    assert.equal(settings.stylePreference, DEFAULT_SETTINGS.stylePreference);
    assert.equal(settings.autoCopy, DEFAULT_SETTINGS.autoCopy);
    assert.equal(settings.theme, DEFAULT_SETTINGS.theme);
    assert.equal(settings.fontSize, DEFAULT_SETTINGS.fontSize);
    assert.equal(settings.animation, DEFAULT_SETTINGS.animation);
    assert.equal(settings.retentionTime, DEFAULT_SETTINGS.retentionTime);
    assert.equal(settings.autoClean, DEFAULT_SETTINGS.autoClean);
    assert.equal(settings.cloudSync, DEFAULT_SETTINGS.cloudSync);
};

const testUpdatePersistsMergedSettings = () => {
    resetStorage();

    const settings = updateAppSettings({
        stylePreference: "fantasy",
        theme: "dark",
        fontSize: "large",
    });

    assert.equal(settings.stylePreference, "fantasy");
    assert.equal(settings.theme, "dark");
    assert.equal(settings.fontSize, "large");
    assert.equal(
        (storage.app_settings as { stylePreference?: string }).stylePreference,
        "fantasy",
    );
};

testReadDefaults();
testRepairInvalidStoredValues();
testUpdatePersistsMergedSettings();

console.log("appSettings tests passed");
