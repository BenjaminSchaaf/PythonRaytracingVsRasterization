#include <Math.cl>

//A vertex is made up of a position, a normal and a UV coordinate
typedef struct {
    float4 position;
//    float4 normal;
//    float2 uv;
} Vertex;

//A camera is made up of it's position and it's orientation
typedef struct {
    float4 position;
    float4 forward;
    float4 up;
    float4 right;
} Camera;

//A Ray-Hit point is made up of it's intersection point and information about it.
typedef struct {
    float4 point;
    float4 normal;
    float4 bary;
    float dist;
} Hit;

//A ray is simply a point and a direction
typedef struct {
    float4 origin;
    float4 direction;
} Ray;

float distance_from_ray_to_plane(Ray* ray, float4 A, float4 B, float4 C, Hit *hit);
bool ray_triangle_check(Ray* ray, float4 A, float4 B, float4 C, float dist, Hit* hit);

bool raycast(Ray* ray, __constant Vertex *vertices, int vertices_len, Hit *hit) {
    hit->dist = INFINITY;

    //Iterate through triangles
    for (int index = 0; index < vertices_len; index += 3) {
        //Get vertex coordiates of every triangle
        float4 A = vertices[index + 0].position; //mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3], 0)).xyz;
        float4 B = vertices[index + 1].position; //mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3 + 1], 0)).xyz;
        float4 C = vertices[index + 2].position; //mult_matrix(&object->matrix, (float4)(*mesh->vertices[tris*3 + 2], 0)).xyz;

        //Get the hitdistace from the plane A, B, C
        float dist = distance_from_ray_to_plane(ray, A, B, C, hit);

        if (dist == INFINITY) {
          continue;
        }

        if(dist < hit->dist) {
            if (ray_triangle_check(ray, A, B, C, dist, hit)) {
                hit->dist = dist;
            }
        }
    }

    //Return whether or not the ray hit anything
    if (hit->dist == INFINITY) {
        return false;
    }

    return true;
}

float distance_from_ray_to_plane(Ray* ray, float4 A, float4 B, float4 C, Hit *hit) {
    hit->normal = cross(C - A, B - A);
    float dotDirection = dot(hit->normal, ray->direction);

    if (dotDirection == 0) {
        return INFINITY;
    }

    float dist = dot(A - ray->origin, hit->normal) / dotDirection;

    return dist;
}

//Check whether an intersection point is inside the triangle A, B, C
//Intersection point is dist along the ray.
bool ray_triangle_check(Ray* ray, float4 A, float4 B, float4 C, float dist, Hit* hit) {
    hit->point = ray->origin + ray->direction * dist;

    float area = length(hit->normal);

    //Optimisation
    float4 QA = A - hit->point;
    float4 QB = B - hit->point;
    float4 QC = C - hit->point;

    //Barycentric intersection test
    hit->bary.x = length(cross(QB, QC))/area;
    hit->bary.y = length(cross(QA, QC))/area;
    hit->bary.z = length(cross(QA, QB))/area;

    //6 decimal precision. Not very good, but good enough
    hit->bary.w = hit->bary.x + hit->bary.y + hit->bary.z;

    //Check for bary intersection
    float diff = fabs(1.0 - hit->bary.w);
    if (diff < 0.000001) {
        return true;
    }

    return false;
}



__kernel void raytrace(__write_only image2d_t renderTexture, Camera camera, __constant Vertex *vertices, int vertices_len, __global float *res_g) {

    int x = get_global_id(0);
    int y = get_global_id(1);
    int2 position = (int2)(x, y);

    float width  = get_global_size(0);
    float height = get_global_size(1);
    //uv coordinates

    float normalised_x = x/width - 0.5;
    float normalised_y = y/height - 0.5;

    float2 normalised_pos = (float2)(normalised_x, normalised_y);

    Ray ray;
    ray.origin = camera.position;
    ray.direction = camera.forward + normalised_y*camera.up + normalised_x*camera.right;

    float4 black = (float4)(0.0, 0.0, 0.0, 1.0);
    float4 white = (float4)(1.0, 1.0, 1.0, 1.0);
    float4 red   = (float4)(1.0, 0, 0, 0);

    float4 color = black;

    Hit hit;

    //Do raytracing
    if (raycast(&ray, vertices, vertices_len, &hit)) {
        color = white;
        res_g[x+y*(int)width] = 1;
    }
    else {
        res_g[x+y*(int)width] = 0;
    }

    if (normalised_x == 0 || normalised_y == 0) {
        color = red;
    }

    //color = (ray.direction + (float4)(1.0, 1.0, 1.0, 1.0))/2;

    write_imagef(renderTexture, position, color);
}
