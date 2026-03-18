import random

class TicTacToe:
    def __init__(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.mode = 'ai'
    
    def make_move(self, row, col):
        if self.game_over or self.board[row][col] != '':
            return False, 'Invalid move'
        
        self.board[row][col] = self.current_player
        
        if self.check_winner():
            self.game_over = True
            self.winner = self.current_player
            return True, f'Player {self.current_player} wins!'
        
        if self.is_board_full():
            self.game_over = True
            self.winner = 'Draw'
            return True, 'It\'s a draw!'
        
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True, 'Move successful'
    
    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return True
        
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return True
        
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return True
        
        return False
    
    def is_board_full(self):
        for row in self.board:
            if '' in row:
                return False
        return True
    
    def reset(self, mode='ai'):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.mode = mode

class OnlineGameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.spectators = []
    
    def add_player(self, player_id):
        if len(self.players) < 2 and player_id not in self.players:
            self.players.append(player_id)
            return True
        return False
    
    def remove_player(self, player_id):
        if player_id in self.players:
            self.players.remove(player_id)
    
    def make_move(self, player_id, row, col):
        if self.game_over:
            return False, 'Game over'
        
        if player_id not in self.players:
            return False, 'Not a player'
        
        player_index = self.players.index(player_id)
        player_symbol = 'X' if player_index == 0 else 'O'
        
        if player_symbol != self.current_player:
            return False, 'Not your turn'
        
        if self.board[row][col] != '':
            return False, 'Position occupied'
        
        self.board[row][col] = player_symbol
        
        if self.check_winner():
            self.game_over = True
            self.winner = player_symbol
            return True, f'Player {player_symbol} wins!'
        
        if self.is_board_full():
            self.game_over = True
            self.winner = 'Draw'
            return True, 'Draw!'
        
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True, 'Move successful'
    
    def check_winner(self):
        for row in self.board:
            if row[0] == row[1] == row[2] != '':
                return True
        
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != '':
                return True
        
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != '':
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != '':
            return True
        
        return False
    
    def is_board_full(self):
        for row in self.board:
            if '' in row:
                return False
        return True
    
    def reset(self):
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None

def test_tictactoe_init():
    game = TicTacToe()
    assert game.current_player == 'X'
    assert game.game_over == False
    assert game.winner == None
    assert game.mode == 'ai'
    assert game.board == [['' for _ in range(3)] for _ in range(3)]
    print('✓ test_tictactoe_init passed')

def test_make_move_valid():
    game = TicTacToe()
    success, message = game.make_move(0, 0)
    assert success == True
    assert game.board[0][0] == 'X'
    assert game.current_player == 'O'
    print('✓ test_make_move_valid passed')

def test_make_move_invalid_occupied():
    game = TicTacToe()
    game.make_move(0, 0)
    success, message = game.make_move(0, 0)
    assert success == False
    assert message == 'Invalid move'
    print('✓ test_make_move_invalid_occupied passed')

def test_make_move_game_over():
    game = TicTacToe()
    game.game_over = True
    success, message = game.make_move(0, 0)
    assert success == False
    assert message == 'Invalid move'
    print('✓ test_make_move_game_over passed')

def test_check_winner_row():
    game = TicTacToe()
    game.board[0] = ['X', 'X', 'X']
    assert game.check_winner() == True
    print('✓ test_check_winner_row passed')

def test_check_winner_column():
    game = TicTacToe()
    for i in range(3):
        game.board[i][0] = 'X'
    assert game.check_winner() == True
    print('✓ test_check_winner_column passed')

def test_check_winner_diagonal():
    game = TicTacToe()
    game.board[0][0] = 'X'
    game.board[1][1] = 'X'
    game.board[2][2] = 'X'
    assert game.check_winner() == True
    print('✓ test_check_winner_diagonal passed')

def test_check_winner_no_winner():
    game = TicTacToe()
    assert game.check_winner() == False
    print('✓ test_check_winner_no_winner passed')

def test_is_board_full():
    game = TicTacToe()
    for i in range(3):
        for j in range(3):
            game.board[i][j] = 'X'
    assert game.is_board_full() == True
    print('✓ test_is_board_full passed')

def test_is_board_not_full():
    game = TicTacToe()
    assert game.is_board_full() == False
    print('✓ test_is_board_not_full passed')

def test_reset():
    game = TicTacToe()
    game.make_move(0, 0)
    game.reset('pvp')
    assert game.board == [['' for _ in range(3)] for _ in range(3)]
    assert game.current_player == 'X'
    assert game.game_over == False
    assert game.winner == None
    assert game.mode == 'pvp'
    print('✓ test_reset passed')

def test_game_win_row():
    game = TicTacToe()
    game.make_move(0, 0)
    game.make_move(1, 0)
    game.make_move(0, 1)
    game.make_move(1, 1)
    success, message = game.make_move(0, 2)
    assert success == True
    assert game.game_over == True
    assert game.winner == 'X'
    print('✓ test_game_win_row passed')

def test_game_draw():
    game = TicTacToe()
    moves = [
        (0, 0), (0, 1), (0, 2),
        (1, 1), (1, 0), (1, 2),
        (2, 1), (2, 0), (2, 2)
    ]
    for move in moves:
        game.make_move(*move)
    assert game.game_over == True
    assert game.winner == 'Draw'
    print('✓ test_game_draw passed')

def test_online_room_init():
    room = OnlineGameRoom('test_room')
    assert room.room_id == 'test_room'
    assert room.players == []
    assert room.current_player == 'X'
    assert room.game_over == False
    assert room.winner == None
    print('✓ test_online_room_init passed')

def test_add_player():
    room = OnlineGameRoom('test_room')
    assert room.add_player('player1') == True
    assert 'player1' in room.players
    assert room.add_player('player2') == True
    assert 'player2' in room.players
    assert room.add_player('player3') == False
    print('✓ test_add_player passed')

def test_add_duplicate_player():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    assert room.add_player('player1') == False
    print('✓ test_add_duplicate_player passed')

def test_remove_player():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    room.remove_player('player1')
    assert 'player1' not in room.players
    print('✓ test_remove_player passed')

def test_online_make_move_valid():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    room.add_player('player2')
    success, message = room.make_move('player1', 0, 0)
    assert success == True
    assert room.board[0][0] == 'X'
    assert room.current_player == 'O'
    print('✓ test_online_make_move_valid passed')

def test_online_make_move_not_player():
    room = OnlineGameRoom('test_room')
    success, message = room.make_move('player1', 0, 0)
    assert success == False
    assert message == 'Not a player'
    print('✓ test_online_make_move_not_player passed')

def test_online_make_move_not_turn():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    room.add_player('player2')
    success, message = room.make_move('player2', 0, 0)
    assert success == False
    assert message == 'Not your turn'
    print('✓ test_online_make_move_not_turn passed')

def test_online_make_move_occupied():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    room.add_player('player2')
    room.make_move('player1', 0, 0)
    success, message = room.make_move('player2', 0, 0)
    assert success == False
    assert message == 'Position occupied'
    print('✓ test_online_make_move_occupied passed')

def test_online_game_win():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    room.add_player('player2')
    room.make_move('player1', 0, 0)
    room.make_move('player2', 1, 0)
    room.make_move('player1', 0, 1)
    room.make_move('player2', 1, 1)
    success, message = room.make_move('player1', 0, 2)
    assert success == True
    assert room.game_over == True
    assert room.winner == 'X'
    print('✓ test_online_game_win passed')

def test_online_game_draw():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    room.add_player('player2')
    moves = [
        ('player1', 0, 0), ('player2', 0, 1), ('player1', 0, 2),
        ('player2', 1, 1), ('player1', 1, 0), ('player2', 1, 2),
        ('player1', 2, 1), ('player2', 2, 0), ('player1', 2, 2)
    ]
    for player, row, col in moves:
        room.make_move(player, row, col)
    assert room.game_over == True
    assert room.winner == 'Draw'
    print('✓ test_online_game_draw passed')

def test_online_reset():
    room = OnlineGameRoom('test_room')
    room.add_player('player1')
    room.add_player('player2')
    room.make_move('player1', 0, 0)
    room.reset()
    assert room.board == [['' for _ in range(3)] for _ in range(3)]
    assert room.current_player == 'X'
    assert room.game_over == False
    assert room.winner == None
    print('✓ test_online_reset passed')

if __name__ == '__main__':
    print('Running tests...\n')
    
    test_tictactoe_init()
    test_make_move_valid()
    test_make_move_invalid_occupied()
    test_make_move_game_over()
    test_check_winner_row()
    test_check_winner_column()
    test_check_winner_diagonal()
    test_check_winner_no_winner()
    test_is_board_full()
    test_is_board_not_full()
    test_reset()
    test_game_win_row()
    test_game_draw()
    
    test_online_room_init()
    test_add_player()
    test_add_duplicate_player()
    test_remove_player()
    test_online_make_move_valid()
    test_online_make_move_not_player()
    test_online_make_move_not_turn()
    test_online_make_move_occupied()
    test_online_game_win()
    test_online_game_draw()
    test_online_reset()
    
    print('\n✓ All tests passed!')
