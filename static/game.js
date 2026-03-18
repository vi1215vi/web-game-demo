class TicTacToeGame {
    constructor() {
        this.board = [];
        this.currentPlayer = 'X';
        this.gameOver = false;
        this.winner = null;
        this.mode = 'ai';
        this.selectedCell = null;
        this.socket = null;
        this.roomId = null;
        this.playerSymbol = null;
        this.isOnline = false;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.fetchStatus();
    }
    
    setupEventListeners() {
        const cells = document.querySelectorAll('.cell');
        cells.forEach(cell => {
            cell.addEventListener('click', () => this.handleCellClick(cell));
        });
        
        document.getElementById('reset').addEventListener('click', () => this.resetGame());
        document.getElementById('mode').addEventListener('change', (e) => this.changeMode(e.target.value));
        
        document.getElementById('create-room').addEventListener('click', () => this.createRoom());
        document.getElementById('join-room-btn').addEventListener('click', () => this.joinRoom());
        
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }
    
    initSocket() {
        if (this.socket) return;
        
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
        });
        
        this.socket.on('room_created', (data) => {
            this.roomId = data.room_id;
            this.playerSymbol = data.player_symbol;
            this.isOnline = true;
            this.updateOnlineUI();
            document.getElementById('online-status').textContent = '房间创建成功，等待对手加入...';
        });
        
        this.socket.on('room_joined', (data) => {
            this.roomId = data.room_id;
            this.playerSymbol = data.player_symbol;
            this.isOnline = true;
            this.board = data.board;
            this.currentPlayer = data.current_player;
            this.updateBoard({
                board: this.board,
                current_player: this.currentPlayer,
                game_over: false,
                winner: null,
                mode: 'online'
            });
            this.updateOnlineUI();
            document.getElementById('online-status').textContent = '成功加入房间！';
        });
        
        this.socket.on('player_joined', (data) => {
            document.getElementById('online-status').textContent = 
                `玩家 ${data.player_symbol} 加入了房间，游戏开始！`;
        });
        
        this.socket.on('player_left', (data) => {
            document.getElementById('online-status').textContent = '对手离开了房间';
        });
        
        this.socket.on('move_made', (data) => {
            this.updateBoard({
                board: data.board,
                current_player: data.current_player,
                game_over: data.game_over,
                winner: data.winner,
                mode: 'online'
            });
        });
        
        this.socket.on('game_reset', (data) => {
            this.updateBoard({
                board: data.board,
                current_player: data.current_player,
                game_over: false,
                winner: null,
                mode: 'online'
            });
            document.getElementById('online-status').textContent = '游戏已重置';
        });
        
        this.socket.on('error', (data) => {
            alert(data.message);
        });
    }
    
    createRoom() {
        this.initSocket();
        this.socket.emit('create_room');
    }
    
    joinRoom() {
        const roomId = document.getElementById('room-code-input').value.trim();
        if (!roomId) {
            alert('请输入房间号');
            return;
        }
        this.initSocket();
        this.socket.emit('join_room', { room_id: roomId });
    }
    
    handleCellClick(cell) {
        if (this.gameOver) return;
        
        if (this.isOnline && this.currentPlayer !== this.playerSymbol) {
            return;
        }
        
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        if (this.board[row] && this.board[row][col] !== '') return;
        
        if (this.isOnline) {
            this.socket.emit('make_move', { row, col });
        } else {
            this.makeMove(row, col);
        }
    }
    
    handleKeyPress(e) {
        const cells = document.querySelectorAll('.cell');
        
        switch(e.key) {
            case 'ArrowUp':
                e.preventDefault();
                this.moveSelection(-1, 0);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.moveSelection(1, 0);
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.moveSelection(0, -1);
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.moveSelection(0, 1);
                break;
            case 'Enter':
            case ' ':
                e.preventDefault();
                if (this.selectedCell) {
                    const row = parseInt(this.selectedCell.dataset.row);
                    const col = parseInt(this.selectedCell.dataset.col);
                    if (this.isOnline) {
                        if (this.currentPlayer === this.playerSymbol) {
                            this.socket.emit('make_move', { row, col });
                        }
                    } else {
                        this.makeMove(row, col);
                    }
                }
                break;
            case 'r':
            case 'R':
                this.resetGame();
                break;
            case 'm':
            case 'M':
                this.toggleMode();
                break;
        }
    }
    
    moveSelection(rowDelta, colDelta) {
        const cells = document.querySelectorAll('.cell');
        
        if (this.selectedCell === null) {
            this.selectedCell = cells[0];
        } else {
            const currentRow = parseInt(this.selectedCell.dataset.row);
            const currentCol = parseInt(this.selectedCell.dataset.col);
            
            let newRow = currentRow + rowDelta;
            let newCol = currentCol + colDelta;
            
            newRow = Math.max(0, Math.min(2, newRow));
            newCol = Math.max(0, Math.min(2, newCol));
            
            this.selectedCell = cells[newRow * 3 + newCol];
        }
        
        this.updateSelection();
    }
    
    updateSelection() {
        const cells = document.querySelectorAll('.cell');
        cells.forEach(cell => cell.classList.remove('selected'));
        
        if (this.selectedCell) {
            this.selectedCell.classList.add('selected');
        }
    }
    
    async makeMove(row, col) {
        try {
            const response = await fetch('/api/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ row, col }),
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateBoard(data);
            }
        } catch (error) {
            console.error('Error making move:', error);
        }
    }
    
    async resetGame() {
        if (this.isOnline) {
            this.socket.emit('reset_game');
            return;
        }
        
        try {
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mode: this.mode }),
            });
            
            const data = await response.json();
            this.updateBoard(data);
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    }
    
    changeMode(newMode) {
        if (this.isOnline && newMode !== 'online') {
            this.disconnectOnline();
        }
        
        this.mode = newMode;
        
        const onlineControls = document.getElementById('online-controls');
        if (newMode === 'online') {
            onlineControls.style.display = 'block';
        } else {
            onlineControls.style.display = 'none';
        }
        
        this.resetGame();
    }
    
    toggleMode() {
        const modeSelect = document.getElementById('mode');
        const modes = ['ai', 'pvp', 'online'];
        const currentIndex = modes.indexOf(this.mode);
        const nextIndex = (currentIndex + 1) % modes.length;
        this.mode = modes[nextIndex];
        modeSelect.value = this.mode;
        this.changeMode(this.mode);
    }
    
    disconnectOnline() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.isOnline = false;
        this.roomId = null;
        this.playerSymbol = null;
    }
    
    updateOnlineUI() {
        document.getElementById('room-id-display').textContent = 
            `房间号: ${this.roomId}`;
        document.getElementById('player-symbol-display').textContent = 
            `你的符号: ${this.playerSymbol}`;
    }
    
    async fetchStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            this.updateBoard(data);
        } catch (error) {
            console.error('Error fetching status:', error);
        }
    }
    
    updateBoard(data) {
        this.board = data.board;
        this.currentPlayer = data.current_player;
        this.gameOver = data.game_over;
        this.winner = data.winner;
        this.mode = data.mode;
        
        const cells = document.querySelectorAll('.cell');
        cells.forEach((cell, index) => {
            const row = Math.floor(index / 3);
            const col = index % 3;
            const value = this.board[row][col];
            
            cell.textContent = value;
            cell.className = 'cell';
            
            if (value === 'X') {
                cell.classList.add('x', 'occupied');
            } else if (value === 'O') {
                cell.classList.add('o', 'occupied');
            }
        });
        
        this.updateStatus();
        this.updateCurrentPlayer();
        
        if (this.selectedCell) {
            this.updateSelection();
        }
    }
    
    updateStatus() {
        const statusElement = document.getElementById('status');
        
        if (this.gameOver) {
            if (this.winner === 'Draw') {
                statusElement.textContent = '平局！';
            } else {
                statusElement.textContent = `玩家 ${this.winner} 获胜！`;
            }
        } else {
            statusElement.textContent = '';
        }
    }
    
    updateCurrentPlayer() {
        const playerInfo = document.querySelector('.player-info');
        const playerX = playerInfo.querySelector('.player-x');
        const playerO = playerInfo.querySelector('.player-o');
        const currentPlayerSpan = document.getElementById('current-player');
        
        playerX.style.opacity = '0.5';
        playerO.style.opacity = '0.5';
        
        if (!this.gameOver) {
            if (this.currentPlayer === 'X') {
                playerX.style.opacity = '1';
                currentPlayerSpan.textContent = '当前回合';
            } else {
                playerO.style.opacity = '1';
                currentPlayerSpan.textContent = '当前回合';
            }
        } else {
            currentPlayerSpan.textContent = '游戏结束';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new TicTacToeGame();
});
