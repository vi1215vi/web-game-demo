from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

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
                        
                        if consecutive == 3 and empty_ends >= 2:
                            count += 1
        
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
                        
                        if consecutive == 4 and empty_ends >= 2:
                            count += 1
        
        return count // 2
    
    def get_best_opponent_score(self):
        best_score = 0
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0:
                    score = self.evaluate_position(i, j, 1)
                    if score > best_score:
                        best_score = score
        return best_score
    
    def reset(self, mode='ai', difficulty='normal'):
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = None
        self.mode = mode
        self.difficulty = difficulty
        self.last_move = None

game = Gomoku()

@app.route('/')
def index():
    return render_template('gomoku.html')

@app.route('/gomoku')
def gomoku_index():
    return render_template('gomoku.html')

@app.route('/gomoku/api/move', methods=['POST'])
def handle_move():
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    print(f'Received move request: row={row}, col={col}, current_player={game.current_player}')
    
    black_count_before = sum(row.count(1) for row in game.board)
    white_count_before = sum(row.count(2) for row in game.board)
    print(f'Before move - Black: {black_count_before}, White: {white_count_before}')
    
    success, message = game.make_move(row, col)
    
    black_count_after = sum(row.count(1) for row in game.board)
    white_count_after = sum(row.count(2) for row in game.board)
    print(f'After player move - Black: {black_count_after}, White: {white_count_after}')
    
    print(f'Move result: success={success}, message={message}, current_player={game.current_player}')
    
    response = {
        'success': success,
        'message': message,
        'board': game.board,
        'current_player': game.current_player,
        'game_over': game.game_over,
        'winner': game.winner,
        'last_move': game.last_move
    }
    
    if success and game.mode == 'ai' and not game.game_over and game.current_player == 2:
        print('AI is making move...')
        result, message = game.ai_move()
        print(f'AI move result: {result}, message: {message}')
        if result is not None:
            ai_row, ai_col = result
            game.make_move(ai_row, ai_col)
            black_count_final = sum(row.count(1) for row in game.board)
            white_count_final = sum(row.count(2) for row in game.board)
            print(f'After AI move - Black: {black_count_final}, White: {white_count_final}')
            response['board'] = game.board
            response['current_player'] = game.current_player
            response['game_over'] = game.game_over
            response['winner'] = game.winner
            response['last_move'] = game.last_move
    
    return jsonify(response)

@app.route('/gomoku/api/reset', methods=['POST'])
def reset_game():
    data = request.json
    mode = data.get('mode', 'ai')
    difficulty = data.get('difficulty', 'normal')
    game.reset(mode, difficulty)
    return jsonify({
        'board': game.board,
        'current_player': game.current_player,
        'game_over': game.game_over,
        'winner': game.winner,
        'mode': mode,
        'difficulty': difficulty,
        'last_move': None
    })

@app.route('/gomoku/api/status', methods=['GET'])
def get_status():
    return jsonify({
        'board': game.board,
        'current_player': game.current_player,
        'game_over': game.game_over,
        'winner': game.winner,
        'mode': game.mode,
        'last_move': game.last_move
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
