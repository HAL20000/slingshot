#    This file is part of Slingshot.
#
# Slingshot is a two-dimensional strategy game where two players attempt to shoot one
# another through a section of space populated by planets.  The main feature of the
# game is that the shots, once fired, are affected by the gravity of the planets.

# Slingshot is Copyright 2007 Jonathan Musther and Bart Mak. It is released under the
# terms of the GNU General Public License version 2, or later if applicable.

# Slingshot is free software; you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation; either
# version 2 of the License, or any later version.

# Slingshot is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with Slingshot;
# if not, write to
# the Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

# Copyright (C) 2009 Marcus Dreier <m-rei@gmx.net>
# Copyright (C) 2010 Ryan Kavanagh <ryanakca@kubuntu.org>

from slingshot.settings import *
from slingshot.general import *
import pygame
import math
from math import sqrt
from random import randint
import scipy.integrate

class Particle(pygame.sprite.Sprite):

        def __init__(self, planets, pos = (0.0, 0.0), size = 10):
                ''' Initialize the particle. '''
                pygame.sprite.Sprite.__init__(self)
                if size == 5:
                        self.image = Settings.particle_image5
                else:
                        self.image = Settings.particle_image10
                self.rect = self.image.get_rect()
#               self.image, self.rect = load_image("explosion-10.png", (0,0,0))
                self.pos = pos
                self.impact_pos = pos
                self.size = size
                angle = randint(0, 359)
                if size == 5:
                        speed = randint(Settings.PARTICLE_5_MINSPEED,Settings.PARTICLE_5_MAXSPEED)
                else:
                        speed = randint(Settings.PARTICLE_10_MINSPEED,Settings.PARTICLE_10_MAXSPEED)
                # (x velocity, y velocity)
                self.v = (0.1 * speed * math.sin(angle), -0.1 * speed * math.cos(angle))
                self.flight = Settings.MAX_FLIGHT
                self.last_sol = None

                c = 3e1

                def rhs (t, y):
                    a = (0.0, 0.0)
                    for p in planets:
                        p_pos = p.get_pos()
                        mass = p.get_mass()
                        dx = y[0] - p_pos[0]
                        dy = y[1] - p_pos[1]
                        d = dx**2 + dy**2
                        # a is the acceleration in pixels/tick
                        #  ->   [ G * m_p * \delta d_x     G * m_p * \delta d_y   ]
                        #  a  = [ ---------------------- , ---------------------- ]
                        #       [      r ^ (1/3)                 r ^ (1/3)        ]
                        try:
                            a = (a[0] -(Settings.g * mass * dx) / (d *
                                math.sqrt(d)), a[1] -(Settings.g * mass * dy) /
                                (d * math.sqrt(d)))
                        except ZeroDivisionError:
                            # Hackishly take any silly particles out of the game.
                            a = (10000, 10000)
                        # It's been a tick, update our velocity according to our
                        # acceleration
                        #self.v = (self.v[0] - a[0], self.v[1] - a[1])
                    #print y
                    #print (y[3] * y[3] - y[4] * y[4] - y[5] * y[5])
                    ginv = 1 / math.sqrt (y[2] * y[2] + y[3] * y[3] + 1 * 1 * c * c)
                    return [c * ginv * y[2], c * ginv * y[3], a[0], a[1]]

                gamma = 1 / math.sqrt (1 - (self.v[0]**2 + self.v[1]**2) / (c**2))
                self.sol = scipy.integrate.solve_ivp (rhs, [0,
                    Settings.MAX_FLIGHT + 10], [self.pos[0], self.pos[1], gamma
                        * self.v[0], gamma * self.v[1]], dense_output = True,
                    rtol = 0.2, method='RK23')

        def max_flight(self):
                if self.flight < 0:
                        return True
                else:
                        return False

        def update(self, planets):
                """
                Updates information about ourselves, namely our location.

                @param planets: list of planets
                @type planets: [Planet]

                @return: -1 if we've hit a black hole
                          0 if we've hit a planet
                          1 otherwise
                @rtype: int

                """
                self.flight = self.flight - 1

                self.last_pos = self.pos

                #self.pos = (self.pos[0] + self.v[0], self.pos[1] + self.v[1])

                res = self.sol.sol (Settings.MAX_FLIGHT - self.flight)
                self.pos = (res[0], res[1])
                        #tuple (res[0:1])
                c = 3e1
                ginv = c / math.sqrt (res[2] * res[2] + res[3] * res[3] + 1 * 1 * c
                        * c)
                self.v = (ginv * res[2], ginv * res[3])
                #tuple (res[2:3])

                if not self.in_range():
                        return 0

                for p in planets:
                        p_pos = p.get_pos()
                        r = p.get_radius()
                        # d is not the distance from the planet, it's the distance squared.
                        d = (self.pos[0] - p_pos[0])**2 + (self.pos[1] - p_pos[1])**2
                        if p.type == "Blackhole":
                                min_dist = 2 * Settings.g * p.get_mass() / 9e6
                                if d <= min_dist:
                                        self.impact_pos = p_pos
                                        self.pos = self.impact_pos
                                        return -1
                        elif d <= (r)**2:
                                # This is a planet
                                self.impact_pos = get_intersect(p_pos, r, self.last_pos, self.pos)
                                self.pos = self.impact_pos
                                return 0

                if Settings.BOUNCE:
                        if self.pos[0] > 799:
                                d = self.pos[0] - self.last_pos[0]
                                self.pos = (799, self.last_pos[1] + (self.pos[1] - self.last_pos[1]) * (799 - self.last_pos[0]) / d)
                                self.v = (-self.v[0], self.v[1])
                        if self.pos[0] < 0:
                                d = self.last_pos[0] - self.pos[0]
                                self.pos = (0,self.last_pos[1] +  (self.pos[1] - self.last_pos[1]) * self.last_pos[0] / d)
                                self.v = (-self.v[0], self.v[1])
                        if self.pos[1] > 599:
                                d = self.pos[1] - self.last_pos[1]
                                self.pos = (self.last_pos[0] + (self.pos[0] - self.last_pos[0]) * (599 - self.last_pos[1]) / d, 599)
                                self.v = (self.v[0], -self.v[1])
                        if self.pos[1] < 0:
                                d = self.last_pos[1] - self.pos[1]
                                self.pos = (self.last_pos[0] + (self.pos[0] - self.last_pos[0]) * self.last_pos[1] / d, 0)
                                self.v = (self.v[0], -self.v[1])
