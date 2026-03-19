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

game = TicTacToe()
rooms = {}
player_rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gomoku')
def gomoku():
    return render_template('gomoku.html')

@app.route('/api/move', methods=['POST'])
def make_move():
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    success, message = game.make_move(row, col)
    
    response = {
        'success': success,
        'message': message,
        'board': game.board,
        'current_player': game.current_player,
        'game_over': game.game_over,
        'winner': game.winner
    }
    
    if success and game.mode == 'ai' and not game.game_over and game.current_player == 'O':
        result, message = game.ai_move()
        if result is not None:
            ai_row, ai_col = result
            game.board[ai_row][ai_col] = 'O'
            
            if game.check_winner():
                game.game_over = True
                game.winner = 'O'
            elif game.is_board_full():
                game.game_over = True
                game.winner = 'Draw'
            else:
                game.current_player = 'X'
            
            response['board'] = game.board
            response['current_player'] = game.current_player
            response['game_over'] = game.game_over
            response['winner'] = game.winner
    
    return jsonify(response)

@app.route('/api/reset', methods=['POST'])
def reset_game():
    data = request.json
    mode = data.get('mode', 'ai')
    game.reset(mode)
    return jsonify({
        'board': game.board,
        'current_player': game.current_player,
        'game_over': game.game_over,
        'winner': game.winner,
        'mode': mode
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'board': game.board,
        'current_player': game.current_player,
        'game_over': game.game_over,
        'winner': game.winner,
        'mode': game.mode
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
