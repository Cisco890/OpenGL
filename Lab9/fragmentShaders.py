# GLSL

fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

void main()
{
    fragColor = texture(tex0, fragTexCoords);
}

'''
radioactive_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;

void main()
{
    // Color fucsia transparente
    vec3 fuchsia = vec3(1.0, 0.0, 1.0);  // RGB para fucsia/magenta
    float alpha = 0.6;  // Transparencia (0.0 = invisible, 1.0 = opaco)
    
    // Mezclar la textura base con el color fucsia
    vec3 baseColor = texture(tex0, fragTexCoords).rgb;
    vec3 finalColor = mix(baseColor, fuchsia, 0.7);  // 70% fucsia, 30% textura
    
    fragColor = vec4(finalColor, alpha);
}

'''

glitch_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform float time;

// Random function
float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

void main()
{
    vec2 uv = fragTexCoords;
    
    // Chromatic aberration / RGB split
    float glitchAmount = 0.02;
    float offsetR = sin(time * 10.0 + uv.y * 50.0) * glitchAmount;
    float offsetB = cos(time * 8.0 + uv.y * 30.0) * glitchAmount;
    
    // Sample texture with RGB offsets
    float r = texture(tex0, uv + vec2(offsetR, 0.0)).r;
    float g = texture(tex0, uv).g;
    float b = texture(tex0, uv + vec2(offsetB, 0.0)).b;
    
    vec3 baseColor = vec3(r, g, b);
    
    // Scanline blocks - horizontal glitch bands
    float blockY = floor(uv.y * 30.0);
    float blockRandom = random(vec2(blockY, floor(time * 2.0)));
    
    // Glitch bands with color corruption
    if (blockRandom > 0.8) {
        // Yellow corruption
        baseColor = vec3(1.0, 1.0, 0.0) * (blockRandom * 1.2);
        uv.x += (blockRandom - 0.9) * 0.5; // horizontal shift
    } else if (blockRandom > 0.6) {
        // Black corruption
        baseColor *= 0.1;
    }
    
    // Pixelation effect on upper areas (like the head in image)
    float pixelSize = 20.0;
    if (uv.y > 0.6) {
        vec2 pixelUV = floor(uv * pixelSize) / pixelSize;
        float pixelRandom = random(pixelUV + vec2(time * 0.5, 0.0));
        
        if (pixelRandom > 0.5) {
            // Colorful pixel corruption (red, blue, yellow mix)
            baseColor = vec3(
                random(pixelUV + vec2(1.0, time)),
                random(pixelUV + vec2(2.0, time)) * 0.3,
                random(pixelUV + vec2(3.0, time))
            );
        }
    }
    
    // Random noise overlay
    float noise = random(uv + vec2(time * 10.0, 0.0)) * 0.15;
    baseColor += vec3(noise);
    
    // Digital artifacts - random bright spots
    float artifact = step(0.98, random(floor(uv * 100.0) + vec2(time * 5.0, 0.0)));
    baseColor += vec3(1.0, 1.0, 0.0) * artifact;
    
    fragColor = vec4(baseColor, 1.0);
}

'''





