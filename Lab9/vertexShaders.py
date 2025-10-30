

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
    
    float glitchStrength = 0.3;
    float glitchFreq = 20.0;
    
    float blockIndex = floor(pos.y * glitchFreq);
    float glitchRandom = fract(sin(blockIndex * 12.9898 + time * 0.5) * 43758.5453);
    
    if (glitchRandom > 0.7) {
        pos.x += sin(time * 10.0 + blockIndex) * glitchStrength;
        pos.z += cos(time * 10.0 + blockIndex) * glitchStrength * 0.5;
    }
    
    float jitter = sin(pos.x * 50.0 + time * 5.0) * cos(pos.y * 50.0 + time * 3.0);
    pos += inNormals * jitter * 0.05;
    
    fragPosition = modelMatrix * vec4(pos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''

expand_shader = '''
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
    int triIndex = gl_VertexID / 3;
    
    float angle1 = float(triIndex) * 2.3456;
    float angle2 = float(triIndex) * 1.2345;
    
    vec3 separationDir = normalize(vec3(
        sin(angle1) * cos(angle2),
        sin(angle2),
        cos(angle1) * cos(angle2)
    ));
    
    float separationAmount = 0.3;
    
    vec3 centerOffset = inPosition * 0.1;  // Offset basado en posicion para efecto radial
    vec3 separatedPos = inPosition + separationDir * separationAmount + centerOffset;
    
    fragPosition = modelMatrix * vec4(separatedPos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''

slime_shader = '''
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
    
    float wave1 = sin(pos.x * 3.0 + time * 2.0) * 0.08;
    float wave2 = cos(pos.y * 4.0 + time * 1.5) * 0.06;
    float wave3 = sin(pos.z * 5.0 + time * 2.5) * 0.05;
    
    float wobble = sin(pos.x * 2.0 + time) * cos(pos.y * 2.0 + time * 0.8) * 0.1;
    
    vec3 slimePos = pos + inNormals * (wave1 + wave2 + wave3 + wobble);
    
    float dripFactor = sin(pos.x * 10.0 + time * 3.0) * cos(pos.z * 10.0 + time * 2.0);
    dripFactor = max(0.0, dripFactor);  // Solo valores positivos
    slimePos.y -= dripFactor * 0.15;
    
    float pulse = sin(time * 1.5) * 0.03;
    slimePos += inNormals * pulse;
    
    fragPosition = modelMatrix * vec4(slimePos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize(vec3(modelMatrix * vec4(inNormals, 0.0)));
    fragTexCoords = inTexCoords;
}

'''