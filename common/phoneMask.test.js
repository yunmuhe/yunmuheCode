const assert = require("node:assert/strict");
const { maskPhoneNumber } = require("./phoneMask");

assert.equal(maskPhoneNumber("13800138000"), "*******8000");
assert.equal(maskPhoneNumber("1234567"), "*******");
assert.equal(maskPhoneNumber(""), "");

console.log("phoneMask tests passed");
