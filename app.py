from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

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
    
    def ai_move(self):
        if self.game_over:
            return None, 'Game over'
        
        available_moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == '':
                    available_moves.append((i, j))
        
        if not available_moves:
            return None, 'No moves available'
        
        for move in available_moves:
            self.board[move[0]][move[1]] = 'O'
            if self.check_winner():
                self.board[move[0]][move[1]] = ''
                return move, 'AI wins!'
            self.board[move[0]][move[1]] = ''
        
        for move in available_moves:
            self.board[move[0]][move[1]] = 'X'
            if self.check_winner():
                self.board[move[0]][move[1]] = ''
                return move, 'AI blocked player'
            self.board[move[0]][move[1]] = ''
        
        if (1, 1) in available_moves:
            return (1, 1), 'AI took center'
        
        move = random.choice(available_moves)
        return move, 'AI made random move'
    
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

class Gomoku:
    def __init__(self, board_size=15):
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.mode = 'ai'
        self.difficulty = 'normal'
        self.last_move = None
    
    def make_move(self, row, col):
        if self.game_over:
            return False, 'Game over'
        
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False, 'Invalid position'
        
        if self.board[row][col] != 0:
            return False, 'Position occupied'
        
        self.board[row][col] = self.current_player
        self.last_move = (row, col)
        
        if self.check_winner(row, col):
            self.game_over = True
            self.winner = self.current_player
            return True, f'Player {self.current_player} wins!'
        
        if self.is_board_full():
            self.game_over = True
            self.winner = 0
            return True, 'Draw!'
        
        self.current_player = 2 if self.current_player == 1 else 1
        return True, 'Move successful'
    
    def check_winner(self, row, col):
        player = self.board[row][col]
        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1)
        ]
        
        for dx, dy in directions:
            count = 1
            for direction in [1, -1]:
                for i in range(1, 5):
                    new_row = row + direction * i * dx
                    new_col = col + direction * i * dy
                    if (0 <= new_row < self.board_size and 
                        0 <= new_col < self.board_size and 
                        self.board[new_row][new_col] == player):
                        count += 1
                    else:
                        break
            if count >= 5:
                return True
        return False
    
    def is_board_full(self):
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    def evaluate_position(self, row, col, player):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            consecutive = 0
            open_ends = 0
            
            for direction in [1, -1]:
                for i in range(1, 5):
                    new_row = row + direction * i * dx
                    new_col = col + direction * i * dy
                    if (0 <= new_row < self.board_size and 
                        0 <= new_col < self.board_size):
                        if self.board[new_row][new_col] == player:
                            consecutive += 1
                        elif self.board[new_row][new_col] == 0:
                            open_ends += 1
                            break
                        else:
                            break
            
            if consecutive >= 4:
                score += 10000
            elif consecutive == 3 and open_ends >= 1:
                score += 1000
            elif consecutive == 2 and open_ends >= 2:
                score += 100
            elif consecutive == 1 and open_ends >= 2:
                score += 10
        
        return score
    
    def ai_move(self):
        if self.game_over:
            return None, 'Game over'
        
        available_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0:
                    available_moves.append((i, j))
        
        if not available_moves:
            return None, 'No moves available'
        
        if self.difficulty == 'easy':
            return self._ai_move_easy(available_moves)
        elif self.difficulty == 'normal':
            return self._ai_move_normal(available_moves)
        elif self.difficulty == 'hard':
            return self._ai_move_hard(available_moves)
        elif self.difficulty == 'master':
            return self._ai_move_master(available_moves)
        else:
            return self._ai_move_normal(available_moves)
    
    def _ai_move_easy(self, available_moves):
        if random.random() < 0.3:
            for move in available_moves:
                row, col = move
                self.board[row][col] = 1
                if self.check_winner(row, col):
                    self.board[row][col] = 0
                    return move, 'AI防守'
                self.board[row][col] = 0
        
        return random.choice(available_moves), 'AI随机落子'
    
    def _ai_move_normal(self, available_moves):
        best_move = None
        best_score = -float('inf')
        
        for move in available_moves:
            row, col = move
            
            self.board[row][col] = 2
            if self.check_winner(row, col):
                self.board[row][col] = 0
                return move, 'AI获胜!'
            self.board[row][col] = 0
            
            self.board[row][col] = 1
            if self.check_winner(row, col):
                self.board[row][col] = 0
                return move, 'AI防守'
            self.board[row][col] = 0
            
            score = self.evaluate_position(row, col, 2) * 0.6
            score -= self.evaluate_position(row, col, 1) * 0.4
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else random.choice(available_moves), 'AI落子'
    
    def _ai_move_hard(self, available_moves):
        best_move = None
        best_score = -float('inf')
        
        for move in available_moves:
            row, col = move
            
            self.board[row][col] = 2
            if self.check_winner(row, col):
                self.board[row][col] = 0
                return move, 'AI获胜!'
            self.board[row][col] = 0
            
            self.board[row][col] = 1
            if self.check_winner(row, col):
                self.board[row][col] = 0
                return move, 'AI防守'
            self.board[row][col] = 0
            
            score = self._evaluate_move_deep(row, col, 2)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else random.choice(available_moves), 'AI落子'
    
    def _ai_move_master(self, available_moves):
        best_move = None
        best_score = -float('inf')
        
        center = self.board_size // 2
        
        for move in available_moves:
            row, col = move
            
            self.board[row][col] = 2
            if self.check_winner(row, col):
                self.board[row][col] = 0
                return move, 'AI获胜!'
            self.board[row][col] = 0
            
            self.board[row][col] = 1
            if self.check_winner(row, col):
                self.board[row][col] = 0
                return move, 'AI防守'
            self.board[row][col] = 0
            
            score = self._evaluate_move_master(row, col)
            
            distance_to_center = abs(row - center) + abs(col - center)
            score += (self.board_size - distance_to_center) * 10
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move if best_move else random.choice(available_moves), 'AI落子'
    
    def _evaluate_move_deep(self, row, col, player):
        original_value = self.board[row][col]
        
        self.board[row][col] = player
        
        score = self.evaluate_position(row, col, player) * 1.2
        score -= self.evaluate_position(row, col, 3 - player) * 0.8
        
        opponent_best = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0:
                    threat = self.evaluate_position(i, j, 3 - player)
                    if threat > opponent_best:
                        opponent_best = threat
        
        self.board[row][col] = original_value
        
        score -= opponent_best * 0.5
        
        return score
    
    def _evaluate_move_master(self, row, col):
        original_value = self.board[row][col]
        
        attack_score = self.evaluate_position(row, col, 2)
        defense_score = self.evaluate_position(row, col, 1)
        
        score = attack_score * 1.5 + defense_score * 1.0
        
        self.board[row][col] = 2
        
        live_threes = self._count_live_threes(2)
        live_fours = self._count_live_fours(2)
        
        self.board[row][col] = original_value
        
        score += live_threes * 500
        score += live_fours * 5000
        
        return score
    
    def _count_live_threes(self, player):
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == player:
                    for dx, dy in directions:
                        consecutive = 1
                        empty_ends = 0
                        
                        for direction in [1, -1]:
                            for step in range(1, 4):
                                ni, nj = i + direction * step * dx, j + direction * step * dy
                                if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                                    if self.board[ni][nj] == player:
                                        consecutive += 1
                                    elif self.board[ni][nj] == 0:
                                        empty_ends += 1
                                        break
                                    else:
                                        break
        
        return count // 2
    
    def _count_live_fours(self, player):
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == player:
                    for dx, dy in directions:
                        consecutive = 1
                        empty_ends = 0
                        
                        for direction in [1, -1]:
                            for step in range(1, 5):
                                ni, nj = i + direction * step * dx, j + direction * step * dy
                                if 0 <= ni < self.board_size and 0 <= nj < self.board_size:
                                    if self.board[ni][nj] == player:
                                        consecutive += 1
                                    elif self.board[ni][nj] == 0:
                                        empty_ends += 1
                                        break
                                    else:
                                        break
        
        return count // 2
    
    def reset(self, mode='ai', difficulty='normal'):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.mode = mode
        self.difficulty = difficulty
        self.last_move = None

