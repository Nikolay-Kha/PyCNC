G17
G0 X90 Y90
G1 Z10
f1800
G2 X110 Y110 I10 J10 ; half circle
G3 X110 Y110 I-5 J-5 ; full circle in one move
G2 X90 Y90 I-10 J-10 ; second half of circle
G2 X90 Y70 I-10 J-10 ; quarter of circle
G2 X90 Y90 I-10 J10 ; three quoter circle
G3 X90 Y90 Z 20 I-10 J-10 F1000 ; spiral
f1800
G2 X92.07 Y85 I-5 J-5 ; small arc
G2 X90 Y90 I-7.07 J0; more then 270 degree arc
G18
G2 X90 Y90 K-5 F120
G19
G2 X90 Y90 K-5 F120
