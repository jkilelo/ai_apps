// WebGL vendor/renderer spoof
(function () {
    try {
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function (param) {
            if (param === 37445) { return 'Intel Inc.'; } // UNMASKED_VENDOR_WEBGL
            if (param === 37446) { return 'Intel Iris OpenGL Engine'; } // UNMASKED_RENDERER_WEBGL
            return getParameter.call(this, param);
        };
    } catch (e) { }
})();
