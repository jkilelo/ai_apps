// Timezone masking script
Intl.DateTimeFormat.prototype.resolvedOptions = new Proxy(Intl.DateTimeFormat.prototype.resolvedOptions, {
    apply(target, thisArg, argArray) {
        const r = Reflect.apply(target, thisArg, argArray);
        r.timeZone = 'UTC';
        return r;
    }
});
