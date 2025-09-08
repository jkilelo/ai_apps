// Font enumeration masking
(function () {
    try {
        const origMeasureText = CanvasRenderingContext2D.prototype.measureText;
        CanvasRenderingContext2D.prototype.measureText = function (text) {
            const m = origMeasureText.call(this, text);
            // Introduce tiny deterministic variance based on text length
            try { Object.defineProperty(m, 'width', { value: m.width * (1 + ((text.length % 5) * 0.0004)), configurable: true }); } catch (e) { }
            return m;
        };
    } catch (e) { }
})();
