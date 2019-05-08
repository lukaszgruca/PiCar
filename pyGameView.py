#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import math
import random

REWARD_RADIUS = 20
CAR_SPEED = 10
CAR_TURN = 30

def normalize(x, xmin, xmax):
    return ((x-xmin)/(xmax-xmin))

class pyGame(object):
    def __init__(self, width=1280, height=1024, fps=60, caption="PyGame", verbose = True, carX = 640, carY = 512, parkX = 640, parkY = 512):
        self.width = width
        self.height = height
        self.verbose = verbose

        #clock
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0

        self.car = Car(carX,carY,0)
        self.env = Environment(parkX,parkY,0)

        #screen init
        if self.verbose:
            pygame.init()
            pygame.display.set_caption(caption)
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
            #frame init
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill((0,0,0)) # fill background black
            #font
            self.font = pygame.font.SysFont('mono', 14, bold=True)

    def reset(self, rX = False, rY = False, rD = False):
        self.car.reset(rX, rY, rD)
        self.env.reset(rX, rY, rD)
        return self.state()

    def state(self):
        return [normalize(self.car.rearAxis.x,0,self.width), normalize(self.car.rearAxis.y,0,self.height), \
              normalize(self.car.frontAxis.x,0,self.width), normalize(self.car.frontAxis.y,0,self.height), \
              normalize(self.env.parkEnd.x,0,self.width),  normalize(self.env.parkEnd.y,0,self.height), \
              normalize(self.env.parkFront.x,0,self.width), normalize(self.env.parkFront.y,0,self.height)]

    def draw(self):
        # draw functions here
        self.background.fill((0,0,0))
        self.background = self.background.convert()

    def flip(self):
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

    def __del__(self):
        #desctructor
        pygame.quit()
        print("Total play time {:.2f} seconds".format(self.playtime))

    def draw_text(self, text, x, y ):
        """Center text in window
        """
        surface = self.font.render(text, True, (0, 255, 0))
        # // makes integer division in python3
        self.background.blit(surface, (x, y))

    def reward(self):
        if math.fabs(self.car.rearAxis.x - self.env.parkEnd.x) < REWARD_RADIUS and math.fabs(self.car.rearAxis.y - self.env.parkEnd.y) < REWARD_RADIUS and \
           math.fabs(self.car.frontAxis.x - self.env.parkFront.x) < REWARD_RADIUS and math.fabs(self.car.frontAxis.y - self.env.parkFront.y < REWARD_RADIUS):
           if self.car.speed == 0:
               return 5000
           else:
                return 1000
        else:
           if self.car.speed == 0:
               return int( - (math.pow(self.car.rearAxis.x - self.env.parkEnd.x,2) + math.pow(self.car.rearAxis.y - self.env.parkEnd.y,2))/2000-100)
           else:
               return int( - (math.pow(self.car.rearAxis.x - self.env.parkEnd.x,2) + math.pow(self.car.rearAxis.y - self.env.parkEnd.y,2))/2000)

    def done(self):
        if (self.car.rearAxis.x>self.width) or (self.car.rearAxis.x<0) or \
        (self.car.rearAxis.y >self.height) or (self.car.rearAxis.y<0):
            return True
        #elif math.fabs(self.car.rearAxis.x - self.env.parkEnd.x) < REWARD_RADIUS and math.fabs(self.car.rearAxis.y - self.env.parkEnd.y) < REWARD_RADIUS and \
        #   math.fabs(self.car.frontAxis.x - self.env.parkFront.x) < REWARD_RADIUS and math.fabs(self.car.frontAxis.y - self.env.parkFront.y < REWARD_RADIUS):
        #    return True
        else:
            return False

    def step(self, action):
        #self.milliseconds = self.clock.tick(self.fps)  # milliseconds passed since last frame
        #self.seconds = self.milliseconds / 1000.0
        #self.playtime += self.seconds
        self.car.act(action)

        # all movement here
        #self.car.move(self.seconds, self.width, self.height)
        self.car.move()

        if self.verbose:
            # all render here
            self.draw()
            self.car.draw(self.background)
            self.env.draw(self.background)
            #self.draw_text("FPS {:.1f}".format(self.clock.get_fps()), 10, 10)
            self.draw_text("Action: {} speed: {} turn: {} Reward {}".format(action,self.car.speed,self.car.turnAngle, self.reward()),10, 10)
            self.flip()

        return self.state(), self.reward(), self.done(), 0

    def run(self):
        mainloop = True

        while mainloop:
            # count time
            self.milliseconds = self.clock.tick(self.fps)  # milliseconds passed since last frame
            self.seconds = self.milliseconds / 1000.0
            self.playtime += self.seconds

            # check for events
            self.car.speed = 0
            self.car.turnAngle = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False # pygame window closed by user
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False # user pressed ESC
                    if event.key == pygame.K_r:
                        self.env.renewPark()

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_w]:
                self.car.speed = CAR_SPEED
            if pressed[pygame.K_s]:
                self.car.speed = -CAR_SPEED
            if pressed[pygame.K_a]:
                self.car.turnAngle = -CAR_TURN
            if pressed[pygame.K_d]:
                self.car.turnAngle = CAR_TURN

            # all movement here
            #self.car.move(self.seconds, self.width, self.height)
            self.car.move(1)

            # all render here
            self.draw()
            self.car.draw(self.background)
            self.env.draw(self.background)
            self.draw_text("speed: {} turn: {} Reward {}".format(self.car.speed,self.car.turnAngle, self.reward()),10, 10)
            self.flip()

