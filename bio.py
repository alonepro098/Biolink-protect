"""
Author: Elite Sid
User: https://t.me/SID_ELITE
Channel: https://t.me/TeamXUpdate
"""

from pyrogram import Client, filters, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
import time
import re

from helper.utils import (
    is_admin,
    get_config, update_config,
    increment_warning, reset_warnings,
    is_whitelisted, add_whitelist, remove_whitelist, get_whitelist,
    get_detection_enabled, get_penalty_duration
)

from helper.detector import has_link_in_bio

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    URL_PATTERN
)

app = Client(
    "biolink_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message):
    chat_id = message.chat.id
    bot = await client.get_me()
    add_url = f"https://t.me/{bot.username}?startgroup=true"
    text = (
        "**✨ Welcome to BioLink Protector Bot! ✨**\n\n"
        "🛡️ I help protect your groups from users with links in their bio.\n\n"
        "**🔹 Key Features:**\n"
        "   • Automatic URL detection in user bios\n"
        "   • Customizable warning limit\n"
        "   • Auto-mute or ban when limit is reached\n"
        "   • Whitelist management for trusted users\n\n"
        "**Use /help to see all available commands.**"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me to Your Group", url=add_url)],
        [
            InlineKeyboardButton("🛠️ Support", url="https://t.me/TeamsXchat"),
            InlineKeyboardButton("🗑️ Close", callback_data="close")
        ]
    ])
    await client.send_message(chat_id, text, reply_markup=kb)
    
@app.on_message(filters.command("help"))
async def help_handler(client: Client, message):
    chat_id = message.chat.id
    help_text = (
        "**🛠️ Bot Commands & Usage**\n\n"
        "`/config` – set warn-limit & punishment mode\n"
        "`/free` – whitelist a user (reply or user/id)\n"
        "`/unfree` – remove from whitelist\n"
        "`/freelist` – list all whitelisted users\n"
        "`/status` – show current configuration\n"
        "`/toggle` – enable/disable bio link scanning in this group\n"
        "`/setduration <value>` – set penalty duration (e.g., 0, 30m, 2h, 1d)\n\n"
        "**When someone with a URL in their bio posts, I’ll:**\n"
        " 1. ⚠️ Warn them\n"
        " 2. 🔇 Mute if they exceed limit\n"
        " 3. 🔨 Ban if set to ban\n\n"
        "**Use the inline buttons on warnings to cancel or whitelist**"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑️ Close", callback_data="close")]
    ])
    await client.send_message(chat_id, help_text, reply_markup=kb)

@app.on_message(filters.group & filters.command("config"))
async def configure(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    mode, limit, penalty = await get_config(chat_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Warn", callback_data="warn")],
        [
            InlineKeyboardButton("Mute ✅" if penalty == "mute" else "Mute", callback_data="mute"),
            InlineKeyboardButton("Ban ✅" if penalty == "ban" else "Ban", callback_data="ban")
        ],
        [InlineKeyboardButton("Close", callback_data="close")]
    ])
    await client.send_message(
        chat_id,
        "**Choose penalty for users with links in bio:**",
        reply_markup=keyboard
    )
    await message.delete()

@app.on_message(filters.group & filters.command("free"))
async def command_free(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await client.send_message(chat_id, "**Reply or use /free user or id to whitelist someone.**")

    await add_whitelist(chat_id, target.id)
    await reset_warnings(chat_id, target.id)

    text = f"**✅ {target.mention} has been added to the whitelist**"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚫 Unwhitelist", callback_data=f"unwhitelist_{target.id}"),
            InlineKeyboardButton("🗑️ Close", callback_data="close")
        ]
    ])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(filters.group & filters.command("unfree"))
async def command_unfree(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    if message.reply_to_message:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        arg = message.command[1]
        target = await client.get_users(int(arg) if arg.isdigit() else arg)
    else:
        return await client.send_message(chat_id, "**Reply or use /unfree user or id to unwhitelist someone.**")

    if await is_whitelisted(chat_id, target.id):
        await remove_whitelist(chat_id, target.id)
        text = f"**🚫 {target.mention} has been removed from the whitelist**"
    else:
        text = f"**ℹ️ {target.mention} is not whitelisted.**"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Whitelist", callback_data=f"whitelist_{target.id}"),
            InlineKeyboardButton("🗑️ Close", callback_data="close")
        ]
    ])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_message(filters.group & filters.command("freelist"))
