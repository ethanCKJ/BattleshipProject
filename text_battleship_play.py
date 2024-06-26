import random
from time import sleep
from random import randint, choice
from copy import deepcopy

BOARD_SIZE = 10
MISS_MSG = "Miss!"
HIT_MSG = "Hit!"


def print_title():
    """Prints ASCII art of  the word "BATTLESHIPS" cinematically one line at a time"""
    print("welcome to...")
    text = [
        ".______        ___   .___________.___________. __       _______     _______. __    __   __  .______     _______.",
        "|   _  \      /   \  |           |           ||  |     |   ____|   /       ||  |  |  | |  | |   _  \   /       |",
        "|  |_)  |    /  ^  \ `---|  |----`---|  |----`|  |     |  |__     |   (----`|  |__|  | |  | |  |_)  | |   (----`",
        "|   _  <    /  /_\  \    |  |        |  |     |  |     |   __|     \   \    |   __   | |  | |   ___/   \   \    ",
        "|  |_)  |  /  _____  \   |  |        |  |     |  `----.|  |____.----)   |   |  |  |  | |  | |  |   .----)   |   ",
        "|______/  /__/     \__\  |__|        |__|     |_______||_______|_______/    |__|  |__| |__| | _|   |_______/    ",
        "                                                                                                                "]
    sleep(1)
    for line in text:
        print(line)
        sleep(0.5)


def print_introduction():
    """Displays the mission to the player"""
    sleep_length = 4
    print("INCOMING TRANSMISSION:")
    sleep(3)
    print("Greetings commander, your mission is the destroy the enemy fleet out there in this thick fog.")
    sleep(sleep_length)
    print("Due to the fog, we can't see them and they can't see us.")
    sleep(sleep_length)
    print("But we can hear the sounds of shells hitting their mark.")
    sleep(sleep_length)
    print("Good luck!")
    sleep(1)
    print("END OF TRANSMISSION.")


def print_instructions(self):
    """Prints instructions to the player on how to play the game"""

    print("""In battleships you will take guesses at firing shots at an enemy fleet you cannot see. The enemy fleet will
    also fire shots are you. The first person to destroy all opposing ships wins.

    Gameplay
    1. You will decide where to place your ships.
    2. A coin is flipped to determine who goes first
    3. On your turn you may fire one shot at a target.
    4. On enemy turn, they will fire one shot
    5. Each turn only has one shot
    6. Game ends when you enter "surrender", win or lose.

    Ships:
    CCCCC - carrier
    BBBB - battleship
    DDD - destroyer
    SSS - submarine
    PP - patrol boat
    Both players have one of each of these ships.

    Other symbols:
    ~ - unexplored ocean tile.
    X - Hit (portion of a ship that is hit but the ship is not yet sunk)
    # - Sunk (part of a sunken ship)
    M - Miss (no ships in this tile)
    """)


