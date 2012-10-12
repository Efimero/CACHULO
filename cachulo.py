import pygame,sys,os
from pygame.locals import *
pg = pygame
pg.init()
class G(object): pass #Global container object

class Fhtagn(object):
	def __init__(self):
		G.root = self
		self.screen = pg.display.set_mode((800,600))
		pg.display.set_caption('CACHULO RAISES FROM RILE')
		pg.key.set_repeat(10,10)
		pg.event.set_allowed(QUIT)
		self.c = pg.time.Clock()
		G.loader = Loader()
		self.vx,self.vy = (0,0)
		self.drawstack = pg.sprite.LayeredUpdates()
		self.bg = pg.sprite.Sprite()
		self.bg.image = pg.image.load('sueloahitoguapo.png').convert()
		self.bg.rect = pg.Rect(0,0,1024,768)
		self.bg.add(self.drawstack)
		self.bg.layer = 0
		self.player = Cthulhu()
		self.load_rlyeh('test.lev')

	def start(self):
		while 1:
			for event in pg.event.get():
				if event.type == pg.QUIT: sys.exit()
			if pg.display.get_active():
				keys = pg.key.get_pressed()
				if keys[K_UP] and not up_lock:
					self.player.go_up()
					up_lock = True
				if not keys[K_UP]:
					up_lock = False
					self.player.no_up()
				if keys[K_RIGHT]: self.player.go_right()
				elif keys[K_LEFT]: self.player.go_left()
				# if keys[K_w]: self.vy += 3
				# if keys[K_a]: self.vx += 3
				# if keys[K_s]: self.vy -= 3
				# if keys[K_d]: self.vx -= 3
				self.screen.fill((255,255,255))
				self.update_view()
				self.drawstack.update()
				self.drawstack.draw(self.screen)
				# pg.draw.rect(self.screen,(255,0,0),self.player.rect,1)
				# pg.draw.circle(self.screen,(0,0,255),(self.player.dx,self.player.dy),5,1)
				pg.display.flip()
				self.c.tick(60)
			else:
				self.c.tick(5)

	def update_view(self):
		xt = self.player.ox + self.player.dx\
			-self.screen.get_width()/2 +self.player.rect.width/2
		yt = self.player.oy + self.player.dy\
			-self.screen.get_height()/2 +self.player.rect.height/2
		self.vx -= (self.vx - xt)/5
		self.vy -= (self.vy - yt)/5
		for i in self.drawstack:
			try:
				i.place(self.vx,self.vy)
			except:
				continue

	def load_rlyeh(self,f=False):
		if not f:
			import Tkinter, Tkconstants, tkFileDialog
			root = Tkinter.Tk()
			root.withdraw()
			f = tkFileDialog.askopenfilename(defaultextension='.lev',\
				filetypes=[('Level file', '.lev'),],title='Abrir un nivel...')
		if not f: return False
		config = {}
		with open(f) as cfg:
			for line in cfg:
				try:
					k,v = line.split('=',1)
				except:
					continue
				try:
					config[k.strip()] = int(v.strip())
				except ValueError:
					config[k.strip()] = v.strip()
		# print config
		rlyeh = []
		with open(config['map']) as gaia:
			for line in gaia:
				# print line
				for land in line:
					rlyeh.append(land)
		w,h = (115,115)
		x = 0
		y = 0
		for tile in rlyeh:
			if tile == '#':
				t = Floor(x*w,y*h)
			if tile == 'C':
				self.player.tp(x*w,y*h)
			if tile == '.':
				t = Cultist(x*w,y*h)
			x += 1
			if x > config['size']:
				x = 0
				y += 1


