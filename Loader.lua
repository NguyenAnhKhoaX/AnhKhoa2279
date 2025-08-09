local Games = loadstring(game:HttpGet("https://raw.githubusercontent.com/NguyenAnhKhoaX/AnhKhoa2279/refs/heads/main/GameList.lua"))()

local URL = Games[game.PlaceId]

if URL then
  loadstring(game:HttpGet(URL))()
end