async def command_freelist(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    ids = await get_whitelist(chat_id)
    if not ids:
        await client.send_message(chat_id, "**⚠️ No users are whitelisted in this group.**")
        return

    text = "**📋 Whitelisted Users:**\n\n"
    for i, uid in enumerate(ids, start=1):
        try:
            user = await client.get_users(uid)
            name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
            text += f"{i}: {name} [`{uid}`]\n"
        except:
            text += f"{i}: [User not found] [`{uid}`]\n"

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Close", callback_data="close")]])
    await client.send_message(chat_id, text, reply_markup=keyboard)

@app.on_callback_query()
async def callback_handler(client: Client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return await callback_query.answer("❌ You are not administrator", show_alert=True)

    if data == "close":
        return await callback_query.message.delete()

    if data == "back":
        mode, limit, penalty = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Warn", callback_data="warn")],
            [
                InlineKeyboardButton("Mute ✅" if penalty=="mute" else "Mute", callback_data="mute"),
                InlineKeyboardButton("Ban ✅" if penalty=="ban" else "Ban", callback_data="ban")
            ],
            [InlineKeyboardButton("Close", callback_data="close")]
        ])
        await callback_query.message.edit_text("**Choose penalty for users with links in bio:**", reply_markup=kb)
        return await callback_query.answer()

    if data == "warn":
        _, selected_limit, _ = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"5 ✅" if selected_limit==5 else "5", callback_data="warn_5"),
             InlineKeyboardButton(f"10 ✅" if selected_limit==10 else "10", callback_data="warn_10"),
             InlineKeyboardButton(f"15 ✅" if selected_limit==15 else "15", callback_data="warn_15")],
            [InlineKeyboardButton("Back", callback_data="back"), InlineKeyboardButton("Close", callback_data="close")]
        ])
        return await callback_query.message.edit_text("**Select number of warns before penalty:**", reply_markup=kb)

    if data in ["mute", "ban"]:
        await update_config(chat_id, penalty=data)
        mode, limit, penalty = await get_config(chat_id)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Warn", callback_data="warn")],
            [
                InlineKeyboardButton("Mute ✅" if penalty=="mute" else "Mute", callback_data="mute"),
                InlineKeyboardButton("Ban ✅" if penalty=="ban" else "Ban", callback_data="ban")
            ],
            [InlineKeyboardButton("Close", callback_data="close")]
        ])
        await callback_query.message.edit_text("**Punishment selected:**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith("warn_"):
        count = int(data.split("_")[1])
        await update_config(chat_id, limit=count)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"5 ✅" if count==5 else "5", callback_data="warn_5"),
             InlineKeyboardButton(f"10 ✅" if count==10 else "10", callback_data="warn_10"),
             InlineKeyboardButton(f"15 ✅" if count==15 else "15", callback_data="warn_15")],
            [InlineKeyboardButton("Back", callback_data="back"), InlineKeyboardButton("Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**Warning limit set to {count}**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith(("unmute_", "unban_")):
        action, uid = data.split("_")
        target_id = int(uid)
        user = await client.get_users(target_id)
        name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        try:
            if action == "unmute":
                await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=True))
            else:
                await client.unban_chat_member(chat_id, target_id)
            await reset_warnings(chat_id, target_id)
            msg = f"**{name} (`{target_id}`) has been {'unmuted' if action=='unmute' else 'unbanned'}**."

            kb = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Whitelist ✅", callback_data=f"whitelist_{target_id}"),
                    InlineKeyboardButton("🗑️ Close", callback_data="close")
                ]
            ])
            await callback_query.message.edit_text(msg, reply_markup=kb)
        
        except errors.ChatAdminRequired:
            await callback_query.message.edit_text(f"I don't have permission to {action} users.")
        return await callback_query.answer()

    if data.startswith("cancel_warn_"):
        target_id = int(data.split("_")[-1])
        await reset_warnings(chat_id, target_id)
        user = await client.get_users(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Whitelist✅", callback_data=f"whitelist_{target_id}"),
             InlineKeyboardButton("🗑️ Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] has no more warnings!**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith("whitelist_"):
        target_id = int(data.split("_")[1])
        await add_whitelist(chat_id, target_id)
        await reset_warnings(chat_id, target_id)
        user = await client.get_users(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚫 Unwhitelist", callback_data=f"unwhitelist_{target_id}"),
             InlineKeyboardButton("🗑️ Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**✅ {mention} [`{target_id}`] has been whitelisted!**", reply_markup=kb)
        return await callback_query.answer()

    if data.startswith("unwhitelist_"):
        target_id = int(data.split("_")[1])
        await remove_whitelist(chat_id, target_id)
        user = await client.get_users(target_id)
        full_name = f"{user.first_name}{(' ' + user.last_name) if user.last_name else ''}"
        mention = f"[{full_name}](tg://user?id={target_id})"
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("Whitelist✅", callback_data=f"whitelist_{target_id}"),
             InlineKeyboardButton("🗑️ Close", callback_data="close")]
        ])
        await callback_query.message.edit_text(f"**❌ {mention} [`{target_id}`] has been removed from whitelist.**", reply_markup=kb)
        return await callback_query.answer()

