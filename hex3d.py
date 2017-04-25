from __future__ import division

import sys
import random

import numpy as np
import pygame as pg
import opensimplex as simp


CAPTION = "Hex 3D"

BACKGROUND = pg.Color("darkslategray")
TRANSPARENT = (0, 0, 0, 0)
SCREEN_SIZE = (1200, 650)
FPS = 60

SQRT_3 = 3**0.5
BASE_POINTS = np.array([[(-1, -SQRT_3), (1, -SQRT_3), (2, 0),
                         (1, SQRT_3), (-1, SQRT_3), (-2, 0)]])

TERRAIN = [("Water", 0.3), ("Beach", 0.4), ("Desert", 0.45), ("Forest", 0.5),
           ("Jungle", 0.65), ("Mountain", 0.8), ("Snow", 1)]


TERRAIN_COLORS = {"Water" : (84, 153, 199),
                  "Beach" : pg.Color("tan"),
                  "Forest" : pg.Color("forestgreen"),
                  "Jungle" : pg.Color("darkgreen"),
                  "Mountain" : pg.Color("sienna"),
                  "Desert" : pg.Color("gold"),
                  "Snow" : pg.Color("white")}


TERRAIN_HEIGHTS = {"Water" : 5,
                   "Beach": 10,
                   "Desert": 15,
                   "Forest": 20,
                   "Jungle": 30,
                   "Mountain": 40,
                   "Snow": 50}
                   

class MapGen(object):    
    def __init__(self, size, seed=None, frequency=None):
        self.seed = seed or random.randrange(2**32)
        self.freq = frequency or random.randrange(5, 10)
        self.size = self.width, self.height = size
        noise = self.gen_noise(simp.OpenSimplex(self.seed), self.freq)
        self.terrain = self.gen_map(noise)
        print(self)

    def __str__(self):
        template = "Map created with:\n   Size: {}\n   Seed: {}\n   Freq: {}"
        return template.format(self.size, self.seed, self.freq)

    def noise(self, gen, nx, ny, freq=10):
        # Rescale from -1.0:+1.0 to 0.0:1.0
        return gen.noise2d(freq*nx, freq*ny) / 2.0 + 0.5

    def gen_noise(self, gen, freq=10):
        vals = {}
        for y in range(self.width):
            for x in range(self.height):
                nx = float(x)/self.width - 0.5
                ny = float(y)/self.height - 0.5
                vals[x,y] = self.noise(gen, nx, ny, freq)
        return vals

    def gen_map(self, noise):
        mapping = [["biome"]*self.height for _ in range(self.width)]
        for x,y in noise:
            for biome, tolerance in TERRAIN:
                if noise[x,y] < tolerance:
                    mapping[y][x] = biome
                    break
        return mapping


