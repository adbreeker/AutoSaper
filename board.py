import pygame
import random
import sys
import time

MARGIN = 20  # marginesy - odległość kraty od końca okna
SQUARE_HEIGHT = 35
SQUARE_WIDTH = 35
CENTER_DIST = 38  # odległość pomiędzy środkami kwadratów
BOARDCOLS = 20  # liczba kolumn planszy
BOARDROWS = BOARDCOLS  # liczba wierszy planszy
WINDOW_HEIGHT = BOARDCOLS * CENTER_DIST + (2 * MARGIN)
WINDOW_WIDTH = BOARDROWS * CENTER_DIST + (2 * MARGIN)


class Field:
	def __init__(self, coordinates, position):
		Board.fields.append(self)
		self.position = position
		self.rect = pygame.Rect(coordinates[0], coordinates[1], SQUARE_WIDTH, SQUARE_HEIGHT)
		self.color = (100, 100, 100)
		self.open = False
		self.marked = False
		self.close_bombs = 0
		self.bomb = self.make_bombs()
		self.redisp = True

	def make_bombs(self):
		random_choice = random.randint(1, 100)
		if random_choice <= 15:
			if self.position not in Board.bombs: Board.bombs.append(self.position)
			return True
		else:
			return False

	def open_field(self):
		if Board.first_click == True and self.bomb == True:
			Board.first_click = False
			print("podmienilem bombe")
			self.bomb = False
			Board.bombs.remove(self.position)
			close8 = Board.list_of_close(Board,self.position)
			for pos in close8:
				Board.fields[pos].close_bombs -=1
			self.open_field()
			if self.close_bombs == 0:
				Board.open_adjecent(Board,self.position)

		else:
			Board.first_click = False
			self.color = (200, 200, 200)
			self.open = True
			self.redisp = True
			#print("moja pozycja: ", self.position)
			if self.position not in Board.open_fields:
				Board.open_fields.append(self.position)
			if self.position in Board.close_fields:
				Board.close_fields.remove(self.position)
			if self.bomb == True:
				self.color = (165, 42, 42)
				print("You lost :(")
				Board.is_ended = True

	def mark_field(self):
		self.color = (179, 179, 0)
		self.redisp = True
		self.marked = True
		if self.bomb == True:
			if self.position not in Board.marked_bombs: Board.marked_bombs.append(self.position)
		if self.position in Board.close_fields:
			Board.close_fields.remove(self.position)


	def unmark_field(self):
		self.color = (100,100,100)
		self.redisp = True
		self.marked = False
		if self.bomb == True:
			if self.position in Board.marked_bombs: Board.marked_bombs.remove(self.position)
		if self.position not in Board.close_fields:
			Board.close_fields.append(self.position)

	# board -----------------------------------------------------------------------------------------------------------------------

