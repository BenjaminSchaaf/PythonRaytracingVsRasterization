#include <Math.cl>
/*
//Find the intersection distance between a ray and a plane
//made from three poits


//check the intersection between a ray and a triangle
//place output data into the hit pointer


RaycastHit* raycast(Ray* ray, int object_count, Object* objects[MAX_OBJECT_COUNT]) {
    RaycastHit* hit = 0;
    float dist = INFINITY;

    for (int index = 0; index < object_count; index++) {
        Mesh* mesh = objects[index]->mesh;
        Object* object = objects[index];

        for (int tris = 0; tris < mesh->triangle_count; tris++) {
            float3 A = mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3], 0)).xyz;
            float3 B = mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3 + 1], 0)).xyz;
            float3 C = mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3 + 2], 0)).xyz;

            float hitdist = ray_plane(ray, A, B, C);
            if (hitdist < dist) {
                RaycastHit hit2;
                if (ray_triangle_check(ray, A, B, C, hitdist, &hit2)) {
                    hit2.triangle_index = tris;
                    hit2.object = objects[index];
                    hit = &hit2;
                }
            }
        }
    }

    return hit;
}

bool in_triangle(float3 point, float3 A, float3 B, float3 C) {
    float area = magnitude(cross(B - A, C - A));

    float3 QA = A - point;
    float3 QB = B - point;
    float3 QC = C - point;
    float value = (magnitude(cross(QB, QC)) +
                   magnitude(cross(QA, QC)) +
                   magnitude(cross(QA, QB)))/area;
    return round_float(value, 6) == 1;
}

void trace(__write_only image2d_t renderTexture,
           int2 pos, float16 *projection_matrix,
           int object_count, Object* objects[MAX_OBJECT_COUNT]) {
    Ray ray;
    ray.origin = mult_matrix(projection_matrix, (float4)(0, 0, 0, 1)).xyz;
    ray.direction = mult_matrix(projection_matrix, (float4)((float)pos.x, (float)pos.y, 1, 0)).xyz;

    RaycastHit* hit = raycast(&ray, object_count, objects);

    if (hit) {
        write_imagef(renderTexture, pos, (float4)(1, 0, 0, 1));
    }
    else {
        write_imagef(renderTexture, pos, (float4)(0, 1, 0, 1));
    }


    if (hit) {
        int iteration = 0;
        float4 endColor = (float4)(0, 0, 0, 1);
        float strength = 1;

        while (hit && iteration < 4) {
            float4 color;
            //ambient
            color = hit->object->material->emission + hit->object->material->ambient;

            //lighting
            float4 light = light_trace(hit->point + (float)0.00001*hit->normal, lights);
            color += hit->object->material->diffuse;////////// *light;

            endColor += color*strength;
            if (false) { //reflection
                hit = raycast(&ray, objects);
            }
            else {
                break;
            }
            iteration += 1;
        }
        write_imagef(renderTexture, pos, endColor);
    }*/
//}

typedef struct {
    float4 position;
    float4 normal;
    float2 uv;
} Vertex;

typedef struct {
    float4 position;
    float4 forward;
    float4 up;
    float4 right;
} Camera;

typedef struct {
    float4 point;
    float4 normal;
    float4 bary;
    float dist;
} Hit;

typedef struct {
    float4 origin;
    float4 direction;
} Ray;

float ray_plane(Ray* ray, float4 A, float4 B, float4 C, Hit *hit) {
    hit->normal = -cross(C - A, B - A);
    float dotDirection = dot(hit->normal, ray->direction);
    return -dot(ray->origin, hit->normal + A) / dotDirection;

    if (dotDirection > 0) {
        return -dot(ray->origin, hit->normal + A) / dotDirection;
    }
    else {
        return INFINITY;
    }
}

void ray_triangle_check(Ray* ray, float4 A, float4 B, float4 C, float dist, Hit* hit) {
    hit->point = ray->origin + ray->direction*dist;
    float area = length(hit->normal);

    float4 QA = A - hit->point;
    float4 QB = B - hit->point;
    float4 QC = C - hit->point;
    hit->bary.x = length(cross(QB, QC))/area;
    hit->bary.y = length(cross(QA, QC))/area;
    hit->bary.z = length(cross(QA, QB))/area;
    hit->bary.w = round_float(hit->bary.x + hit->bary.y + hit->bary.z, 6);
    hit->dist = dist;
    if (hit->bary.w == 1.0) {
        hit->dist = dist;
    }
}

bool raycast(Ray* ray, __constant Vertex *vertices, int vertices_len, Hit *hit) {
    hit->dist = INFINITY;

    for (int index = 0; index < vertices_len; index += 3) {
        float4 A = vertices[index + 0].position;//mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3], 0)).xyz;
        float4 B = vertices[index + 1].position;//mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3 + 1], 0)).xyz;
        float4 C = vertices[index + 2].position;//mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3 + 2], 0)).xyz;

        float hitdist = ray_plane(ray, A, B, C, hit);

        if (hitdist < hit->dist) {
            ray_triangle_check(ray, A, B, C, hitdist, hit);
        }
    }

    if (hit->dist < INFINITY) {
        return true;
    }
    return false;
}

__kernel void raytrace(__write_only image2d_t renderTexture,
                       Camera camera,
                       __constant Vertex *vertices, int vertices_len) {
    //texture position
    int2 pos = (int2)(get_global_id(0), get_global_id(1));
    //texture size
    float2 size = (float2)(get_global_size(0), get_global_size(1));
    //uv coordinates
    float2 npos = (float2)(pos.x/size.x - 0.5, pos.y/size.y - 0.5);

    Ray ray;
    ray.origin = camera.position;
    ray.direction = camera.forward + npos.y*camera.up + npos.x*camera.right;

    float4 color = (float4)(0.0, 0.0, 0.0, 1.0);

    Hit hit;

    if (raycast(&ray, vertices, vertices_len, &hit)) {
        color = (float4)(1.0, 1.0, 1.0, 1.0);
    }

    //color = (ray.direction + (float4)(1.0, 1.0, 1.0, 1.0))/2;

    write_imagef(renderTexture, pos, color);
}
