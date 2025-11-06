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
    vec3 fuchsia = vec3(1.0, 0.0, 1.0);
    float alpha = 0.6;
    vec3 baseColor = texture(tex0, fragTexCoords).rgb;
    vec3 finalColor = mix(baseColor, fuchsia, 0.7);
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

float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

void main()
{
    vec2 uv = fragTexCoords;
    float glitchAmount = 0.02;
    float offsetR = sin(time * 10.0 + uv.y * 50.0) * glitchAmount;
    float offsetB = cos(time * 8.0 + uv.y * 30.0) * glitchAmount;
    float r = texture(tex0, uv + vec2(offsetR, 0.0)).r;
    float g = texture(tex0, uv).g;
    float b = texture(tex0, uv + vec2(offsetB, 0.0)).b;
    vec3 baseColor = vec3(r, g, b);
    float blockY = floor(uv.y * 30.0);
    float blockRandom = random(vec2(blockY, floor(time * 2.0)));
    if (blockRandom > 0.8) {
        baseColor = vec3(1.0, 1.0, 0.0) * (blockRandom * 1.2);
        uv.x += (blockRandom - 0.9) * 0.5;
    } else if (blockRandom > 0.6) {
        baseColor *= 0.1;
    }
    float pixelSize = 20.0;
    if (uv.y > 0.6) {
        vec2 pixelUV = floor(uv * pixelSize) / pixelSize;
        float pixelRandom = random(pixelUV + vec2(time * 0.5, 0.0));
        if (pixelRandom > 0.5) {
            baseColor = vec3(
                random(pixelUV + vec2(1.0, time)),
                random(pixelUV + vec2(2.0, time)) * 0.3,
                random(pixelUV + vec2(3.0, time))
            );
        }
    }
    float noise = random(uv + vec2(time * 10.0, 0.0)) * 0.15;
    baseColor += vec3(noise);
    float artifact = step(0.98, random(floor(uv * 100.0) + vec2(time * 5.0, 0.0)));
    baseColor += vec3(1.0, 1.0, 0.0) * artifact;
    fragColor = vec4(baseColor, 1.0);
}

'''

threshold_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform float time;

float noise(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
}

float smoothNoise(vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);
    f = f * f * (3.0 - 2.0 * f);
    
    float a = noise(i);
    float b = noise(i + vec2(1.0, 0.0));
    float c = noise(i + vec2(0.0, 1.0));
    float d = noise(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

void main()
{
    vec3 texColor = texture(tex0, fragTexCoords).rgb;
    float luminance = dot(texColor, vec3(0.299, 0.587, 0.114));
    
    vec3 brightCopper = vec3(0.95, 0.64, 0.38);   // Cobre brillante
    vec3 darkCopper = vec3(0.72, 0.45, 0.20);     // Cobre oscuro
    
    vec3 lightPatina = vec3(0.40, 0.80, 0.67);    // Pátina verde clara
    vec3 darkPatina = vec3(0.13, 0.55, 0.45);     // Pátina verde oscura
    vec3 rustBrown = vec3(0.55, 0.27, 0.07);      // Marrón óxido
    
    float oxidationCycle = mod(time * 0.0167, 1.0);  // 0.0 = nuevo, 1.0 = muy oxidado
    
    float oxidationPattern = smoothNoise(fragTexCoords * 12.0 + vec2(time * 0.008, time * 0.005));
    oxidationPattern += smoothNoise(fragTexCoords * 6.0 + vec2(-time * 0.006, time * 0.004)) * 0.5;
    oxidationPattern += smoothNoise(fragTexCoords * 20.0 + vec2(time * 0.003, -time * 0.002)) * 0.3;
    oxidationPattern += smoothNoise(fragTexCoords * 35.0) * 0.2;
    oxidationPattern /= 2.0;
    
    float earlyOxidation = pow(oxidationCycle, 0.5);  // Raíz cuadrada hace que crezca más rápido al inicio
    
    float oxidationMask = smoothstep(0.15, 0.85, oxidationPattern);
    oxidationMask *= smoothstep(0.0, 1.0, earlyOxidation);  // Usa la curva acelerada
    
    float rustVariation = noise(fragTexCoords * 20.0);
    vec3 oxidationColor;
    if (rustVariation > 0.6) {
        oxidationColor = mix(lightPatina, darkPatina, oxidationPattern);
    } else {
        oxidationColor = mix(rustBrown, darkPatina, oxidationPattern * 0.5);
    }
    
    vec3 copperBase = mix(darkCopper, brightCopper, luminance);
    
    vec3 finalColor = mix(copperBase, oxidationColor, oxidationMask);
    
    float metallic = pow(luminance, 3.0) * (1.0 - oxidationMask * 0.7);
    finalColor += vec3(metallic * 0.3);
    
    float corrosion = smoothNoise(fragTexCoords * 35.0 + vec2(time * 0.004, time * 0.003));
    float corrosionStrength = smoothstep(0.75, 0.95, corrosion) * smoothstep(0.5, 1.0, oxidationCycle);
    finalColor = mix(finalColor, finalColor * 0.3, corrosionStrength);
    
    fragColor = vec4(finalColor, 1.0);
}

'''