class Point(object):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def xy(self):
        return self.x, self.y

    def xyI(self):
        return int(self.x), int(self.y)

    def rotate(self, px = 0, py = 0, angle = 0):
        self.x = px + self.x  * math.cos(math.radians(angle)) - self.y  * math.sin(math.radians(angle))
        self.y = py + self.x  * math.sin(math.radians(angle)) + self.y  * math.cos(math.radians(angle))

    def translate(self, lenght, angle, p = 0):
        if p == 0:
            self.x += lenght * math.cos(math.radians(angle))
            self.y += lenght * math.sin(math.radians(angle))
        else:
            self.x = p.x + lenght * math.cos(math.radians(angle))
            self.y = p.y + lenght * math.sin(math.radians(angle))

    def random(self, xmin, xmax, ymin, ymax):
        self.x = random.randrange(xmin, xmax)
        self.y = random.randrange(ymin, ymax)

    def copy(self, p):
        self.x = p.x
        self.y = p.y

class graphicCalculations():
    def findLocation(self,centerPointX, centerPointY, deltaX,deltaY, angle):
        # find location from center of object and apply rotation by given angle
        centerPoint = Point(centerPointX, centerPointY)
        delta = Point(deltaX, deltaY)
        return self.findLocation(centerPoint, delta, angle)

    def findLocation(self,centerPoint, delta, angle):
        # find location from center of object and apply rotation by given angle
        out = Point()
        out.x = int(centerPoint.x + delta.x  * math.cos(math.radians(angle)) - delta.y  * math.sin(math.radians(angle)))
        out.y = int(centerPoint.y + delta.x  * math.sin(math.radians(angle)) + delta.y  * math.cos(math.radians(angle)))
        return out



