#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 viewportSize;
    float imageAspect;
    float reveal;
    float seed;
};
layout(binding = 1) uniform sampler2D source;

float noise(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7)) + seed * 19.19) * 43758.5453);
}

void main() {
    vec2 size = max(viewportSize, vec2(1.0));
    vec2 pixel = qt_TexCoord0 * size;
    float amount = clamp(reveal, 0.0, 1.0);
    float block = mix(64.0, 1.0, pow(amount, 1.5));
    vec2 uv = mix((floor(pixel / block) + 0.5) * block / size,
                  qt_TexCoord0, smoothstep(0.93, 1.0, amount));
    float screenAspect = size.x / size.y;
    // PreserveAspectCrop without relying on the source Image's visual geometry.
    if (screenAspect > imageAspect) uv.y = (uv.y - 0.5) * imageAspect / screenAspect + 0.5;
    else uv.x = (uv.x - 0.5) * screenAspect / imageAspect + 0.5;
    float threshold = noise(floor(pixel / 32.0));
    float visible = smoothstep(threshold, threshold + 0.08, amount * 1.08);
    vec4 color = texture(source, uv);
    fragColor = color * visible * qt_Opacity;
}
