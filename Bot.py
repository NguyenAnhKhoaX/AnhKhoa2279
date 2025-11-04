import discord
from discord import app_commands
import random
import string
import asyncio
from datetime import datetime

# Cấu hình
TOKEN = "YOUR_BOT_TOKEN_HERE"
KEY_PREFIX = "NazuX"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Lưu trữ key đã tạo
generated_keys = {}

def generate_key():
    """Tạo key ngẫu nhiên"""
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    timestamp = datetime.now().strftime("%d%H%M")
    key = f"{KEY_PREFIX}_{random_part}_{timestamp}"
    return key

@client.event
async def on_ready():
    print(f'✅ Bot đã đăng nhập với tên: {client.user}')
    await tree.sync()
    print("✅ Slash commands đã đồng bộ")

@tree.command(name="key", description="Tạo key ngẫu nhiên cho NazuX Hub")
async def key_command(interaction: discord.Interaction):
    """Lệnh /key để tạo key"""
    try:
        # Tạo key mới
        new_key = generate_key()
        
        # Lưu key theo user
        user_id = str(interaction.user.id)
        if user_id not in generated_keys:
            generated_keys[user_id] = []
        
        generated_keys[user_id].append({
            "key": new_key,
            "timestamp": datetime.now().isoformat()
        })
        
        # Tạo embed đẹp
        embed = discord.Embed(
            title="🔑 NazuX Hub Key Generator",
            description=f"Key của bạn đã được tạo thành công!",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📋 KEY CỦA BẠN",
            value=f"```{new_key}```",
            inline=False
        )
        
        embed.add_field(
            name="📊 THỐNG KÊ",
            value=f"Bạn đã tạo: **{len(generated_keys[user_id])}** key",
            inline=True
        )
        
        embed.add_field(
            name="⏰ THỜI GIAN",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=True
        )
        
        embed.set_footer(text="NazuX Hub • Sử dụng key trong script của bạn")
        
        # Gửi key qua DM (bảo mật hơn)
        try:
            await interaction.user.send(
                content="🔑 **KEY CỦA BẠN - GIỮ KÍN!**",
                embed=embed
            )
            await interaction.response.send_message(
                "✅ Key đã được gửi đến tin nhắn riêng của bạn!",
                ephemeral=True
            )
        except discord.Forbidden:
            # Nếu không gửi được DM, gửi ở channel
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Lỗi khi tạo key: {str(e)}",
            ephemeral=True
        )

@tree.command(name="mykeys", description="Xem các key bạn đã tạo")
async def mykeys_command(interaction: discord.Interaction):
    """Lệnh /mykeys để xem key đã tạo"""
    user_id = str(interaction.user.id)
    
    if user_id not in generated_keys or not generated_keys[user_id]:
        await interaction.response.send_message(
            "❌ Bạn chưa tạo key nào! Dùng `/key` để tạo key mới.",
            ephemeral=True
        )
        return
    
    user_keys = generated_keys[user_id][-5:]  # 5 key gần nhất
    
    embed = discord.Embed(
        title="📋 KEY CỦA BẠN",
        description="Danh sách các key bạn đã tạo:",
        color=0x0099ff
    )
    
    for i, key_data in enumerate(reversed(user_keys), 1):
        embed.add_field(
            name=f"Key #{i}",
            value=f"```{key_data['key']}```\nTạo: <t:{int(datetime.fromisoformat(key_data['timestamp']).timestamp())}:R>",
            inline=False
        )
    
    embed.set_footer(text=f"Tổng cộng: {len(generated_keys[user_id])} key")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="stats", description="Thống kê key đã tạo")
async def stats_command(interaction: discord.Interaction):
    """Lệnh /stats để xem thống kê"""
    total_keys = sum(len(keys) for keys in generated_keys.values())
    total_users = len(generated_keys)
    
    embed = discord.Embed(
        title="📊 THỐNG KÊ HỆ THỐNG",
        color=0xff9900
    )
    
    embed.add_field(name="👥 Tổng users", value=f"**{total_users}** users", inline=True)
    embed.add_field(name="🔑 Tổng keys", value=f"**{total_keys}** keys", inline=True)
    embed.add_field(name="⚡ Prefix", value=f"`{KEY_PREFIX}`", inline=True)
    
    # Top users
    if generated_keys:
        top_users = sorted(generated_keys.items(), key=lambda x: len(x[1]), reverse=True)[:3]
        top_text = "\n".join([f"<@{user_id}>: {len(keys)} keys" for user_id, keys in top_users[:3]])
        embed.add_field(name="🏆 TOP USERS", value=top_text or "Chưa có data", inline=False)
    
    await interaction.response.send_message(embed=embed)

# Chạy bot
if __name__ == "__main__":
    print("🚀 Đang khởi động bot...")
    client.run(TOKEN)
