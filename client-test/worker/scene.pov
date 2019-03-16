// this file is generated
// from pypovlib V0.1.11 written by Oliver Cordes (C) 2015-2019

// PovPreFile scene_pre.pov
#version 3.7;

global_settings {  assumed_gamma 1.0 }

#include "colors.inc"
#include "stones.inc"
#include "woods.inc"
#include "textures.inc"
#include "metals.inc"
#include "holodeck.inc"

light_source {
        < 0.0, 150, -30>
        rgb <1.000000, 1.00000, 1.000000> * 3.0
}

light_source {
        <2, 10, -10>
        rgb <1.000000, 1.00000, 1.000000> * 3.
}



plane{ <0,1,0>,  0
        Holo_texture_y_color( 3.0, rgb<0.05,0.05,0.05> )
        //texture{ pigment { color rgb <0.0,0.0,0.0> } }
}

plane{ <1,0,0>, -20
  Holo_texture_x( 3.0 )
}

plane{ <0,0,1>, 10
        Holo_texture_z( 3.0 )
}

camera{
    perspective
    location <5.000000,3.000000,-20.000000>
    look_at <0.000000,1.000000,0.000000>
    sky <0.000000,1.000000,0.000000>
    angle 67.380000
    right x * image_width/image_height
}

box{
    <0.000000,0.000000,0.000000> <1.000000,1.000000,1.000000>
    texture{
        pigment{ rgb <1,0,0>}
    }
    scale <3.000000,3.000000,3.000000>
}



// end of generated file
