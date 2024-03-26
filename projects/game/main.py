import numpy as np

# Game board layout
board_size = 10
board = np.zeros((board_size, board_size))

# Snakes and ladders
snakes = {
    15: 5,
    32: 10,
    47: 25,
    64: 30
}
ladders = {
    2: 12,
    7: 23,
    14: 36,
    20: 48
}

# Player movement
def roll_dice():
    return np.random.randint(1, 7)

def move_player(player_position, dice_roll):
    new_position = player_position + dice_roll

    # Check for snakes and ladders
    if new_position in snakes:
        new_position = snakes[new_position]
    elif new_position in ladders:
        new_position = ladders[new_position]

    return new_position

# Game logic
def play_game():
    # Initialize players
    players = ["Player 1", "Player 2"]
    player_positions = [0, 0]

    # Game loop
    while True:
        for player in players:
            # Roll dice and move player
            dice_roll = roll_dice()
            new_position = move_player(player_positions[players.index(player)], dice_roll)
            player_positions[players.index(player)] = new_position

            # Check for victory
            if new_position == board_size ** 2 - 1:
                print(f"{player} wins!")
                return

# User interface
def display_board(board, player_positions):
    # Display the board
    for row in range(board_size - 1, -1, -1):
        for col in range(board_size):
            if (row, col) in player_positions:
                print("P", end=" ")
            else:
                print(board[row][col], end=" ")
        print()

# Main function
def main():
    # Play the game
    play_game()

if __name__ == "__main__":
    main()