class Environment(object):
    def __init__(self, parkEndStartX = 400, parkEndStartY = 240, directionStart = 0 ):
        self.parkEndStart = Point()
        self.parkEndStart.x = parkEndStartX
        self.parkEndStart.y = parkEndStartY
        self.random = random
        self.parkEnd = Point()
        self.parkFront = Point()
        self.parkLenght = 50
        self.directionStart = 0
        self.direction = 30
        self.points = 0
        self.reset()

    def draw(self,surface):
        # center of the parking space
        pygame.draw.line(surface, (150,150,150), self.parkEnd.xy(), self.parkFront.xy())

        # circle to aroung front and back point
        pygame.draw.circle(surface, (100,100,100), self.parkEnd.xyI(),2,1)
        #pygame.draw.circle(surface, (100,0,100), self.parkFront.xyI(),30,1)

        # outlines of the parking space
        rl = graphicCalculations().findLocation(self.parkEnd,  Point(-20,-20),self.direction)
        rr = graphicCalculations().findLocation(self.parkEnd,  Point(-20, 20),self.direction)
        fr = graphicCalculations().findLocation(self.parkFront,Point( 20, 20),self.direction)
        fl = graphicCalculations().findLocation(self.parkFront,Point( 20,-20),self.direction)

        pygame.draw.polygon(surface, (150,150,150), (rl.xyI(),rr.xyI(),fr.xyI(),fl.xyI()), 1)

    def reset(self, rX = False, rY = False, rD = False):
        if rX:
            self.parkEnd.x = random.randrange(200,1000) #self.parkEndStart.x
        else:
            self.parkEnd.x = self.parkEndStart.x
        if rY:
            self.parkEnd.y = random.randrange(200,800) #self.parkEndStart.y
        else:
            self.parkEnd.y = self.parkEndStart.y
        if rD:
            self.direction = random.randrange(0,360) #self.directionStart
        else:
            self.direction = self.directionStart

        self.parkFront.translate(self.parkLenght, self.direction, self.parkEnd)

    def renewPark(self):
        self.parkEnd.random(100,540,100,220)
        self.direction = random.randrange(0,360)
        self.parkFront.translate(self.parkLenght, self.direction, self.parkEnd)