@app.on_message(filters.group)
async def check_bio(client: Client, message):
    chat_id = message.chat.id

    if not await get_detection_enabled(chat_id):
        return

    # Skip service messages or bot messages
    if not message.from_user or message.from_user.is_bot:
        return

    user_id = message.from_user.id
    if await is_admin(client, chat_id, user_id) or await is_whitelisted(chat_id, user_id):
        return

    # Prefer get_users for user info; fallback to get_chat
    try:
        user = await client.get_users(user_id)
    except Exception:
        user = await client.get_chat(user_id)

    bio = getattr(user, "bio", "") or ""
    full_name = f"{user.first_name}{(' ' + user.last_name) if getattr(user, 'last_name', None) else ''}"
    mention = f"[{full_name}](tg://user?id={user_id})"

    if has_link_in_bio(bio):
        try:
            await message.delete()
        except errors.MessageDeleteForbidden:
            return await message.reply_text("Please grant me delete permission.")

        mode, limit, penalty = await get_config(chat_id)
        duration = await get_penalty_duration(chat_id)
        until_date = int(time.time() + duration) if duration > 0 else None

        if mode == "warn":
            count = await increment_warning(chat_id, user_id)
            warning_text = (
                "**🚨 Warning Issued** 🚨\\n\\n"
                f"👤 **User:** {mention} `[{user_id}]`\\n"
                "❌ **Reason:** URL found in bio\\n"
                f"⚠️ **Warning:** {count}/{limit}\\n\\n"
                "**Notice: Please remove any links from your bio.**"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel Warning", callback_data=f"cancel_warn_{user_id}"),
                 InlineKeyboardButton("✅ Whitelist", callback_data=f"whitelist_{user_id}")],
                [InlineKeyboardButton("🗑️ Close", callback_data="close")]
            ])
            sent = await message.reply_text(warning_text, reply_markup=keyboard)
            if count >= limit:
                try:
                    if penalty == "mute":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False), until_date=until_date)
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unmute ✅", callback_data=f"unmute_{user_id}")]])
                        await sent.edit_text(f"**{mention} has been 🔇 muted for [Link In Bio].**", reply_markup=kb)
                    else:
                        await client.ban_chat_member(chat_id, user_id, until_date=until_date)
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unban ✅", callback_data=f"unban_{user_id}")]])
                        await sent.edit_text(f"**{mention} has been 🔨 banned for [Link In Bio].**", reply_markup=kb)
                
                except errors.ChatAdminRequired:
                    await sent.edit_text(f"**I don't have permission to {penalty} users.**")
        else:
            try:
                if mode == "mute":
                    await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False), until_date=until_date)
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unmute", callback_data=f"unmute_{user_id}")]])
                    await message.reply_text(f"{mention} has been 🔇 muted for [Link In Bio].", reply_markup=kb)
                else:
                    await client.ban_chat_member(chat_id, user_id, until_date=until_date)
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Unban", callback_data=f"unban_{user_id}")]])
                    await message.reply_text(f"{mention} has been 🔨 banned for [Link In Bio].", reply_markup=kb)
            except errors.ChatAdminRequired:
                return await message.reply_text(f"I don't have permission to {mode} users.")
    else:
        await reset_warnings(chat_id, user_id)

def _parse_duration(arg: str) -> int:
    s = arg.strip().lower()
    if s.isdigit():
        return int(s)
    m = re.match(r"^(\d+)\s*([smhdw])$", s)
    if not m:
        raise ValueError("Invalid duration format")
    val = int(m.group(1))
    unit = m.group(2)
    return {
        "s": val,
        "m": val * 60,
        "h": val * 3600,
        "d": val * 86400,
        "w": val * 604800,
    }[unit]


