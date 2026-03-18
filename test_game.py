import pytest
from app import TicTacToe, OnlineGameRoom

class TestTicTacToe:
    def test_init(self):
        game = TicTacToe()
        assert game.current_player == 'X'
        assert game.game_over == False
        assert game.winner == None
        assert game.mode == 'ai'
        assert game.board == [['' for _ in range(3)] for _ in range(3)]
    
    def test_make_move_valid(self):
        game = TicTacToe()
        success, message = game.make_move(0, 0)
        assert success == True
        assert game.board[0][0] == 'X'
        assert game.current_player == 'O'
    
    def test_make_move_invalid_occupied(self):
        game = TicTacToe()
        game.make_move(0, 0)
        success, message = game.make_move(0, 0)
        assert success == False
        assert message == 'Invalid move'
    
    def test_make_move_game_over(self):
        game = TicTacToe()
        game.game_over = True
        success, message = game.make_move(0, 0)
        assert success == False
        assert message == 'Invalid move'
    
    def test_check_winner_row(self):
        game = TicTacToe()
        game.board[0] = ['X', 'X', 'X']
        assert game.check_winner() == True
    
    def test_check_winner_column(self):
        game = TicTacToe()
        for i in range(3):
            game.board[i][0] = 'X'
        assert game.check_winner() == True
    
    def test_check_winner_diagonal(self):
        game = TicTacToe()
        game.board[0][0] = 'X'
        game.board[1][1] = 'X'
        game.board[2][2] = 'X'
        assert game.check_winner() == True
    
    def test_check_winner_no_winner(self):
        game = TicTacToe()
        assert game.check_winner() == False
    
    def test_is_board_full(self):
        game = TicTacToe()
        for i in range(3):
            for j in range(3):
                game.board[i][j] = 'X'
        assert game.is_board_full() == True
    
    def test_is_board_not_full(self):
        game = TicTacToe()
        assert game.is_board_full() == False
    
    def test_reset(self):
        game = TicTacToe()
        game.make_move(0, 0)
        game.reset('pvp')
        assert game.board == [['' for _ in range(3)] for _ in range(3)]
        assert game.current_player == 'X'
        assert game.game_over == False
        assert game.winner == None
        assert game.mode == 'pvp'
    
    def test_ai_move_winning(self):
        game = TicTacToe()
        game.board[0] = ['O', 'O', '']
        game.board[1] = ['X', 'X', '']
        game.board[2] = ['', '', '']
        game.current_player = 'O'
        move, message = game.ai_move()
        assert move == (0, 2)
    
    def test_ai_move_blocking(self):
        game = TicTacToe()
        game.board[0] = ['X', 'X', '']
        game.board[1] = ['O', 'O', '']
        game.board[2] = ['', '', '']
        game.current_player = 'O'
        move, message = game.ai_move()
        assert move == (0, 2)
    
    def test_ai_move_center(self):
        game = TicTacToe()
        game.current_player = 'O'
        move, message = game.ai_move()
        assert move == (1, 1)
    
    def test_game_win_row(self):
        game = TicTacToe()
        game.make_move(0, 0)
        game.make_move(1, 0)
        game.make_move(0, 1)
        game.make_move(1, 1)
        success, message = game.make_move(0, 2)
        assert success == True
        assert game.game_over == True
        assert game.winner == 'X'
    
    def test_game_draw(self):
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

class TestOnlineGameRoom:
    def test_init(self):
        room = OnlineGameRoom('test_room')
        assert room.room_id == 'test_room'
        assert room.players == []
        assert room.current_player == 'X'
        assert room.game_over == False
        assert room.winner == None
    
    def test_add_player(self):
        room = OnlineGameRoom('test_room')
        assert room.add_player('player1') == True
        assert 'player1' in room.players
        assert room.add_player('player2') == True
        assert 'player2' in room.players
        assert room.add_player('player3') == False
    
    def test_add_duplicate_player(self):
        room = OnlineGameRoom('test_room')
        room.add_player('player1')
        assert room.add_player('player1') == False
    
    def test_remove_player(self):
        room = OnlineGameRoom('test_room')
        room.add_player('player1')
        room.remove_player('player1')
        assert 'player1' not in room.players
    
    def test_make_move_valid(self):
        room = OnlineGameRoom('test_room')
        room.add_player('player1')
        room.add_player('player2')
        success, message = room.make_move('player1', 0, 0)
        assert success == True
        assert room.board[0][0] == 'X'
        assert room.current_player == 'O'
    
    def test_make_move_not_player(self):
        room = OnlineGameRoom('test_room')
        success, message = room.make_move('player1', 0, 0)
        assert success == False
        assert message == 'Not a player'
    
    def test_make_move_not_turn(self):
        room = OnlineGameRoom('test_room')
        room.add_player('player1')
        room.add_player('player2')
        success, message = room.make_move('player2', 0, 0)
        assert success == False
        assert message == 'Not your turn'
    
    def test_make_move_occupied(self):
        room = OnlineGameRoom('test_room')
        room.add_player('player1')
        room.add_player('player2')
        room.make_move('player1', 0, 0)
        success, message = room.make_move('player2', 0, 0)
        assert success == False
        assert message == 'Position occupied'
    
    def test_make_move_game_over(self):
        room = OnlineGameRoom('test_room')
        room.add_player('player1')
        room.add_player('player2')
        room.game_over = True
        success, message = room.make_move('player1', 0, 0)
        assert success == False
        assert message == 'Game over'
    
    def test_online_game_win(self):
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
    
    def test_online_game_draw(self):
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
    
    def test_reset(self):
        room = OnlineGameRoom('test_room')
        room.add_player('player1')
        room.add_player('player2')
        room.make_move('player1', 0, 0)
        room.reset()
        assert room.board == [['' for _ in range(3)] for _ in range(3)]
        assert room.current_player == 'X'
        assert room.game_over == False
        assert room.winner == None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
