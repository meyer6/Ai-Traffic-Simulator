import math

# Gets an approximation for the circumference of 1/4 of an ellipse
def getCircumference(a, b):
    return 2 * 3.14 * (sum(t**1.5 for t in (a, b))/2)**(1/1.5) // 4 - 1
    
def pythag(a, b):
    return (a**2 + b**2) ** (1/2)

# Decorator to return function to give coordinates and angle of car given how far along the section it is
def getHorizontalData(y, x1, x2):
    def innerFunc(i):
        return x1 + (x2 - x1) // abs(x2 - x1) * i, y, 0
    return abs(x2-x1), innerFunc

# Decorator to return function to give coordinates and angle of car given how far along the section it is
def getVerticalData(x, y1, y2):
    def innerFunc(i):
        return x, y1 + (y2 - y1) // abs(y2 - y1) * i, 90
    return abs(y2-y1), innerFunc

# Function to give coordinates and angle of car given how far along the section it is
def getLength(a, b, startx, endx, i):
    sum = 0
    direction = (endx - startx) // abs(endx - startx)
    dx = startx
    y = ((1 - dx**2/a**2)*b**2)**(1/2)
    c = 0
    while sum < i*1.1:
        c += 1
        oldy = y
        dx += 0.05 * direction
        y = ((1 - dx**2/a**2)*b**2)**(1/2)
        sum += pythag(0.05, y - oldy)
    return dx - startx

# Decorator to return function to give coordinates and angle of car given how far along the section it is
def getEllipseData(startx, starty, endx, endy, qx, qy):
    if qx == 1: midx = min(endx, startx)
    else:       midx = max(endx, startx)
    
    if qy == 1: midy = min(endy, starty)
    else:       midy = max(endy, starty)

    a = abs(endx - startx)
    b = abs(endy - starty)

    startx -= midx
    endx -= midx

    circ = getCircumference(a, b) * 0.91
    iLookUp = []
    for i in range(1, int(circ)+1):
        dx = getLength(a, b, startx, endx, i)

        x = startx + dx
        y = ((1 - x**2/a**2)*b**2)**(1/2) * qy

        m = (-b**2*x)/(a**2*y)
        t = -math.atan(m)/3.14*180

        iLookUp.append([i, x + midx, y + midy, t])

    def innerfunc(i):
        return iLookUp[i - 1][1], iLookUp[i - 1][2], iLookUp[i - 1][3]

    return int(circ), innerfunc