@app.on_message(filters.group & filters.command("status"))
async def status_handler(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    mode, limit, penalty = await get_config(chat_id)
    detection = await get_detection_enabled(chat_id)
    duration = await get_penalty_duration(chat_id)
text = (
    "**🔧 Current Configuration**\n\n"
    f"• Detection: {'Enabled' if detection else 'Disabled'}\n"
    f"• Mode: {mode}\n"
    f"• Warning Limit: {limit}\n"
    f"• Penalty: {penalty}\n"
    f"• Penalty Duration: {duration if duration > 0 else 'Permanent'}\n"
)

kb = InlineKeyboardMarkup([
    [InlineKeyboardButton("🗑️ Close", callback_data="close")]
])

await client.send_message(chat_id, text, reply_markup=kb)


@app.on_message(filters.group & filters.command("toggle"))
async def toggle_handler(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    current = await get_detection_enabled(chat_id)
    new_val = not current
    await update_config(chat_id, detection_enabled=new_val)
await client.send_message(chat_id, f"**Detection {'Enabled' if new_val else 'Disabled'}**")

@app.on_message(filters.group & filters.command("setduration"))
async def setduration_handler(client: Client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not await is_admin(client, chat_id, user_id):
        return

    if len(message.command) < 2:
        return await client.send_message(chat_id, "**Usage:** /setduration <seconds|30m|2h|1d|0>")
    arg = message.command[1]
    try:
        seconds = _parse_duration(arg)
    except Exception:
        return await client.send_message(chat_id, "**Invalid duration. Use seconds or 30m / 2h / 1d / 0.**")
        
    await update_config(chat_id, penalty_duration=seconds)
    await client.send_message(chat_id, f\"**Penalty duration set to {seconds if seconds>0 else 'Permanent'}**\")


@app.on_message(filters.group & filters.new_chat_members)
async def new_member_scan(client: Client, message):
    chat_id = message.chat.id

    if not await get_detection_enabled(chat_id):
        return

    for user in message.new_chat_members:
        if user.is_bot:
            continue

        user_id = user.id
        if await is_admin(client, chat_id, user_id) or await is_whitelisted(chat_id, user_id):
            continue

        try:
            u = await client.get_users(user_id)
        except Exception:
            u = await client.get_chat(user_id)

        bio = getattr(u, \"bio\", \"\") or \"\"
        full_name = f\"{u.first_name}{(' ' + u.last_name) if getattr(u, 'last_name', None) else ''}\"
        mention = f\"[{full_name}](tg://user?id={user_id})\"

        if has_link_in_bio(bio):
            mode, limit, penalty = await get_config(chat_id)
            duration = await get_penalty_duration(chat_id)
            until_date = int(time.time() + duration) if duration > 0 else None

            try:
                if mode == \"warn\":
                    count = await increment_warning(chat_id, user_id)
                    warning_text = (
                        \"**🚨 Warning Issued (On-Join)** 🚨\\n\\n\"
                        f\"👤 **User:** {mention} `[{user_id}]`\\n\"
                        \"❌ **Reason:** URL found in bio\\n\"
                        f\"⚠️ **Warning:** {count}/{limit}\\n\\n\"
                        \"**Notice: Please remove any links from your bio.**\"
                    )
                    kb = InlineKeyboardMarkup([[InlineKeyboardButton(\"🗑️ Close\", callback_data=\"close\")]])
                    await client.send_message(chat_id, warning_text, reply_markup=kb)
                else:
                    if mode == \"mute\":
                        await client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False), until_date=until_date)
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton(\"Unmute\", callback_data=f\"unmute_{user_id}\")]])
                        await client.send_message(chat_id, f\"{mention} has been 🔇 muted for [Link In Bio].\", reply_markup=kb)
                    else:
                        await client.ban_chat_member(chat_id, user_id, until_date=until_date)
                        kb = InlineKeyboardMarkup([[InlineKeyboardButton(\"Unban\", callback_data=f\"unban_{user_id}\")]])
                        await client.send_message(chat_id, f\"{mention} has been 🔨 banned for [Link In Bio].\", reply_markup=kb)
            except errors.ChatAdminRequired:
                await client.send_message(chat_id, \"I don't have sufficient admin permissions.\")


if __name__ == "__main__":
    app.run()
