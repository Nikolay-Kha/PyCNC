%
g28
n1 g1x0y0z0
n1 g1 x1 y1 z1 ; check if comments is ok
g1(check if inline comments work)x2y2(two times)z2
(or on separated line)
; or like this
m3s04000
g4 p0.5
m5
f500
g91
g20
g0x1
g0x1
g0x1
g0x-1
g0x-1
g0x-1
g21
g1y1
g1y-1
g90
g92x100y100z100f240
m111
g1x98y98z98f120
(head should be in zero position)
m2