class Board:
	fields = []
	bombs = []
	close_fields = []
	open_fields = []
	marked_bombs = []
	first_click = True
	is_ended = False
	automode = False # jesli chcesz zaczac od automatu wystarczy zmienic te opcje na True
	fps = 30

	def __init__(self):
		pygame.display.set_caption("AutoSaper")
		self.game_display = pygame.display.set_mode((WINDOW_HEIGHT, WINDOW_WIDTH))
		self.init_board()
		self.count_close()
		print("Bombs on map: ", len(self.bombs))

	def init_board(self):
		x = MARGIN
		y = MARGIN
		pos = 0
		for i in range(BOARDROWS):
			for j in range(BOARDCOLS):
				Field((x, y),pos)
				if pos not in self.close_fields: self.close_fields.append(pos)
				x += CENTER_DIST
				pos +=1
			y += CENTER_DIST
			x = MARGIN

	def board_events(self):
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # klawisz esc zamyka program
				sys.exit(0)

			if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
				self.help_mode()

			if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
				if self.automode == False:
					self.fps = 5
					self.automode = True
				else:
					self.fps = 30
					self.automode = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				clicked = [square for square in self.fields if square.rect.collidepoint(pos)]
				for square in clicked:
					if event.button == 1:
						square.open_field()
						if square.bomb == False and square.close_bombs==0:
							self.open_adjecent(square.position)
					if event.button == 3:
						if square.marked == False:
							square.mark_field()
						else:
							square.unmark_field()



	def list_of_close(self,pos):
		list = []
		for i in range(-1,2):
			for j in range(-1,2):
				position = pos + i*BOARDCOLS + j
				if position >=0 and position < BOARDCOLS*BOARDROWS:
					list.append(position)

		if pos%BOARDCOLS == 0:
			tr = (pos - BOARDCOLS - 1)
			if tr in list: list.remove(tr)
			tr = (pos - 1)
			if tr in list: list.remove(tr)
			tr = (pos + BOARDCOLS - 1)
			if tr in list: list.remove(tr)

		if pos%BOARDCOLS == (BOARDCOLS - 1):
			tr = (pos - BOARDCOLS + 1)
			if tr in list: list.remove(tr)
			tr = (pos + 1)
			if tr in list: list.remove(tr)
			tr = (pos + BOARDCOLS + 1)
			if tr in list: list.remove(tr)

		list.remove(pos)
		return list


	def count_close(self):
		for square in self.fields:
			close8 = self.list_of_close(square.position)
			for pos in close8:
				#if pos >= 0 and pos < BOARDCOLS*BOARDROWS:
				if self.fields[pos].bomb == True:
					square.close_bombs +=1


	def open_adjecent(self, progenitor):
		close8 = self.list_of_close(progenitor)
		for pos in close8:
			#if (pos < BOARDCOLS * BOARDROWS and pos >= 0):
			if self.fields[pos].bomb == False and self.fields[pos].open == False:
				self.fields[pos].open_field()
				if self.fields[pos].close_bombs == 0:
					self.open_adjecent(pos)


	#aditional modes -------------------------------------------------------------------------------------------------------------------
	def mark_bombs(self):
		for square in self.fields:
			if square.open == True and square.close_bombs > 0:
				close8 = self.list_of_close(square.position)
				close_open = 0
				potential = []
				for field in close8:
					if self.fields[field].open == True:
						close_open +=1
					else:
						potential.append(self.fields[field].position)
				if (len(close8)-close_open) == square.close_bombs:
					for pf in potential:
						self.fields[pf].mark_field()




	def open_unmarked(self):
		for square in self.fields:
			if square.open == True: #and square.close_bombs > 0:
				close8 = self.list_of_close(square.position)
				close_open = 0
				close_marked = 0
				potential = []
				for field in close8:
					if self.fields[field].open == True:
						close_open +=1
					if self.fields[field].marked == True:
						close_marked +=1
					if self.fields[field].marked == False and self.fields[field].open == False:
						potential.append(field)

				if square.close_bombs == close_marked and (8-close_open-close_marked)>0:
					for pf in potential:
						self.fields[pf].open_field()
						if self.fields[pf].bomb == False and self.fields[pf].close_bombs==0:
							self.open_adjecent(pf)




	def help_mode(self):
		self.mark_bombs()
		self.board_display(False)
		pygame.display.update()
		time.sleep(0.5)
		self.open_unmarked()
		print("Marked bombs: ", len(self.marked_bombs))

	def auto_mode(self):
		if self.automode == True and self.is_ended==False:
			pre = len(self.open_fields)
			self.mark_bombs()
			self.board_display(False)
			pygame.display.update()
			time.sleep(0.5)
			self.open_unmarked()
			self.board_display(False)
			pygame.display.update()
			time.sleep(0.5)
			if pre == len(self.open_fields) and len(self.close_fields) > 0:
				#print("wyjebałem sie po sprawdzaniu pre")
				if len(self.close_fields) > 1:
					rch = random.randint(0,(len(self.close_fields)-1))
					chf = self.close_fields[rch]
					while self.fields[chf].marked == True:
						#print("siedze w pentli while: ", chf)
						rch = random.randint(0,(len(self.close_fields)-1))
						chf = self.close_fields[rch]
				else:
					chf = 0
				self.fields[chf].open_field()
				if self.fields[chf].bomb == False and self.fields[chf].close_bombs == 0:
					self.open_adjecent(self.fields[chf].position)




	#display --------------------------------------------------------------------------------------------------------------------------

	def board_display(self, first):
		if first == True:
			self.game_display.fill((0,0,0))
		if len(self.marked_bombs) == len(self.bombs):
			print("Winner !!!")
			self.is_ended = True

		for square in self.fields:
			if square.redisp == True:
				pygame.draw.rect(self.game_display, square.color, square.rect)
				if square.open == True and square.close_bombs>0 and square.bomb==False:
					number_font = pygame.font.SysFont(None,30)
					number_image = number_font.render(str(square.close_bombs), True, (0, 0, 0))
					self.game_display.blit(number_image, square.rect)
				square.redisp = False

