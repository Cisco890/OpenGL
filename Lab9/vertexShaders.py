

vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;


void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);

    fragPosition = modelMatrix * vec4(inPosition, 1.0);

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));

    fragTexCoords = inTexCoords;
}

'''


wave_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;

void main()
{
    vec3 pos = inPosition;
    
    // Glitch vertical displacement
    float glitchStrength = 0.3;
    float glitchFreq = 20.0;
    
    // Random glitch blocks based on Y position
    float blockIndex = floor(pos.y * glitchFreq);
    float glitchRandom = fract(sin(blockIndex * 12.9898 + time * 0.5) * 43758.5453);
    
    // Horizontal displacement for glitch effect
    if (glitchRandom > 0.7) {
        pos.x += sin(time * 10.0 + blockIndex) * glitchStrength;
        pos.z += cos(time * 10.0 + blockIndex) * glitchStrength * 0.5;
    }
    
    // Pixel/vertex jitter for digital corruption
    float jitter = sin(pos.x * 50.0 + time * 5.0) * cos(pos.y * 50.0 + time * 3.0);
    pos += inNormals * jitter * 0.05;
    
    fragPosition = modelMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''