#                               print self.pos
#                               print self.last_pos

                self.rect.center = (round(self.pos[0]), round(self.pos[1]))
                return 1

        def in_range(self):
            try:
                if pygame.Rect(-800, -600, 2400, 1800).collidepoint(self.pos):
                        return True
                else:
                        return False
            except:
                return False
                #Hackishly ignore invalid position and let particle leave the
                #scene

        def visible(self):
            """
            Returns whether or not the particle is within the playing area.

            """
            try:
                if pygame.Rect(0, 0, 800, 600).collidepoint(self.pos):
                        return True
                else:
                        return False
            except:
                return False

        def get_pos(self):
                return self.pos

        def get_impact_pos(self):
                return self.impact_pos

        def get_size(self):
                return self.size

class Missile(Particle):

        def __init__(self, trail_screen):
                pygame.sprite.Sprite.__init__(self)
                #Particle.__init__(self) #call Sprite intializer
                self.image, self.rect = load_image("shot.png", (0,0,0))
                self.rect = self.image.get_rect()
                self.trail_screen = trail_screen
                self.last_pos = (0.0, 0.0)

        def launch(self, player, planets):
                self.flight = Settings.MAX_FLIGHT
                self.pos = player.get_launchpoint()
                speed = player.get_power()
                angle = math.radians(player.get_angle())
                self.v = (0.1 * speed * math.sin(angle), -0.1 * speed * math.cos(angle))
                self.trail_color = player.get_color()

                self.score = -Settings.PENALTY_FACTOR * speed

                c = 3e1

                def rhs (t, y):
                    a = (0.0, 0.0)
                    for p in planets:
                        p_pos = p.get_pos()
                        mass = p.get_mass()
                        dx = y[0] - p_pos[0]
                        dy = y[1] - p_pos[1]
                        d = dx**2 + dy**2
                        # a is the acceleration in pixels/tick
                        #  ->   [ G * m_p * \delta d_x     G * m_p * \delta d_y   ]
                        #  a  = [ ---------------------- , ---------------------- ]
                        #       [      r ^ (1/3)                 r ^ (1/3)        ]
                        try:
                            a = (a[0] -(Settings.g * mass * dx) / (d *
                                math.sqrt(d)), a[1] -(Settings.g * mass * dy) /
                                (d * math.sqrt(d)))
                        except ZeroDivisionError:
                            # Hackishly take any silly particles out of the game.
                            a = (10000, 10000)
                        # It's been a tick, update our velocity according to our
                        # acceleration
                        #self.v = (self.v[0] - a[0], self.v[1] - a[1])
                    #print y
                    #print (y[3] * y[3] - y[4] * y[4] - y[5] * y[5])
                    ginv = 1 / math.sqrt (y[2] * y[2] + y[3] * y[3] + 1 * 1 * c * c)
                    return [c * ginv * y[2], c * ginv * y[3], a[0], a[1]]

                gamma = 1 / math.sqrt (1 - (self.v[0]**2 + self.v[1]**2) / (c**2))
                self.sol = scipy.integrate.solve_ivp (rhs, [0,
                    Settings.MAX_FLIGHT + 10], [self.pos[0], self.pos[1], gamma
                        * self.v[0], gamma * self.v[1]], dense_output = True,
                    rtol = 1e-5)

        def update_players(self, players):
                result = 1

                for i in xrange(10):
                        pos = (self.last_pos[0] + i * 0.1 * self.v[0], self.last_pos[1] + i * 0.1 * self.v[1])
                        if players[1].hit(pos):
                                result = 0
                        if players[2].hit(pos):
                                result = 0
                        if result == 0:
                                self.impact_pos = pos
                                self.pos = pos
                                break
                return result

        def draw_status(self, screen):
                txt = Settings.font.render("Power penalty: %d" %(-self.score), 1, (255,255,255))
                rect = txt.get_rect()
                rect.midtop = (399, 5)
                screen.blit(txt, rect.topleft)
                if self.flight >= 0:
                    txt = Settings.font.render("Timeout in %d, Speed: %f"
                            %(self.flight, math.sqrt (self.v[0]**2 +
                                self.v[1]**2) / 3e1), 1,(255,255,255))
                else:
                        txt = Settings.font.render("Shot timed out...", 1, (255,255,255))
                rect = txt.get_rect()
                rect.midbottom = (399, 594)
                screen.blit(txt, rect.topleft)


        def update(self, planets, players):
                result = Particle.update(self, planets)
                result = result * self.update_players(players)
                # Draws the missile's trajectory only if we haven't entered a black hole.
                if result != -1:
                        #pygame.draw.aaline(self.trail_screen, self.trail_color, self.last_pos, self.pos)
                        curve = [self.last_pos]
                        t = Settings.MAX_FLIGHT - self.flight
                        for i in xrange (len (self.sol.t)):
                            if (self.sol.t[i]) < t and (self.sol.t[i]) > (t -
                                    1):
                                curve.append ((self.sol.y[0][i],
                                    self.sol.y[1][i]))
                        curve.append (self.pos)
                        pygame.draw.aalines (self.trail_screen, self.trail_color,
                                False, curve)
                return result

        def get_image(self):
                return self.image

        def get_score(self):
                return self.score
