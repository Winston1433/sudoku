const express = require('express');
const http = require('http');
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// 設定靜態檔案資料夾，讓瀏覽器能讀取 public 裡面的 index.html
app.use(express.static('public'));

// ----------------------------------------
// Socket.io 連線與廣播邏輯
// ----------------------------------------
io.on('connection', (socket) => {
  console.log('連線成功！有新玩家進來了，ID: ', socket.id);

  // 1. 接收某個玩家「開新局」的題目，並廣播給所有人 (包含他自己)
  socket.on('sync_puzzle', (data) => {
    io.emit('sync_puzzle', data);
  });

  // 2. 接收某個玩家「填入數字」，轉發給『其他』玩家
  socket.on('player_input', (data) => {
    socket.broadcast.emit('remote_input', data);
  });

  // 3. 接收某個玩家「清除格子」，轉發給『其他』玩家
  socket.on('player_erase', (data) => {
    socket.broadcast.emit('remote_erase', data);
  });

  // 玩家關閉網頁或斷線
  socket.on('disconnect', () => {
    console.log('玩家離開了，ID: ', socket.id);
  });
});

// ----------------------------------------
// 啟動伺服器
// ----------------------------------------
// 優先使用雲端平台提供的 PORT，如果在本地端測試則預設為 3000
const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  console.log(`🚀 遊戲伺服器已啟動！Port: ${PORT}`);
});