// AudioContext fingerprint noise injection
(function () {
    try {
        const origGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function () {
            const data = origGetChannelData.apply(this, arguments);
            if (!this._ai_noise_applied) {
                for (let i = 0; i < data.length; i += 100) { // sparse perturbation
                    data[i] = data[i] + (Math.random() * 1e-5 - 5e-6);
                }
                this._ai_noise_applied = true;
            }
            return data;
        };
    } catch (e) { }
})();
