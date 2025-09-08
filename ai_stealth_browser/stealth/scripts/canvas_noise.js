// Canvas noise injection to perturb fingerprint stability
const toBlob = HTMLCanvasElement.prototype.toBlob;
HTMLCanvasElement.prototype.toBlob = function () {
    const ctx = this.getContext('2d');
    if (ctx) { ctx.fillStyle = 'rgba(0,0,0,0.01)'; ctx.fillRect(0, 0, 1, 1); }
    return toBlob.apply(this, arguments);
};
