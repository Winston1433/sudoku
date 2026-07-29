const express = require('express');
const http = require('http');
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// 設定靜態檔案資料夾
app.use(express.static('public'));

// 簡單的數獨題目產生器
function emptyBoard() { return Array.from({length: 9}, () => Array(9).fill(0)); }
function isValid(board, row, col, num) {
  for (let i = 0; i < 9; i++) if (board[row][i] === num || board[i][col] === num) return false;
  const br = Math.floor(row / 3) * 3, bc = Math.floor(col / 3) * 3;
  for (let r = br; r < br + 3; r++) for (let c = bc; c < bc + 3; c++) if (board[r][c] === num) return false;
  return true;
}
function findEmpty(board) {
  for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) if (board[r][c] === 0) return [r, c];
  return null;
}
function solve(board) {
  const empty = findEmpty(board);
  if (!empty) return true;
  const [row, col] = empty;
  let nums = [1,2,3,4,5,6,7,8,9].sort(() => Math.random() - 0.5);
  for (const num of nums) {
    if (isValid(board, row, col, num)) {
      board[row][col] = num;
      if (solve(board)) return true;
      board[row][col] = 0;
    }
  }
  return false;
}
function generateServerPuzzle() {
  const solution = emptyBoard();
  solve(solution);
  const puzzle = solution.map(row => row.slice());
  let removed = 0;
  while (removed < 35) {
    let r = Math.floor(Math.random() * 9);
    let c = Math.floor(Math.random() * 9);
    if (puzzle[r][c] !== 0) {
      puzzle[r][c] = 0;
      removed++;
    }
  }
  return { puzzle, solution };
}

const rooms = {};

io.on('connection', (socket) => {
  console.log('連線成功！玩家 ID: ', socket.id);

  // 1. 建立房間
  socket.on('create_room', () => {
    const roomId = Math.floor(1000 + Math.random() * 9000).toString();
    rooms[roomId] = {
      players: [socket.id],
      gameData: generateServerPuzzle(),
      started: false,   // 遊戲是否已經正式開始（雙人到齊）
      gameOver: false    // 遊戲是否已經分出勝負，避免重複判定
    };
    socket.join(roomId);
    socket.emit('room_joined', { roomId });
    console.log(`玩家 ${socket.id} 建立了房間 ${roomId}`);
  });

  // 2. 加入房間
  socket.on('join_room', (data) => {
    const { roomId } = data;
    if (rooms[roomId]) {
      if (rooms[roomId].players.length >= 2) {
        socket.emit('error_msg', '這個房間已經滿人了！');
        return;
      }
      rooms[roomId].players.push(socket.id);
      socket.join(roomId);
      socket.emit('room_joined', { roomId });
      console.log(`玩家 ${socket.id} 加入了房間 ${roomId}`);

      // 雙人到齊，正式開始對戰
      rooms[roomId].started = true;
      io.to(roomId).emit('start_game', rooms[roomId].gameData);
    } else {
      socket.emit('error_msg', '找不到此房間代碼，請重新確認！');
    }
  });

  // 3. 接收玩家進度更新
  socket.on('update_progress', (data) => {
    const { roomId, progress, mistakes } = data;
    if (roomId && rooms[roomId]) {
      socket.to(roomId).emit('opponent_update', { progress, mistakes });
    }
  });

  // 4. 判定某一方獲勝（正常解完）
  socket.on('win_game', (data) => {
    const { roomId } = data;
    const room = rooms[roomId];
    if (room && !room.gameOver) {
      room.gameOver = true;
      io.to(roomId).emit('game_over', { winner: socket.id, reason: 'solved' });
    }
  });

  // 5. 玩家斷線或離開房間處理
  socket.on('disconnect', () => {
    console.log('玩家離開了，ID: ', socket.id);
    for (const roomId in rooms) {
      const room = rooms[roomId];
      if (!room.players.includes(socket.id)) continue;

      // 只有「遊戲已經正式開始」且「尚未分出勝負」時，才判定對手獲勝
      if (room.started && !room.gameOver) {
        const opponentId = room.players.find(id => id !== socket.id);
        if (opponentId) {
          room.gameOver = true;
          io.to(roomId).emit('game_over', { winner: opponentId, reason: 'opponent_disconnected' });
        }
      }

      // 清理房間
      delete rooms[roomId];
    }
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`🚀 遊戲競速伺服器已啟動！Port: ${PORT}`);
});