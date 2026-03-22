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
        this.cellSize = 37.14;
        this.margin = 20;
        
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
        
        // 创建棋盘背景点击层
        const clickLayer = document.createElement('div');
        clickLayer.className = 'click-layer';
        clickLayer.style.position = 'absolute';
        clickLayer.style.top = '0';
        clickLayer.style.left = '0';
        clickLayer.style.width = '100%';
        clickLayer.style.height = '100%';
        clickLayer.style.zIndex = '10';
        clickLayer.style.cursor = 'pointer';
        
        // 点击事件 - 计算最近的交叉点
        clickLayer.addEventListener('click', (e) => {
            const rect = boardElement.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // 计算最近的交叉点
            const col = Math.round((x - this.margin) / this.cellSize);
            const row = Math.round((y - this.margin) / this.cellSize);
            
            // 检查是否在有效范围内
            if (row >= 0 && row < this.boardSize && col >= 0 && col < this.boardSize) {
                this.makeMove(row, col);
            }
        });
        
        // 鼠标移动事件 - 显示预选效果
        clickLayer.addEventListener('mousemove', (e) => {
            const rect = boardElement.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const col = Math.round((x - this.margin) / this.cellSize);
            const row = Math.round((y - this.margin) / this.cellSize);
            
            this.highlightPreview(row, col);
        });
        
        boardElement.appendChild(clickLayer);
        
        // 创建棋子容器
        const stonesContainer = document.createElement('div');
        stonesContainer.className = 'stones-container';
        stonesContainer.style.position = 'absolute';
        stonesContainer.style.top = '0';
        stonesContainer.style.left = '0';
        stonesContainer.style.width = '100%';
        stonesContainer.style.height = '100%';
        stonesContainer.style.zIndex = '5';
        stonesContainer.style.pointerEvents = 'none';
        this.stonesContainer = stonesContainer;
        boardElement.appendChild(stonesContainer);
        
        // 创建预览棋子元素
        const previewStone = document.createElement('div');
        previewStone.className = 'preview-stone';
        previewStone.style.position = 'absolute';
        previewStone.style.width = '28px';
        previewStone.style.height = '28px';
        previewStone.style.borderRadius = '50%';
        previewStone.style.background = 'rgba(102, 126, 234, 0.3)';
        previewStone.style.display = 'none';
        previewStone.style.zIndex = '4';
        previewStone.style.pointerEvents = 'none';
        this.previewStone = previewStone;
        boardElement.appendChild(previewStone);
    }
    
    highlightPreview(row, col) {
        if (row >= 0 && row < this.boardSize && col >= 0 && col < this.boardSize) {
            if (this.board.length > 0 && this.board[row] && this.board[row][col] === 0 && !this.gameOver) {
                const crossX = this.margin + col * this.cellSize;
                const crossY = this.margin + row * this.cellSize;
                this.previewStone.style.left = `${crossX - 14}px`;
                this.previewStone.style.top = `${crossY - 14}px`;
                this.previewStone.style.display = 'block';
            } else {
                this.previewStone.style.display = 'none';
            }
        } else {
            this.previewStone.style.display = 'none';
        }
    }
    
    setupEventListeners() {
        document.getElementById('reset').addEventListener('click', () => this.resetGame());
        document.getElementById('mode').addEventListener('change', (e) => this.changeMode(e.target.value));
        document.getElementById('difficulty').addEventListener('change', (e) => this.changeDifficulty(e.target.value));
        
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }
    
    handleKeyPress(e) {
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
                    const row = this.selectedCell.row;
                    const col = this.selectedCell.col;
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
        if (!this.selectedCell) {
            this.selectedCell = { row: 7, col: 7 };
        } else {
            let newRow = this.selectedCell.row + rowDelta;
            let newCol = this.selectedCell.col + colDelta;
            
            newRow = Math.max(0, Math.min(this.boardSize - 1, newRow));
            newCol = Math.max(0, Math.min(this.boardSize - 1, newCol));
            
            this.selectedCell = { row: newRow, col: newCol };
        }
        
        this.updateSelection();
    }
    
    updateSelection() {
        // 清除之前的选中效果
        const prevSelection = document.querySelector('.selection-marker');
        if (prevSelection) {
            prevSelection.remove();
        }
        
        if (this.selectedCell) {
            const crossX = this.margin + this.selectedCell.col * this.cellSize;
            const crossY = this.margin + this.selectedCell.row * this.cellSize;
            
            const marker = document.createElement('div');
            marker.className = 'selection-marker';
            marker.style.position = 'absolute';
            marker.style.width = '28px';
            marker.style.height = '28px';
            marker.style.borderRadius = '50%';
            marker.style.background = 'rgba(102, 126, 234, 0.4)';
            marker.style.boxShadow = '0 0 10px rgba(102, 126, 234, 0.5)';
            marker.style.left = `${crossX - 14}px`;
            marker.style.top = `${crossY - 14}px`;
            marker.style.zIndex = '3';
            marker.style.pointerEvents = 'none';
            
            document.getElementById('board').appendChild(marker);
        }
    }
    
    async makeMove(row, col) {
        if (this.gameOver) return;
        
        try {
            console.log('Making move:', row, col);
            const response = await fetch('/api/gomoku/move', {
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
            const response = await fetch('/api/gomoku/reset', {
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
            const response = await fetch('/api/gomoku/status');
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
        
        const difficultyContainer = document.getElementById('difficulty-container');
        if (this.mode === 'ai') {
            difficultyContainer.style.display = 'block';
        } else {
            difficultyContainer.style.display = 'none';
        }
        
        // 清空棋子容器
        this.stonesContainer.innerHTML = '';
        
        // 渲染所有棋子
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                const value = this.board[row][col];
                if (value !== 0) {
                    const crossX = this.margin + col * this.cellSize;
                    const crossY = this.margin + row * this.cellSize;
                    
                    const stone = document.createElement('div');
                    stone.className = `stone ${value === 1 ? 'black' : 'white'}`;
                    stone.style.left = `${crossX - 14}px`;
                    stone.style.top = `${crossY - 14}px`;
                    
                    if (this.lastMove && this.lastMove[0] === row && this.lastMove[1] === col) {
                        stone.classList.add('last-move');
                    }
                    
                    this.stonesContainer.appendChild(stone);
                }
            }
        }
        
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
