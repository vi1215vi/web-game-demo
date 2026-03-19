class GomokuGame {
    constructor() {
        this.board = [];
        this.currentPlayer = 1;
        this.gameOver = false;
        this.winner = null;
        this.mode = 'ai';
        this.difficulty = 'normal';
        this.selectedCell = null;
        this.lastMove = null;
        this.boardSize = 15;
        
        this.init();
    }
    
    init() {
        this.createBoard();
        this.setupEventListeners();
        this.fetchStatus();
    }
    
    createBoard() {
        const boardElement = document.getElementById('board');
        boardElement.innerHTML = '';
        
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.row = row;
                cell.dataset.col = col;
                // 格子位置：17px边距 + 格子偏移
                cell.style.left = `${17 + col * 35}px`;
                cell.style.top = `${17 + row * 35}px`;
                cell.addEventListener('click', () => this.handleCellClick(cell));
                boardElement.appendChild(cell);
            }
        }
    }
    
    setupEventListeners() {
        document.getElementById('reset').addEventListener('click', () => this.resetGame());
        document.getElementById('mode').addEventListener('change', (e) => this.changeMode(e.target.value));
        document.getElementById('difficulty').addEventListener('change', (e) => this.changeDifficulty(e.target.value));
        
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }
    
    handleCellClick(cell) {
        if (this.gameOver) return;
        
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        
        if (this.board.length > 0 && this.board[row] && this.board[row][col] !== 0) return;
        
        this.makeMove(row, col);
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
                    if (this.board.length > 0 && this.board[row] && this.board[row][col] === 0) {
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
            
            newRow = Math.max(0, Math.min(this.boardSize - 1, newRow));
            newCol = Math.max(0, Math.min(this.boardSize - 1, newCol));
            
            this.selectedCell = cells[newRow * this.boardSize + newCol];
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
            console.log('Making move:', row, col);
            const response = await fetch('/gomoku/api/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ row, col }),
            });
            
            const data = await response.json();
            console.log('Move response:', data);
            
            if (data.success) {
                this.updateBoard(data);
            } else {
                console.error('Move failed:', data.message);
            }
        } catch (error) {
            console.error('Error making move:', error);
        }
    }
    
    async resetGame() {
        try {
            const response = await fetch('/gomoku/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mode: this.mode, difficulty: this.difficulty }),
            });
            
            const data = await response.json();
            this.updateBoard(data);
        } catch (error) {
            console.error('Error resetting game:', error);
        }
    }
    
    changeMode(newMode) {
        this.mode = newMode;
        // 根据模式显示/隐藏难度选择
        const difficultyContainer = document.getElementById('difficulty-container');
        if (newMode === 'ai') {
            difficultyContainer.style.display = 'block';
        } else {
            difficultyContainer.style.display = 'none';
        }
        this.resetGame();
    }
    
    changeDifficulty(newDifficulty) {
        this.difficulty = newDifficulty;
        this.resetGame();
    }
    
    toggleMode() {
        const modeSelect = document.getElementById('mode');
        this.mode = this.mode === 'ai' ? 'pvp' : 'ai';
        modeSelect.value = this.mode;
        // 根据模式显示/隐藏难度选择
        const difficultyContainer = document.getElementById('difficulty-container');
        if (this.mode === 'ai') {
            difficultyContainer.style.display = 'block';
        } else {
            difficultyContainer.style.display = 'none';
        }
        this.resetGame();
    }
    
    async fetchStatus() {
        try {
            const response = await fetch('/gomoku/api/status');
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
        if (data.difficulty) {
            this.difficulty = data.difficulty;
        }
        this.lastMove = data.last_move;
        
        // 更新难度选择显示状态
        const difficultyContainer = document.getElementById('difficulty-container');
        if (this.mode === 'ai') {
            difficultyContainer.style.display = 'block';
        } else {
            difficultyContainer.style.display = 'none';
        }
        
        const cells = document.querySelectorAll('.cell');
        cells.forEach((cell, index) => {
            const row = Math.floor(index / this.boardSize);
            const col = index % this.boardSize;
            const value = this.board[row][col];
            
            cell.innerHTML = '';
            cell.className = 'cell';
            
            if (value !== 0) {
                cell.classList.add('occupied');
                const stone = document.createElement('div');
                stone.className = `stone ${value === 1 ? 'black' : 'white'}`;
                
                if (this.lastMove && this.lastMove[0] === row && this.lastMove[1] === col) {
                    stone.classList.add('last-move');
                }
                
                cell.appendChild(stone);
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
            if (this.winner === 0) {
                statusElement.textContent = '平局！';
            } else {
                const playerName = this.winner === 1 ? '黑棋' : '白棋';
                statusElement.textContent = `${playerName} 获胜！`;
            }
        } else {
            statusElement.textContent = '';
        }
    }
    
    updateCurrentPlayer() {
        const playerInfo = document.querySelector('.player-info');
        const playerBlack = playerInfo.querySelector('.player-black');
        const playerWhite = playerInfo.querySelector('.player-white');
        const currentPlayerSpan = document.getElementById('current-player');
        
        playerBlack.style.opacity = '0.5';
        playerWhite.style.opacity = '0.5';
        
        if (!this.gameOver) {
            if (this.currentPlayer === 1) {
                playerBlack.style.opacity = '1';
                currentPlayerSpan.textContent = '当前回合';
            } else {
                playerWhite.style.opacity = '1';
                currentPlayerSpan.textContent = '当前回合';
            }
        } else {
            currentPlayerSpan.textContent = '游戏结束';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new GomokuGame();
});