class Car(object):
    def __init__(self,startX = 100, startY = 140, directionStart = 0):
        self.rearAxisStart = Point()
        self.rearAxisStart.x = startX
        self.rearAxisStart.y = startY
        self.directionStart = directionStart
        self.direction = self.directionStart
        self.random = random
        self.carLenght = 50
        self.carWidth = 30
        self.wheelSize = 16
        self.rearAxis = Point()
        self.direction = 0 # angle of the car 0-360
        self.color = (255,0,0)
        self.turnAngle = 0 # turning angle 0-360
        self.speed = 0

        # point to turn around
        self.turnPoint = Point()
        self.frontAxis = Point()
        self.reset()
        #action 0 - stop, 1-forward, 2-backward, 3 forward + right, 4 forward + left, 5 - backward + rigth, 6 backward + left
        self.actSpeed = {
            0: 0,
            1: CAR_SPEED,
            2: -CAR_SPEED,
            3: CAR_SPEED,
            4: CAR_SPEED,
            5: -CAR_SPEED,
            6: -CAR_SPEED
        }
        self.actTurn = {
            0: 0,
            1: 0,
            2: 0,
            3: CAR_TURN,
            4: -CAR_TURN,
            5: CAR_TURN,
            6: -CAR_TURN
        }

    def act(self, action):
        self.speed = self.actSpeed[action]
        self.turnAngle = self.actTurn[action]
        #print("Action: ",action, "\tSpeed: ", self.speed, "\tTurn: ", self.turnAngle)

    def reset(self, rX = False, rY = False, rD = False):
        if rX:
            self.rearAxis.x = random.randrange(200,1000) #self.rearAxisStart.x
        else:
            self.rearAxis.x = self.rearAxisStart.x

        if rY:
            self.rearAxis.y = random.randrange(200,800) #self.rearAxisStart.y
        else:
            self.rearAxis.y = self.rearAxisStart.y

        if rD:
            self.direction = random.randrange(0,360) #self.directionStart
        else:
            self.direction = self.directionStart

        #update front axis
        self.frontAxis.translate(self.carLenght, self.direction, self.rearAxis)

    def move(self):

        #update front axis
        self.frontAxis.translate(self.carLenght, self.direction, self.rearAxis)

        if self.turnAngle != 0:
            turnRadius = self.carLenght / math.sin(math.radians(self.turnAngle))
            angleSpeed = ( self.speed / turnRadius )

            # calculate turn point
            self.turnPoint.x = self.frontAxis.x + self.carLenght * math.sin(math.radians(-self.direction-self.turnAngle)) / math.sin(math.radians(self.turnAngle))
            self.turnPoint.y = self.frontAxis.y + self.carLenght * math.cos(math.radians(-self.direction-self.turnAngle)) / math.sin(math.radians(self.turnAngle))

            # update direction
            self.direction += math.degrees(angleSpeed)
            if self.direction >= 360:
                self.direction -= 360
            if self.direction <=0:
                self.direction += 360;

            # rotate rear axis
            #self.rearAxis.rotate(self.turnPoint.x, self.turnPoint.y, self.angleSpeed)
            self.rearAxis.x = ((self.rearAxis.x - self.turnPoint.x) * math.cos(angleSpeed) - (self.rearAxis.y - self.turnPoint.y) * math.sin(angleSpeed) + self.turnPoint.x)
            self.rearAxis.y = ((self.rearAxis.x - self.turnPoint.x) * math.sin(angleSpeed) + (self.rearAxis.y - self.turnPoint.y) * math.cos(angleSpeed) + self.turnPoint.y)
        else:
            self.rearAxis.x += self.speed * math.cos(math.radians(self.direction))
            self.rearAxis.y += self.speed * math.sin(math.radians(self.direction))
            self.turnPoint.x = 0
            self.turnPoint.y = 0

    def findLocation(self,dx,dy):
        # find location from rearAxis centre, after appling direction
        outcome = Point()
        outcome.x = int(self.rearAxis.x + dx  * math.cos(math.radians(self.direction)) - dy  * math.sin(math.radians(self.direction)))
        outcome.y = int(self.rearAxis.y + dx  * math.sin(math.radians(self.direction)) + dy  * math.cos(math.radians(self.direction)))
        return outcome

    def drawLine(self,surface, x1,y1,x2,y2): # fro drawing a car (before rotation)
        pygame.draw.line(surface, self.color, self.findLocation(x1,y1).xy(),self.findLocation(x2,y2).xy())


    def draw(self, surface):
        #pygame.draw.circle(surface,(0,70,0), (150,100), 20)
        # draw main line
        self.drawLine(surface, 0, 0, self.carLenght, 0)

        #draw Axis
        self.drawLine(surface, 0, -self.carWidth/2, 0, self.carWidth/2)
        self.drawLine(surface, self.carLenght,  -self.carWidth/2, self.carLenght,  self.carWidth/2)

        #draw wheels
        #back
        self.drawLine(surface, -self.wheelSize/2, -self.carWidth/2, self.wheelSize/2, -self.carWidth/2)
        self.drawLine(surface, -self.wheelSize/2,  self.carWidth/2, self.wheelSize/2,  self.carWidth/2)
        #front
        #fl = Point(0,0)
        fl1 = Point( self.wheelSize/2,0)
        fl2 = Point(-self.wheelSize/2,0)
        fl1.rotate(0,0, self.turnAngle)
        fl2.rotate(0,0, self.turnAngle)
        self.drawLine(surface, self.carLenght + fl1.x, -self.carWidth/2 + fl1.y, self.carLenght+fl2.x, -self.carWidth/2 + fl2.y)
        self.drawLine(surface, self.carLenght + fl1.x,  self.carWidth/2 + fl1.y, self.carLenght+fl2.x,  self.carWidth/2 + fl2.y)

        # draw turn point (center of turning) and radius
        if self.turnPoint.x != 0 and self.turnPoint.y != 0:
            pygame.draw.circle(surface, (100,0,0), (int(self.turnPoint.x), int(self.turnPoint.y)), 2)
            pygame.draw.line(surface, (0,50,0), (int(self.frontAxis.x), int(self.frontAxis.y)), (int(self.turnPoint.x), int(self.turnPoint.y)))

if __name__ == '__main__':
    g = pyGame()
    g.run()