tictactoe_game = TicTacToe()
gomoku_game = Gomoku()
rooms = {}
player_rooms = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/tictactoe')
def tictactoe_index():
    return render_template('index.html')

@app.route('/gomoku')
def gomoku_index():
    return render_template('gomoku.html')

@app.route('/api/tictactoe/move', methods=['POST'])
def tictactoe_move():
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    success, message = tictactoe_game.make_move(row, col)
    
    response = {
        'success': success,
        'message': message,
        'board': tictactoe_game.board,
        'current_player': tictactoe_game.current_player,
        'game_over': tictactoe_game.game_over,
        'winner': tictactoe_game.winner
    }
    
    if success and tictactoe_game.mode == 'ai' and not tictactoe_game.game_over and tictactoe_game.current_player == 'O':
        result, message = tictactoe_game.ai_move()
        if result is not None:
            ai_row, ai_col = result
            tictactoe_game.board[ai_row][ai_col] = 'O'
            
            if tictactoe_game.check_winner():
                tictactoe_game.game_over = True
                tictactoe_game.winner = 'O'
            elif tictactoe_game.is_board_full():
                tictactoe_game.game_over = True
                tictactoe_game.winner = 'Draw'
            else:
                tictactoe_game.current_player = 'X'
            
            response['board'] = tictactoe_game.board
            response['current_player'] = tictactoe_game.current_player
            response['game_over'] = tictactoe_game.game_over
            response['winner'] = tictactoe_game.winner
    
    return jsonify(response)