class HexTile(pg.sprite.Sprite):
    def __init__(self, biome, index, *groups):
        super(HexTile, self).__init__(*groups)
        self.index = index
        self.image = None
        self.rect = None
        self.biome = biome

    def update(self, tiles, offset, point_array):
        self.image = tiles[self.biome]
        self.rect = self.image.get_rect()
        point = point_array[0][self.index]
        self.rect.bottomleft = point[0] - offset[0], point[1] + offset[1]

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class HexMap(object):
    def __init__(self, size, center):
        self.width, self.height = size
        self.angle = 0
        self.squash_ratio = 0.5
        self.scale = 10
        ##self.mapping = MapGen(size, seed=1195699439, frequency=6)
        self.mapping = MapGen(size)
        self.draw_order = None
        self.tiles, self.points = self.make_map()
        self.start_points = self.points.copy()
        self.recenter(center)
        self.change = True
        self.angle_delta = 60

    def make_map(self):
        tiles = pg.sprite.Group()
        row_offset = 2*SQRT_3
        col_offset = 3
        stagger = SQRT_3
        points = []
        for i in range(self.width):
            for j in range(self.height):
                biome = self.mapping.terrain[i][j]
                pos = (col_offset*i, row_offset*j + stagger*(i%2))
                points.append(pos)
                hextile = HexTile(biome, i*self.height+j, tiles)
                if i == self.width//2 and j == self.height//2:
                    self.center = pos
        points = np.array([points], dtype=float)
        return tiles, points

    def reset(self):
        self.angle = 0
        self.squash_ratio = 0.5
        self.scale = 10
        self.change = True

    def recenter(self, new_center):
        current = self.center
        offset = new_center[0] - current[0], new_center[1] - current[1]
        self.points += offset
        self.start_points += offset
        self.center = new_center

    def azimuthal(self, direction, inc=0.1):
        self.squash_ratio = max(0.1, min(1, self.squash_ratio + inc*direction))
        self.change = True

    def rotate(self, angle):
        self.angle = (self.angle + angle) % (360)
        self.change = True

    def zoom(self, ammount):
        self.scale = max(3, min(20, self.scale + ammount))
        self.change = True

    def transform(self, rot):
        points = (self.start_points - self.center)*self.scale
        points = np.dot(points, rot.T)
        points = points * (1, self.squash_ratio) + self.center
        return points
    
    def draw(self, surface):
        for tile in self.draw_order:
            tile.draw(surface)

    def update(self):
        rel = pg.mouse.get_rel()
        if pg.mouse.get_pressed()[2]:
            self.rotate(-rel[0]/2)
            self.azimuthal(1, rel[1]*0.0025)
        if self.change:
            angle = np.radians(self.angle)
            cos = np.cos(angle)
            sin = np.sin(angle)
            rot = np.array([[cos, -sin], [sin, cos]])
            self.points = self.transform(rot)
            tile_images, center = make_tiles(rot, self.scale, self.squash_ratio)
            self.tiles.update(tile_images, center, self.points)
            self.draw_order = sorted(self.tiles, key=lambda t: t.rect.bottom)
            self.change = False

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                self.rotate(-self.angle_delta)
            elif event.key == pg.K_RIGHT:
                self.rotate(self.angle_delta)
            elif event.key == pg.K_DOWN:
                self.azimuthal(1)
            elif event.key == pg.K_UP:
                self.azimuthal(-1)
            elif event.key in (pg.K_PLUS, pg.K_KP_PLUS, pg.K_EQUALS):
                self.zoom(2)
            elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
                self.zoom(-2)
            elif event.key == pg.K_SPACE:
                self.reset()
        elif event.type == pg.MOUSEBUTTONDOWN:
            pg.mouse.get_rel()
            if event.button == 4:
                self.zoom(1)
            elif event.button == 5:
                self.zoom(-1)
            

class App(object):
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.done = False
        self.hexmap = HexMap((60,60), self.screen_rect.center)
        
    def update(self):
        self.hexmap.update()

    def render(self):
        self.screen.fill(BACKGROUND)
        self.hexmap.draw(self.screen)
        pg.display.update()

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            self.hexmap.get_event(event)

    def display_fps(self):
        """Show the programs FPS in the window handle."""
        caption = "{} - FPS: {:.2f}".format(CAPTION, self.clock.get_fps())
        pg.display.set_caption(caption)
        
    def main_loop(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.render()
            self.clock.tick(FPS)
            self.display_fps()


def make_tiles(rot, scale, squash):
    border = 2 if scale > 8 else 1
    points = (np.dot(BASE_POINTS[0]*scale, rot.T) * (1, squash))
    min_x, min_y = np.min(points[:,0]), np.min(points[:,1])
    points -= min_x, min_y
    points = np.ceil(points)
    max_x, max_y = np.max(points[:,0]), np.max(points[:,1])
    footprint = pg.Rect((0, 0, max_x, max_y))
    tiles = {}
    for biome,_ in TERRAIN:
        color = TERRAIN_COLORS[biome]
        bottom_color = [0.5 * col for col in color[:3]]
        height = TERRAIN_HEIGHTS[biome]*(scale/5)
        surf = pg.Surface((max_x+border,max_y+height+border), flags=pg.SRCALPHA)
        top = points.tolist()
        poly = sorted(top, key=lambda p: p[1], reverse=True)
        top_order = sorted(poly[:4])
        bottom_order = [(x,y+height) for x,y in top_order]
        poly_order = bottom_order + top_order[::-1]
        pg.draw.polygon(surf, bottom_color, poly_order)
        pg.draw.polygon(surf, color, top)
        pg.draw.lines(surf, pg.Color("black"), 0, bottom_order, border)
        pg.draw.lines(surf, pg.Color("black"), 1, top, border)
        for pair in zip(bottom_order, top_order):
            pg.draw.line(surf, pg.Color("black"), pair[0], pair[1], border)
        tiles[biome] = surf
    return tiles, (footprint.w//2, footprint.h//2)
    

def main():
    pg.init()
    pg.display.set_caption(CAPTION)
    pg.display.set_mode(SCREEN_SIZE)
    App().main_loop()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