class Board:
    """Stores data about the battleship board and supplies methods for interacting with the board"""

    def __init__(self, size: int):
        # privateBoard shows ships, water, hits, misses and sinks. Never shown unless for debugging and used for
        # internal calculations.
        # publicBoard shows hits, misses, sinks and water. Always shown to the opponent.
        self.private_board = []
        self.public_board = []
        self.board_width = size
        self.LETTER_TO_COORDINATE_MAP = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
        # Way a ship is represented on the board
        self.SHIP_ART = ["CCCCC", "BBBB", "SSS", "DDD", "PP"]
        self.SHIP_TILE_TO_NAME = {"C": "CARRIER",
                                  "B": "BATTLESHIP",
                                  "D": "DESTROYER",
                                  "S": "SUBMARINE",
                                  "P": "PATROL BOAT"}
        # Stores coordinates of each ship tile.
        self.ship_positions = {}
        # Stores health corresponding to a ship. Used to determine if a ship is sunk.
        self.ship_health_bars = {}
        self.MISS_TILE = "M"
        self.HIT_TILE = "X"
        self.WATER_TILE = "~"
        self.SUNK_TILE = "#"
        self.initialise_board(size)

    def initialise_board(self, size):
        """Creates a size by size board containing only water"""
        self.private_board = []
        for i in range(size):
            self.private_board.append([self.WATER_TILE] * size)
        self.public_board = deepcopy(self.private_board)

    def number_to_letter(self, n):
        """Converts y coordinates to the letters used to label rows on the board"""
        return self.LETTER_TO_COORDINATE_MAP[n]

    def letter_to_number(self, l):
        """Converts letter used to label rows to a y coordinate"""
        return self.LETTER_TO_COORDINATE_MAP.index(l)

    def print_board(self, showShips=False):
        """Prints the board"""
        if showShips:
            board = self.private_board
        else:
            board = self.public_board
        print("   0   1   2   3   4   5   6   7   8   9")
        for y in range(self.board_width):
            print(" " + "+---" * self.board_width + "+")
            print(self.number_to_letter(y), end="")
            for x in range(self.board_width):
                print("| " + board[x][y] + " ", end="")
            print("|")
        print(" " + "+---" * self.board_width + "+")

    def generate_ship_positions(self, ship_art: str, startX: int, startY: int, orientation: str) -> list[int, int]:
        """Returns list of coordinates for all sections of a ship based on its size, position and orientation"""
        positions = []
        ship_length = len(ship_art)
        if orientation == "H":
            for i in range(ship_length):
                positions.append([startX + i, startY])
        else:
            for i in range(ship_length):
                positions.append([startX, startY + i])
        return positions

    def is_on_board(self, x, y):
        return (0 <= x <= 9) and (0 <= y <= 9)

    def is_water_tile(self, x, y):
        return self.private_board[x][y] == self.WATER_TILE

    def is_fire_tile(self, x, y):
        return self.private_board[x][y] == self.HIT_TILE

    def is_miss_tile(self, x, y):
        return self.private_board[x][y] == self.MISS_TILE

    def is_ship_tile(self, x, y):
        return self.private_board[x][y] in self.SHIP_TILE_TO_NAME.keys()

    def is_valid_ship_location(self, ship_positions: list[int, int]):
        """Returns true if all proposed position of a ship on water tiles and within the board"""
        for x, y in ship_positions:
            if not (self.is_on_board(x, y)) or not (self.is_water_tile(x, y)):
                return False
        return True

    def place_ship(self, ship: str, ship_positions: list[list[int]]):
        """Places a ship on the private board, creates a healthbar for the ship and tracks the position of the ship"""
        ship_letter = ship[0]
        for x, y in ship_positions:
            self.private_board[x][y] = ship_letter
        self.ship_positions.setdefault(ship_letter, ship_positions)
        self.ship_health_bars.setdefault(ship_letter, len(ship))

    def auto_place_ships(self):
        """Places all available ships on the map. Mainly used to place the AI fleet"""
        for ship in self.SHIP_ART:
            keep_searching = True
            # Attempt to find valid x coordinate, y coordinate and orientation that allows us to
            # place a ship. When a ship can be placed, place the ship.
            # Repeat until all ships are placed.
            while keep_searching:
                start_x = randint(0, self.board_width - 1)
                start_y = randint(0, self.board_width - 1)
                orientation = choice(("H", "V"))
                ship_positions = self.generate_ship_positions(ship, start_x, start_y, orientation)
                if self.is_valid_ship_location(ship_positions):
                    keep_searching = False
                    self.place_ship(ship, ship_positions)

    def ship_tile_to_art(self, ship_tile: str) -> str:
        """Returns ship art for a ship tile. Returns "CCCCC" for tile "C" """
        for ship in self.SHIP_ART:
            if ship.startswith(ship_tile):
                return ship

    def manual_place_ships(self, command: list, ships_to_place_tiles: list[str]) -> (bool, str, str, list[list[int]]):
        """Allows player input the position of their ships"""
        # Example command is C 4 A H meaning put a Carrier at (4, A) horizontally to the right.
        if len(command) == 4:
            tile = command[0]
            number = command[1]
            letter = command[2]
            orientation = command[3]
            if tile in ships_to_place_tiles:
                if number.isdigit():
                    if letter in self.LETTER_TO_COORDINATE_MAP:
                        if orientation in ("H", "V"):
                            startX = int(number)
                            startY = self.letter_to_number(letter)
                            ship = self.ship_tile_to_art(tile)
                            ship_positions = self.generate_ship_positions(ship, startX, startY, orientation)
                            if self.is_valid_ship_location(ship_positions):
                                return True, tile, ship, ship_positions
        return False, "", "", []

    def place_player_ships(self):
        """Asks player where to place ships and places the ships if the position is valid"""
        ships_to_place_codes = list(self.SHIP_TILE_TO_NAME.keys())
        self.print_board()
        while ships_to_place_codes:
            print("Ships to place: ")
            print("Code| Ship")
            for k in ships_to_place_codes:
                v = self.SHIP_TILE_TO_NAME[k]
                print(k + "   |", v)
            print("Enter ship code, number, letter and orientation (H/V) separated by space")
            print("e.g [C 5 J H] places a carrier horizontally starting at 5J")
            command = input("> ").upper().split(" ")

            # Check if input is valid and extract place to put the ship.
            is_valid_position, code, ship, ship_positions = self.manual_place_ships(command, ships_to_place_codes)
            if is_valid_position:
                self.place_ship(ship, ship_positions)
                ships_to_place_codes.remove(code)
                self.print_board(showShips=True)
            else:
                print("Ensure command is 4 items long, each item is valid and ship does not overlap another ship")

    def is_valid_coordinate(self, command):
        """Returns true if a coordinate is one number (0-9) followed by one letter (A-J)"""
        if len(command) == 2:
            if command[0].isdigit() and command[1] in self.LETTER_TO_COORDINATE_MAP:
                return True
        else:
            return False

    def coordinate_to_cartesian(self, action):
        """Converts an inputted coordinate (number and letter) to x and y coordinates on the board"""
        x = int(action[0])
        y = self.letter_to_number(action[1])
        return x, y

    def mark_ship_sunk(self, ship_code):
        """Change hit tiles of a sunk ship to sunk tiles on both private and public board"""
        sunk = []
        for x, y in self.ship_positions[ship_code]:
            self.private_board[x][y] = self.SUNK_TILE
            self.public_board[x][y] = self.SUNK_TILE
            sunk.append([x, y])
        return sunk

    def is_game_over(self):
        """If health bars of all ships is 0, return True"""
        for i in self.ship_health_bars.values():
            if i != 0:
                return False
        return True

    def shoot(self, x, y) -> (bool, list[list[int]], str, bool):
        """Returns hit, sunk, ship_tile, is_game_over"""
        hit = False
        sunk = []
        ship_tile = ""
        if self.is_water_tile(x, y):
            self.private_board[x][y] = self.MISS_TILE
            self.public_board[x][y] = self.MISS_TILE

        elif self.is_ship_tile(x, y):
            hit = True
            ship_tile = self.private_board[x][y]
            self.ship_health_bars[ship_tile] -= 1
            if self.ship_health_bars[ship_tile] == 0:
                sunk = self.mark_ship_sunk(ship_tile)
            else:
                self.private_board[x][y] = self.HIT_TILE
                self.public_board[x][y] = self.HIT_TILE

        return hit, sunk, ship_tile, self.is_game_over()

    def get_message(self, hit, sunk, ship_tile):
        """Returns message to the player on status of their shots like "Hit!", "Miss!", "Enemy Carrier sunk" """
        if sunk:
            return "Enemy " + self.SHIP_TILE_TO_NAME[ship_tile] + " sunk."
        elif hit:
            return "Hit!"
        else:
            return "Miss!"


