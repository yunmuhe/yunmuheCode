function maskPhoneNumber(phone) {
    const raw = String(phone || "").trim();
    if (!raw) return "";
    if (raw.length <= 7) return "*".repeat(raw.length);
    return `${"*".repeat(7)}${raw.slice(7)}`;
}

export { maskPhoneNumber };
