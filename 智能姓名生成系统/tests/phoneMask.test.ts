import assert from 'node:assert/strict';
import { maskPhoneNumber } from '../common/phoneMask';

assert.equal(maskPhoneNumber('13800138000'), '*******8000');
assert.equal(maskPhoneNumber('1234567'), '*******');
assert.equal(maskPhoneNumber(''), '');
assert.equal(maskPhoneNumber(' 13800138000 '), '*******8000');

console.log('phoneMask tests passed');