class Player:
    def __init__(self, board):
        self.board = board

    def get_player_action(self) -> (int, int):
        """Gets the x and y coordinate of a player's shot and ensures they are on the board."""
        while True:
            print("Enter firing coordinates (number then letter separated by space e.g 0 A)")
            action = input('> ').upper().split(" ")
            if self.board.is_valid_coordinate(action):
                x, y = self.board.coordinate_to_cartesian(action)
                return x, y
            print("Invalid firing coordinates")


class AIConditional:
    """AI has series of conditions based on whether it hits, misses, or sinks. It also considers which ship it sunk"""

    def __init__(self, player_board: Board) -> None:
        self.name = "AIConditional"
        self.player_board = player_board
        self.mode = "seek"
        self.active_hits = []
        # Assume AI and player have the same number and type of ships.
        self.player_ships = player_board.SHIP_ART
        self.WATER_TILE = player_board.WATER_TILE
        self.selected_orientation = []
        self.move_x = None
        self.move_y = None
        self.pointer_x = None
        self.pointer_y = None
        self.do_flank_move = False
        self.first_move = True

    def get_AI_action(self, hit, sunk: list, shipTile) -> tuple[int, int]:
        """Returns x,y coordinate of the AI's shot"""

        if sunk:
            self.do_flank_move = False
            self.active_hits = list(filter(lambda coordinate: coordinate not in sunk, self.active_hits))
            # Remove the sunk player ship
            self.player_ships = list(filter(lambda x: not x.startswith(shipTile), self.player_ships))
            # If no more ships on fire, enter seek mode.
            if not self.active_hits:
                self.mode = "seek"
                return self.seek()
            else:
                # ship tiles are adjacent of a fire tile. ship tile cannot be outside the board
                # valid_orientations is a list containing a mix of [1,0], [0,1], [-1,0], [0, -1] which may lead to a
                # ship tile.
                valid_orientations = []
                index = 0
                while not valid_orientations:
                    active_hit = self.active_hits[index]
                    self.move_x = active_hit[0]
                    self.move_y = active_hit[1]
                    valid_orientations = self.get_adjacent_water_tiles(self.move_x, self.move_y)
                    index += 1
                self.selected_orientation = valid_orientations.pop(random.randint(0, len(valid_orientations) - 1))
                return self.move_along_orientation(self.selected_orientation[0], self.selected_orientation[1])

        if (self.mode == "seek") and (hit == False):
            return self.seek()

        # If seeking then hit a target,
        # 1. We found a target so set mode to "hit"
        # 2. Record hit
        # 3. Get possible valid_orientations that may lead to rest of the hit ship then select a random one
        if (self.mode == "seek") and (hit == True) and (sunk == []):
            self.mode = "attack"
            self.active_hits.append([self.move_x, self.move_y])
            valid_orientations = self.get_possible_orientations(self.move_x, self.move_y)
            self.selected_orientation = valid_orientations.pop(random.randint(0, len(valid_orientations) - 1))
            return self.move_along_orientation(self.selected_orientation[0], self.selected_orientation[1])

        # If currently attacking a still live target
        # continue moving along the target by using the previous orientation
        # A successful flank (hit) also follows this
        if (self.mode == "attack") and (hit == True) and (sunk == []):
            self.do_flank_move = False
            self.active_hits.append([self.move_x, self.move_y])
            # Check if running into the edge of the board
            if not self.player_board.is_on_board(self.move_x + self.selected_orientation[0],
                                                 self.move_y + self.selected_orientation[1]):
                return self.flank()
            else:
                return self.move_along_orientation(self.selected_orientation[0], self.selected_orientation[1])

        # If currently attacking a target and missed, likely means the first strike on the target hit the middle
        # of the ship. So use the first strike point and move in the opposite direction
        # this move is called a flank only perform a flank if there are appropriate tiles for a flank
        if (self.mode == "attack") and (hit == False) and (self.do_flank_move == False):
            return self.flank()

        # A failed flank (miss) means the flank was performed along the horizontal axis while multiple ships are
        # lined side by side along the vertical axis. Alternatively, flank was vertical and ships are horizontal. We
        # restart the process of finding a new orientation using a fire tile.
        if (self.mode == "attack") and (hit == False) and (self.do_flank_move == True):
            self.do_flank_move = False
            active_hit = self.active_hits[0]
            self.move_x = active_hit[0]
            self.move_y = active_hit[1]
            valid_orientations = self.get_adjacent_water_tiles(self.move_x, self.move_y)
            self.selected_orientation = valid_orientations.pop(random.randint(0, len(valid_orientations) - 1))
            return self.move_along_orientation(self.selected_orientation[0], self.selected_orientation[1])

    def seek(self):
        """When seeking, shoot random tiles that are connected to enough tiles such that
        the group of tiles is large enough to contain a ship."""
        valid_move = False
        while not valid_move:
            self.move_x = random.randint(0, self.player_board.board_width - 1)
            self.move_y = random.randint(0, self.player_board.board_width - 1)

            if self.player_board.public_board[self.move_x][self.move_y] == self.WATER_TILE:
                orientations = self.get_possible_orientations(self.move_x, self.move_y)
                if orientations:
                    return self.move_x, self.move_y

    def flank(self):
        """flanking is used when the first shot on a ship hits the middle of the ship
        For example ~~BBBB~~ is a ship
        Firing 4 shots ~~BXXXM~
        A flank is triggered ~~XXXM~"""
        # Check if flank is viable (flank orientation is in possible orientations in the first strike point)
        flank_orientation = [self.selected_orientation[0] * -1, self.selected_orientation[1] * -1]
        orientations = []
        index = 0
        # It is guaranteed that at least one of the active hits is connected to the rest of a ship.
        while not orientations:
            active_hit = self.active_hits[index]
            self.move_x = active_hit[0]
            self.move_y = active_hit[1]
            orientations = self.get_adjacent_water_tiles(self.move_x, self.move_y)
            index += 1

        if flank_orientation in orientations:
            self.do_flank_move = True
            self.selected_orientation = flank_orientation.copy()
        else:
            self.selected_orientation = orientations.pop(random.randint(0, len(orientations) - 1))
        return self.move_along_orientation(self.selected_orientation[0], self.selected_orientation[1])

    def get_valid_orientations(self, move_x, move_y):
        """Returns orientations from a point that may contain enemy ships"""
        # Move front a point
        maxSize = min(map(len, self.player_ships))
        directions = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        valid_directions = []
        for xdir, ydir in directions:
            valid = True
            # Move along a particular direction. If encountered a non water tile then that direction is invalid.
            for i in range(1, maxSize):
                if not self.player_board.public_board[move_x + (xdir * i)][move_y + (ydir * i)]:
                    valid = False
                    break
            if valid:
                valid_directions.append([xdir, ydir])
        return valid_directions

    def get_possible_orientations(self, move_x, move_y):
        """Returns the orientation(s) [-1, 0], [0, 1], [1, 0], [0, -1] that may have a ship"""
        min_ship_length = min(map(len, self.player_ships))
        orientations = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        valid_orientations = []
        for x_orient, y_orient in orientations:
            valid = True
            # Take steps along a particular direction starting from the tile of (move_x, move_ y).
            # Number of steps is based on minimum size of a ship still in battle
            # If encountered a non water tile or outside the map at any step the orientation is invalid.
            for step in range(1, min_ship_length):
                step_position_x = move_x + (x_orient * step)
                step_position_y = move_y + (y_orient * step)
                if (not self.player_board.is_on_board(step_position_x, step_position_y)
                        or self.player_board.public_board[step_position_x][step_position_y] != self.WATER_TILE):
                    valid = False
                    break
            if valid:
                valid_orientations.append([x_orient, y_orient])
        return valid_orientations

    def move_along_orientation(self, orientation_x, orientation_y):
        """Next shot is based on previous shot and orientation selected"""
        self.move_x += orientation_x
        self.move_y += orientation_y
        return self.move_x, self.move_y

    def get_adjacent_water_tiles(self, x: int, y: int) -> list[list[int]]:
        """Returns orientations to reach the water tiles due North, South, East and West of (x,y)"""
        step_directions = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        orientations = []
        for xdir, ydir in step_directions:
            xstep = xdir + x
            ystep = ydir + y
            if self.player_board.is_on_board(xstep, ystep) and self.player_board.public_board[xstep][
                ystep] == self.WATER_TILE:
                orientations.append([xdir, ydir])
        return orientations