class Cthulhu(pg.sprite.Sprite):
	def __init__(self):
		super(Cthulhu, self).__init__()
		self.vx,self.vy = self.dx,self.dy = self.ox,self.oy = (0,0)
		self.sprite = [
			G.loader.load_alpha('cachulo_stand.png'),
			G.loader.load_alpha('cachulo_walk1.png'),
			G.loader.load_alpha('cachulo_walk2.png'),
			G.loader.load_alpha('cachulo_jump.png'),
		]
		for s in self.sprite[:]:
			self.sprite.append(pg.transform.flip(s, True, False))
		self.rect = pg.Rect(0,0,
			self.sprite[0].get_width(), self.sprite[0].get_height())
		self.fall = True
		self.fall_speed = 0
		self.jump = False
		self.jump_counter = 0
		self.walk = False
		self.left = False
		self.frame = 0
		self.layer = 10
		self.tick_rect()
		self.add(G.root.drawstack)
		self.solid = []

	def tick_rect(self):
		self.rect = pg.Rect(self.ox+self.dx+self.vx,self.oy+self.dy+self.vy,
			self.rect.width,self.rect.height)

	def update(self):
		if not self.solid:
			for i in G.root.drawstack:
				if isinstance(i, Floor):
					self.solid.append(i)
		if self.walk:
			if self.left: self.dx -= 8
			else: self.dx += 8
		if self.jump:
			self.dy -= self.jump_counter if self.jump_counter < 15 else 15
			self.jump_counter -= 1
		if self.jump_counter <= 0:
			self.jump = False
			self.fall = True
		if self.fall:
			self.dy += self.fall_speed
			self.fall_speed += 1
			if self.fall_speed >= 20: self.fall_speed = 20
		self.tick_rect()
		for coll in pg.sprite.spritecollide(self,G.root.drawstack, False):
			if coll in self.solid:
				if self.walk:
					if self.left:
						if self.rect.top > coll.rect.top - self.rect.height*2/3\
						and self.rect.top < coll.rect.top + coll.rect.height*2/3\
						and self.rect.left > coll.rect.left + coll.rect.width/2\
						and self.rect.left < coll.rect.left + coll.rect.width - self.rect.width/3:
							self.dx = -self.ox -self.vx + coll.rect.left + coll.rect.width - self.rect.width/3
							self.tick_rect()
					else:
						if self.rect.top > coll.rect.top - self.rect.height*2/3\
						and self.rect.top < coll.rect.top + coll.rect.height*2/3\
						and self.rect.left < coll.rect.left + coll.rect.width/2\
						and self.rect.left > coll.rect.left - self.rect.width*2/3:
							self.dx = -self.ox -self.vx + coll.rect.left - self.rect.width*2/3
							self.tick_rect()
				if self.jump\
				and self.rect.left - 10 > coll.rect.left - self.rect.width*2/3\
				and self.rect.left + 10 < coll.rect.left + coll.rect.width - self.rect.width/3\
				and self.rect.top < coll.rect.top + int(coll.rect.height*.8)\
				and self.rect.top > coll.rect.top:
					self.dy = -self.oy -self.vy + coll.rect.top + int(coll.rect.height*.8)
					self.jump_counter = 0
					self.jump = False
					self.fall = True
					self.tick_rect()
				if self.fall\
				and self.rect.left > coll.rect.left - self.rect.width*2/3\
				and self.rect.left < coll.rect.left + coll.rect.width - self.rect.width/3\
				and self.rect.top < coll.rect.top - self.rect.height*2/3:
					self.fall = False
					self.fall_speed = 0
					self.dy = -self.oy -self.vy + coll.rect.top - int(self.rect.height*.9)
					self.tick_rect()
			elif isinstance(coll, Pickup):
				coll.pick()
		self.frame += 1
		if self.frame >= 6*4: self.frame = 0
		if self.fall and not self.jump:
			self.image = self.sprite[3+4*self.left]
		elif self.jump and not self.fall:
			self.image = self.sprite[2+4*self.left]
		elif not self.walk:
			self.image = self.sprite[0+4*self.left]
		elif self.frame <= 6:
			self.image = self.sprite[0+4*self.left]
		elif self.frame <= 6*2:
			self.image = self.sprite[1+4*self.left]
		elif self.frame <= 6*3:
			self.image = self.sprite[2+4*self.left]
		else:
			self.image = self.sprite[1+4*self.left]
		self.walk = False

	def go_up(self):
		if not(self.fall or self.jump):
			self.jump = True
			self.jump_counter = 25

	def no_up(self):
		if self.jump and self.jump_counter > 5:
			self.jump_counter = 5

	def go_left(self):
		self.walk = True
		self.left = True

	def go_right(self):
		self.walk = True
		self.left = False

	def tp(self,x,y):
		self.ox,self.oy = (x,y)

	def place(self,x,y):
		# print , self.ox, x, self.ox-x
		self.vx,self.vy = (-x,-y)
		self.tick_rect()


class Floor(pg.sprite.Sprite):
	def __init__(self,x,y):
		super(Floor, self).__init__()
		self.image = G.loader.load_alpha('floor4.png')
		self.w, self.h = (self.image.get_width(), self.image.get_height())
		self.ox = self.x = x
		self.oy = self.y = y
		self.rect = pg.Rect(self.x,self.y,self.w,self.h)
		self.layer = 20
		self.add(G.root.drawstack)

	def place(self,x,y):
		self.x = self.ox - x
		self.y = self.oy - y
		self.rect = pg.Rect(self.x,self.y,self.w,self.h)


class Pickup(pg.sprite.Sprite):
	def __init__(self,x,y,image):
		super(Pickup, self).__init__()
		self.image = G.loader.load_alpha(image)
		self.w, self.h = (self.image.get_width(), self.image.get_height())
		self.ox = self.x = x
		self.oy = self.y = y
		self.rect = pg.Rect(self.x,self.y,self.w,self.h)
		self.layer = 5
		self.add(G.root.drawstack)

	def place(self,x,y):
		self.x = self.ox - x
		self.y = self.oy - y
		self.rect = pg.Rect(self.x,self.y,self.w,self.h)

	def pick(self):
		pass


class Cultist(Pickup):
	def __init__(self,x,y):
		super(Cultist, self).__init__(x+45,y+93,'cultist.png')

	def pick(self):
		super(Cultist, self).pick()
		self.image = G.loader.load_alpha('cultistb.png')


class Loader(object):
	def __init__(self):
		self.res = {}

	def load_alpha(self,image):
		if not image in self.res.keys():
			# print 'Loading:', image
			surf = pg.image.load(image)
			self.res[image] = pg.transform.scale(surf,(surf.get_width()/2,
				surf.get_height()/2)).convert_alpha()
		return self.res[image]


def main():
	Fhtagn().start()


if __name__ == '__main__':
	main()