@app.route('/api/tictactoe/reset', methods=['POST'])
def tictactoe_reset():
    data = request.json
    mode = data.get('mode', 'ai')
    tictactoe_game.reset(mode)
    return jsonify({
        'board': tictactoe_game.board,
        'current_player': tictactoe_game.current_player,
        'game_over': tictactoe_game.game_over,
        'winner': tictactoe_game.winner,
        'mode': mode
    })

@app.route('/api/tictactoe/status', methods=['GET'])
def tictactoe_status():
    return jsonify({
        'board': tictactoe_game.board,
        'current_player': tictactoe_game.current_player,
        'game_over': tictactoe_game.game_over,
        'winner': tictactoe_game.winner,
        'mode': tictactoe_game.mode
    })

@app.route('/api/gomoku/move', methods=['POST'])
def gomoku_move():
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    success, message = gomoku_game.make_move(row, col)
    
    response = {
        'success': success,
        'message': message,
        'board': gomoku_game.board,
        'current_player': gomoku_game.current_player,
        'game_over': gomoku_game.game_over,
        'winner': gomoku_game.winner,
        'last_move': gomoku_game.last_move
    }
    
    if success and gomoku_game.mode == 'ai' and not gomoku_game.game_over and gomoku_game.current_player == 2:
        result, message = gomoku_game.ai_move()
        if result is not None:
            ai_row, ai_col = result
            gomoku_game.make_move(ai_row, ai_col)
            response['board'] = gomoku_game.board
            response['current_player'] = gomoku_game.current_player
            response['game_over'] = gomoku_game.game_over
            response['winner'] = gomoku_game.winner
            response['last_move'] = gomoku_game.last_move
    
    return jsonify(response)

@app.route('/api/gomoku/reset', methods=['POST'])
def gomoku_reset():
    data = request.json
    mode = data.get('mode', 'ai')
    difficulty = data.get('difficulty', 'normal')
    gomoku_game.reset(mode, difficulty)
    return jsonify({
        'board': gomoku_game.board,
        'current_player': gomoku_game.current_player,
        'game_over': gomoku_game.game_over,
        'winner': gomoku_game.winner,
        'mode': mode,
        'difficulty': difficulty,
        'last_move': None
    })

@app.route('/api/gomoku/status', methods=['GET'])
def gomoku_status():
    return jsonify({
        'board': gomoku_game.board,
        'current_player': gomoku_game.current_player,
        'game_over': gomoku_game.game_over,
        'winner': gomoku_game.winner,
        'mode': gomoku_game.mode,
        'last_move': gomoku_game.last_move
    })

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    player_id = request.sid
    if player_id in player_rooms:
        room_id = player_rooms[player_id]
        if room_id in rooms:
            rooms[room_id].remove_player(player_id)
            emit('player_left', {'player_id': player_id}, room=room_id)
        del player_rooms[player_id]

@socketio.on('create_room')
def handle_create_room(data=None):
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = OnlineGameRoom(room_id)
    join_room(room_id)
    
    player_id = request.sid
    rooms[room_id].add_player(player_id)
    player_rooms[player_id] = room_id
    
    emit('room_created', {
        'room_id': room_id,
        'player_id': player_id,
        'player_symbol': 'X'
    })

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('room_id')
    player_id = request.sid
    
    if room_id not in rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = rooms[room_id]
    
    if len(room.players) >= 2:
        emit('error', {'message': 'Room is full'})
        return
    
    join_room(room_id)
    room.add_player(player_id)
    player_rooms[player_id] = room_id
    
    player_symbol = 'O' if len(room.players) == 2 else 'X'
    
    emit('room_joined', {
        'room_id': room_id,
        'player_id': player_id,
        'player_symbol': player_symbol,
        'board': room.board,
        'current_player': room.current_player
    })
    
    emit('player_joined', {
        'player_id': player_id,
        'player_symbol': player_symbol
    }, room=room_id, include_self=False)

@socketio.on('make_move')
def handle_make_move(data=None):
    player_id = request.sid
    room_id = player_rooms.get(player_id)
    
    if not room_id or room_id not in rooms:
        emit('error', {'message': 'Not in a room'})
        return
    
    room = rooms[room_id]
    row = data.get('row')
    col = data.get('col')
    
    success, message = room.make_move(player_id, row, col)
    
    if success:
        emit('move_made', {
            'row': row,
            'col': col,
            'player_symbol': room.board[row][col],
            'board': room.board,
            'current_player': room.current_player,
            'game_over': room.game_over,
            'winner': room.winner
        }, room=room_id)
    else:
        emit('error', {'message': message})

@socketio.on('reset_game')
def handle_reset_game(data=None):
    player_id = request.sid
    room_id = player_rooms.get(player_id)
    
    if room_id and room_id in rooms:
        room = rooms[room_id]
        room.reset()
        
        emit('game_reset', {
            'board': room.board,
            'current_player': room.current_player
        }, room=room_id)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