def main():
    print_title()
    if input("Do you need instructions (y/n)? ").lower().startswith("y"):
        print_instructions()
    while True:
        # Setup
        is_game_over = False
        enemy_board = Board(10)
        enemy_board.auto_place_ships()
        player_board = Board(10)
        player_board.place_player_ships()
        player = Player(player_board)
        AIPlayer = AIConditional(player_board)
        is_player_turn = True

        AI_hit = False
        AI_sunk = []
        AI_ship_tile = ""

        while not is_game_over:
            if is_player_turn:
                print("[PLAYER TURN]")
                print("Your fleet:")
                player_board.print_board(showShips=True)
                print("Enemy fleet:")
                enemy_board.print_board(showShips=False)
                x, y = player.get_player_action()
                hit, sunk, ship_tile, is_game_over = enemy_board.shoot(x, y)
                print(enemy_board.get_message(hit, sunk, ship_tile))
            else:
                print("[AI TURN]")
                x, y = AIPlayer.get_AI_action(AI_hit, AI_sunk, AI_ship_tile)
                print("AI shot:", x, y)
                AI_hit, AI_sunk, AI_ship_tile, is_game_over = player_board.shoot(x, y)

            is_player_turn = not is_player_turn

        # Reveal everything
        print("[Your fleet]")
        player_board.print_board(showShips=True)
        print("[Enemy fleet]")
        enemy_board.print_board(showShips=True)
        if not is_player_turn:
            print("PLAYER VICTORY!")
        else:
            print("AI VICTORY!")

        if not input("Do you want to play again (y/n)? ").lower().startswith("y"):
            break
if __name__ == '__main__':
    main()