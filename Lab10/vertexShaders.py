

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
    // Primero transformar al espacio del mundo para obtener la escala correcta
    vec4 worldPos = modelMatrix * vec4(inPosition, 1.0);
    vec3 pos = worldPos.xyz;
    
    // Usar las coordenadas del mundo para el efecto
    float glitchStrength = 0.3;
    float glitchFreq = 2.0;  // Reducir frecuencia para que funcione con modelos de diferentes tamaños
    
    float blockIndex = floor(pos.y * glitchFreq);
    float glitchRandom = fract(sin(blockIndex * 12.9898 + time * 0.5) * 43758.5453);
    
    if (glitchRandom > 0.7) {
        pos.x += sin(time * 10.0 + blockIndex) * glitchStrength;
        pos.z += cos(time * 10.0 + blockIndex) * glitchStrength * 0.5;
    }
    
    // Aplicar jitter basado en las coordenadas del mundo
    float jitter = sin(pos.x * 5.0 + time * 5.0) * cos(pos.y * 5.0 + time * 3.0);
    vec3 worldNormal = mat3(modelMatrix) * inNormals;
    pos += normalize(worldNormal) * jitter * 0.05;
    
    fragPosition = vec4(pos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize(worldNormal);
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
    // Usar la posición normalizada del vértice para crear direcciones únicas
    vec3 normalizedPos = normalize(inPosition);
    
    int triIndex = gl_VertexID / 3;
    
    float angle1 = float(triIndex) * 2.3456;
    float angle2 = float(triIndex) * 1.2345;
    
    vec3 separationDir = normalize(vec3(
        sin(angle1) * cos(angle2),
        sin(angle2),
        cos(angle1) * cos(angle2)
    ));
    
    // Transformar primero y luego aplicar separación en espacio del mundo
    vec4 worldPos = modelMatrix * vec4(inPosition, 1.0);
    
    // Aplicar separación proporcional al tamaño del modelo
    float separationAmount = 0.5;
    worldPos.xyz += separationDir * separationAmount;
    
    // Agregar expansión radial desde el centro
    worldPos.xyz += normalizedPos * 0.3;
    
    fragPosition = worldPos;
    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize(mat3(modelMatrix) * inNormals);
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
    // Transformar primero al espacio del mundo
    vec4 worldPos = modelMatrix * vec4(inPosition, 1.0);
    vec3 pos = worldPos.xyz;
    vec3 worldNormal = normalize(mat3(modelMatrix) * inNormals);
    
    // Ondas basadas en la posición del mundo (escala independiente)
    float wave1 = sin(pos.x * 0.5 + time * 2.0) * 0.15;
    float wave2 = cos(pos.y * 0.5 + time * 1.5) * 0.12;
    float wave3 = sin(pos.z * 0.5 + time * 2.5) * 0.1;
    
    float wobble = sin(pos.x * 0.3 + time) * cos(pos.y * 0.3 + time * 0.8) * 0.2;
    
    vec3 slimePos = pos + worldNormal * (wave1 + wave2 + wave3 + wobble);
    
    // Goteo basado en la posición del mundo
    float dripFactor = sin(pos.x * 1.0 + time * 3.0) * cos(pos.z * 1.0 + time * 2.0);
    dripFactor = max(0.0, dripFactor);
    slimePos.y -= dripFactor * 0.3;
    
    // Pulso general
    float pulse = sin(time * 1.5) * 0.08;
    slimePos += worldNormal * pulse;
    
    fragPosition = vec4(slimePos, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = worldNormal;
    fragTexCoords = inTexCoords;
}

'''