from board import Board
import time
import pygame

clock = pygame.time.Clock()

def main():
	pygame.init()
	board = Board()
	first = True

	#while True:
	while board.is_ended == False:
		board.board_display(first)
		first = False
		board.board_events()
		board.auto_mode()
		pygame.display.update()
		clock.tick(board.fps)

	board.board_display(first)
	pygame.display.update()
	time.sleep(5)
	pygame.display.quit()
	pygame.quit()
	return 0


if __name__ == '__main__':
    main()
