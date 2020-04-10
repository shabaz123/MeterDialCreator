# meter dial creator

import math
import svgwrite

############### settings #########################

mechangle=(80/360)*2*math.pi # meter movement has 80 degree total span

arc_color=svgwrite.rgb(10, 10, 16, '%')
arc_width=1.5
tick_color=svgwrite.rgb(10, 10, 16, '%')
tick_width_L=2.0
tick_width_M=1.5
tick_width_log_M=1.0
tick_width_S=1.0

# docu is for cutout markings etc, doesn't need to be changed
docu_color=svgwrite.rgb(10, 10, 16, '%')
docu_width=0.5

# a constant for approximate sizing
szfactor=5.64

################# functions ########################

# convert polar to cartesian
# h is the height at which the point is required
# ang_n is between 0 (min deflection) and 1 (max deflection)
def toxy(h, ang_n):
    a=(ang_n*mechangle) - (mechangle/2)
    y=0-math.cos(a)*h
    x=math.sin(a)*h
    return x, y

# draw a full arc at height h, with p points
def full_arc(h, p):
    plist=[]
    for i in range (0, p):
        x,y = toxy(h, (i/(p-1)))
        plist.append([x,y])
    dwg.add(
        dwg.polyline(
            points=plist,
            stroke=arc_color,
            stroke_opacity=1.0,
            fill="none",
            stroke_width=arc_width,
            stroke_linejoin="round",
            stroke_linecap="round"
        )
    )

# draw a partial arc at height h, with p points
# t = total segments, n = segment to draw from 0 to t-1
def part_arc(h, p, n, t):
    plist=[]
    for i in range (0, p):
        x,y = toxy(h, (n/t) + (i/(t*(p-1))))
        plist.append([x,y])
    dwg.add(
        dwg.polyline(
            points=plist,
            stroke=arc_color,
            stroke_opacity=1.0,
            fill="none",
            stroke_width=arc_width,
            stroke_linejoin="round",
            stroke_linecap="round"
        )
    )

# draw a sector at height h to h+l, with p points
# t = total segments, n = segment to draw from 0 to t-1
def sector(h, p, l, n, t):
    plist=[]
    for i in range (0, p): # draw bottom arc
        x,y = toxy(h, (n/t) + (i/(t*(p-1))))
        plist.append([x,y])
    x,y = toxy(h+l, (n/t) + ((p-1)/(t*(p-1)))) # right side
    plist.append([x,y])
    for i in range (0, p): # draw top arc
        x,y = toxy(h+l, (n/t) + (((p-1)-i)/(t*(p-1))))
        plist.append([x,y])
    x,y = toxy(h, (n/t)) # left side
    plist.append([x,y])

    dwg.add(
        dwg.polygon(
            points=plist,
            stroke=arc_color,
            stroke_opacity=1.0,
            fill="none",
            stroke_width=arc_width,
            stroke_linejoin="round",
            stroke_linecap="round"
        )
    )


# draw major, semi and minor ticks
# h is the height of the base of the ticks
# len_L, len_M, len_S is the length of the major, semi and minor ticks
# (Large, Medium, Small)
def full_ticks(h, p, len_L, len_M, len_S, interval_L, interval_M):
    count_M=0
    count_L=0
    for i in range (0, p):
        x,y = toxy(h, (i/(p-1)))
        if i%interval_L==0:
            x1,y1=toxy(h+len_L, (i/(p-1)))
            width=tick_width_L
        elif  i%interval_M==0:
            x1,y1=toxy(h+len_M, (i/(p-1)))
            width=tick_width_M
        else:
            x1,y1=toxy(h+len_S, (i/(p-1)))
            width=tick_width_S

        dwg.add(
            dwg.line(
                (x,y), (x1,y1), 
                stroke=tick_color,
                stroke_width=width,
                stroke_linejoin="round",
                stroke_linecap="round"
            )
        )

