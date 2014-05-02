//Math functions
float4 mult_matrix(float16 *m, float4 v) {
    float x = m->s0*v.x + m->s1*v.y + m->s2*v.z + m->s3*v.w;
    float y = m->s4*v.x + m->s5*v.y + m->s6*v.z + m->s7*v.w;
    float z = m->s8*v.x + m->s9*v.y + m->sa*v.z + m->sb*v.w;
    float w = m->sc*v.x + m->sd*v.y + m->se*v.z + m->sf*v.w;
    return (float4)(x, y, z, w);
}

//Round a float by decimal values
float round_float(float value, uint decimals) {
    float power = pow(10.0, decimals);
    float powval = value*power;
    if (powval - (int)powval > 0.5) {
        return ((int)powval + 1)/power;
    }
    else {
        return (int)powval/power;
    }
}
