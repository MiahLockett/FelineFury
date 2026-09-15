import pygame
import json

AUTOTILE_MAP = {
	tuple(sorted([(1,0), (0,1)])) : 0,
	tuple(sorted([(1,0), (0,1), (-1,0)])) : 1,
	tuple(sorted([(-1,0), (0,1)])) : 2,
	tuple(sorted([(-1,0), (0,-1), (0,1)])) : 3,
	tuple(sorted([(-1,0), (0,-1)])) : 4,
	tuple(sorted([(-1,0), (0,-1), (1,0)])) : 5,
	tuple(sorted([(1,0), (0,-1)])) : 6,
	tuple(sorted([(1,0), (0,-1), (0,1)])) : 7,
	tuple(sorted([(1,0), (-1,0), (0,1), (0,-1)])) : 8,
}

NEIGHBOUR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1,0), (0,0), (-1,1), (0,1), (1,1)] #Using Tuples
PHYSICS_TILES = {'grass', 'stone'} #faster than using a list to check tile types, using sets
#^^ what tiles I want to add collision to
AUTOTILE_TYPES = {'grass', 'stone'} #what tiles i want to automatically change based on placement

class Tilemap:
	def __init__(self, game, tile_size=16):
		self.game = game
		self.tile_size = tile_size
		self.tilemap = {} #dictionary as more convenient and efficient
		self.offgrid_tiles = [] #list
		
	def extract(self, id_pairs, keep=False): #adding particles
		matches = []
		for tile in self.offgrid_tiles.copy():
			if (tile['type'], tile['variant']) in id_pairs: #searching 
				matches.append(tile.copy())
				if not keep:
					self.offgrid_tiles.remove(tile)

		for loc in self.tilemap:
			tile = self.tilemap[loc]
			if (tile['type'], tile['variant']) in id_pairs:
				matches.append(tile.copy()) #String concatenation
				matches[-1]['pos'] = matches[-1]['pos'].copy()
				matches[-1]['pos'][0] *= self.tile_size #pixel coords of x-axis
				matches[-1]['pos'][1] *= self.tile_size #pixel coords of y-axis
				if not keep:
					del self.tilemap[loc]

		return matches

	def tiles_around(self,pos):
		tiles = []
		tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))	
		for offset in NEIGHBOUR_OFFSETS:
			check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1]) #String conversation
			if check_loc in self.tilemap:
				tiles.append(self.tilemap[check_loc])
		return tiles #give us all the tiles around this location		

	def save(self, path): #saving created map, converting into json
		f = open(path, 'w')
		json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f) #json.dump() writes files
		f.close()

	def load(self, path):
		f = open(path, 'r') #read from map file
		map_data = json.load(f) #Reading Files
		f.close()

		self.tilemap = map_data	['tilemap']
		self.tile_size = map_data	['tile_size']
		self.offgrid_tiles = map_data	['offgrid']

	def solid_check(self, pos):
		tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
		if tile_loc in self.tilemap:
			if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
				return self.tilemap[tile_loc]		

	def physics_rects_around(self, pos):
		rects = []
		for tile in self.tiles_around(pos):
			if tile['type'] in PHYSICS_TILES:
				rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
		return rects

	def autotile(self): #automatically place what type of tile should come next
		for loc in self.tilemap:
			tile = self.tilemap[loc]
			neighbours = set()
			for shift in [(1,0), (-1,0), (0,-1), (0,1)]: #neighbour checking tiles
				check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
				if check_loc in self.tilemap:
					if self.tilemap[check_loc]['type'] == tile['type']: #ensures only automatically places for the same tile type, not variants
						neighbours.add(shift)
			neighbours = tuple(sorted(neighbours))
			if (tile['type'] in AUTOTILE_TYPES) and (neighbours in AUTOTILE_MAP):
				tile['variant'] = AUTOTILE_MAP[neighbours]


	def render(self, surf, offset=(0,0)):
		for tile in self.offgrid_tiles: #pattern matching with dictionary lookup
			surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1])) 
		
		#more efficient way of only loading tiles around, using nested loops
		for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
			for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
				loc = str(x) + ';' + str(y)
				if loc in self.tilemap:
					tile = self.tilemap[loc]
					surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

		
		#for loc in self.tilemap:
		#	tile = self.tilemap[loc]
		#	surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))

		