# draw major, semi and minor ticks
# h is the height of the base of the ticks
# d is number of decades
# len_L, len_M, len_S is the length of the major, medium and minor ticks
# (Large, Medium, Small)
def log_full_ticks(h, d, len_L, len_M, len_S):
    count_M=0
    count_L=0
    p=10*d
    dsel=0
    inc=1
    for i in range (0, p):
        ang_n=(dsel/d) + (math.log10(inc)*(1/d)) 
        x,y = toxy(h, ang_n)
        if (i%10==0) or (i==p-1):
            x1,y1=toxy(h+len_L, ang_n)
            width=tick_width_L
        elif (i%5==0):
            x1,y1=toxy(h+len_M, ang_n)
            width=tick_width_log_M
        else:
            x1,y1=toxy(h+len_S, ang_n)
            width=tick_width_S
        inc=inc+1
        if (inc>10):
            inc=1
            dsel=dsel+1

        dwg.add(
            dwg.line(
                (x,y), (x1,y1), 
                stroke=tick_color,
                stroke_width=width,
                stroke_linejoin="round",
                stroke_linecap="round"
            )
        )


# text labels at height h, total of p points.
def full_label(h, p):
    for i in range (0, p):
        rotate=[]
        a=((i/(p-1))*mechangle) - (mechangle/2)
        a=a*360/(2*math.pi)
        rotate.append(a)
        x,y = toxy(h, (i/(p-1)))
        dwg.add(dwg.text(
            "x", insert=(x, y), fill='red', rotate=rotate)
        )

################# create output file #######################

dwg = svgwrite.Drawing('out.svg', profile='tiny')
# add crosshair at meter spindle
dwg.add(dwg.line((-1, 0), (1, 0), stroke=docu_color, stroke_width=docu_width))
dwg.add(dwg.line((0, -1), (0, 1), stroke=docu_color, stroke_width=docu_width))


################ main code #################################

# Temperature indication:
# Traditional meter style, with major, minor and small ticks
# temperature will be from 15-30 degrees C, which is a range of 15 deg C
# have a total of 31 ticks (i.e. per half degree)
# every 10 ticks (5 deg C) for large markings
# every 2 ticks (1 deg C) for medium markings
h=265 # 265 / 5.64 = 47mm 
full_arc(h, 31)
full_ticks(h, 31, 10, 5, 4, 10, 2)
full_label(h+12, 16)
# partial arcs, ideal for adornment on a meter dial, etc
#for i in range (0,15):
#    if ((i+15)>=18) and ((i+15)<24):
#        part_arc(h+5, 10, i, 15)
# sector for shading in green:
sectors=15
for i in range (0,sectors):
    if ((i+15)>=18) and ((i+15)<24):
        sector(h, 10, 6, i, sectors)

# Humidity indication:
# sector style. 20-90 percent RH, this is a total of 7 sectors
h=225
sectors=7
for i in range (0,sectors):
    sector(h, 10, 6, i, sectors)
full_label(h+12, 8)
# half-sectors for shading in green:
sectors=14
sector(h, 10, 6, 5, sectors)
sector(h, 10, 6, 8, sectors)

# VOC indication:
# traditional meter style, but with log ticks
# need 5 decades
h=185
full_arc(h, 51)
log_full_ticks(h, 5, 10, 4, 4)
full_label(h+12, 6)
# no safe definition for general VOC, but a sector will be shown for less than 27 ppb (formaldehyde):
sectors=3.5
sector(h, 10, 6, 0, sectors)

# Co2 indication:
# traditional meter style, but with log ticks
# need 3 decades
h=145
full_arc(h, 61)
log_full_ticks(h, 3, 10, 4, 4)
full_label(h+12, 4)
# 250-1000ppm is good. The settings below will draw a sector for 300-1000ppm which is good enough
sectors=6
sector(h, 10, 6, 1, sectors)

# save the drawing!
dwg.save()
print("done!")

