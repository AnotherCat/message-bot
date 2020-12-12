# cogs/maincog.py

"""
Message Manager - A bot for discord
Copyright (C) 2020  AnotherCat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import platform

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import discord

from discord.ext import commands

from main import Bot

if TYPE_CHECKING:
    Cog = commands.Cog[commands.Context]
else:
    Cog = commands.Cog


class MainCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def on_command_error(
        self, ctx: commands.Context, error: discord.DiscordException
    ) -> None:
        await ctx.send(
            "There was an unknown error!\n"
            f"Report a bug or get support from the support server at {self.bot.command_with_prefix(ctx, 'support')}\n"
            f"Error: {error}"
        )
        raise error

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # Print the bot invite link
        print(
            f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=379968&scope=bot"
        )
        print(f"Logged on as {self.bot.user}!")
        self.bot.load_time = datetime.utcnow()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        channel = None
        assert guild.me is not None
        if guild.system_channel is None:
            for c in guild.text_channels:
                perm = c.permissions_for(guild.me)
                if perm.send_messages and perm.embed_links:
                    channel = c
                    break
        else:
            system_channel = guild.system_channel
            perms = system_channel.permissions_for(guild.me)
            if perms.send_messages and perms.embed_links:
                channel = system_channel
            else:
                for c in guild.text_channels:
                    perm = c.permissions_for(guild.me)
                    if perm.send_messages and perm.embed_links:
                        channel = c
                        break
        if channel is not None:
            prefix = await self.bot.db.get_prefix(guild)
            embed = discord.Embed(
                title="Hi there!",
                colour=discord.Colour(16761035),
                description="Thank you for inviting me to your server!",
                timestamp=datetime.now(timezone.utc),
                url="https://messagemanager.xyz",
            )
            embed.add_field(
                name="Prefix", value=f"My prefix here is: `{prefix}`", inline=False
            )
            embed.add_field(
                name="Help",
                value="Have a look at my [docs](https://docs.messagemanager.xyz) "
                "If you've got any questions or join our [support server](https://discord.gg/xFZu29t)",
                inline=False,
            )
            embed.add_field(
                name="Privacy Policy",
                value="Please read my [privacy policy](). \nBy using the bot you are confirming that you have read the privacy policy.",
            )
            await channel.send(embed=embed)
        if not self.bot.self_hosted:
            embed = discord.Embed(
                title="Joined a server!",
                colour=discord.Colour(16761035),
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="Name", value=guild.name, inline=False)
            embed.add_field(name="ID", value=str(guild.id), inline=False)
            log_channel = self.bot.get_channel(self.bot.join_log_channel)
            if isinstance(
                log_channel, discord.TextChannel
            ):  # ensure that log_channel is a text channel
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        if not self.bot.self_hosted:
            embed = discord.Embed(
                title="Left a server!",
                colour=discord.Colour(16761035),
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(name="Name", value=guild.name, inline=False)
            embed.add_field(name="ID", value=str(guild.id), inline=False)
            log_channel = self.bot.get_channel(self.bot.join_log_channel)
            if isinstance(
                log_channel, discord.TextChannel
            ):  # ensure that the log channel is a text channel
                await log_channel.send(embed=embed)

    @commands.command(
        name="help", help="Responds with an embed with all the commands and options"
    )
    async def help(self, ctx: commands.Context, option: Optional[str] = None) -> None:
        if option is None or option.lower() != "setup":
            embed = discord.Embed(
                title="Help!",
                colour=16761035,
                timestamp=datetime.now(timezone.utc),
                url="https://docs.messagemanager.xyz",
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "ping"),
                value="Replies with the latency of the bot",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "help"),
                value="Displays this view.",
                inline=True,
            ),
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "info"),
                value="Displays info about the bot",
                inline=True,
            ),
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "send [channel_id] [content]"),
                value="Sends a message from the bot in the specificed channel",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(
                    ctx, "edit [channel_id] [message_id] [new_content]"
                ),
                value="Edits a message, message **must** be from the bot",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(
                    ctx, "fetch [channel_id] [message_id]"
                ),
                value="Returns raw content of the message in a .txt file",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(
                    ctx, "delete [channel_id] [message_id]"
                ),
                value="Deletes the message from the bot. **Must** be from the bot",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "setup"),
                value="Starts setup, Requires the user to have admin permissions",
                inline=True,
            )
            embed.add_field(
                name="Embeds",
                value="Find the documentation for sending embeds [here](https://docs.messagemanager.xyz/functions/messages/#rich-embed-messages) (it's too big to fit here now)",
            )
            await ctx.send(embed=embed)
        else:
            try:
                setup_command = self.bot.get_command("setup")
                if setup_command is not None:
                    await ctx.invoke(setup_command)
                return
            except Exception:
                help_command = self.bot.get_command("help")
                if help_command is not None:
                    await ctx.invoke(help_command)

    # Create the info command.
    @commands.command(name="info")
    async def info(self, ctx: commands.Context) -> None:
        prefix = await self.bot.db.get_prefix(ctx.guild)
        total_seconds = (datetime.utcnow() - self.bot.start_time).total_seconds()
        days = total_seconds // 86400
        hours = (total_seconds - (days * 86400)) // 3600
        minutes = (total_seconds - (days * 86400) - (hours * 3600)) // 60
        seconds = total_seconds - (days * 86400) - (hours * 3600) - (minutes * 60)
        embed = discord.Embed(
            title="Info about the bot",
            colour=discord.Colour(0xC387C1),
            timestamp=datetime.now(timezone.utc),
            url="https://messagemanager.xyz",
        )
        embed.add_field(name="Username", value=str(self.bot.user), inline=True),
        embed.add_field(name="Prefix", value=f"`{prefix}`", inline=True),
        embed.add_field(name="Version", value=self.bot.version, inline=True),
        embed.add_field(
            name="Docs",
            value="[The Docs](https://docs.messagemanager.xyz)",
            inline=True,
        ),
        embed.add_field(
            name="Developer",
            value="[Another Cat](https://github.com/AnotherCat)",
            inline=True,
        ),  # The developer (me), Must not be changed, as per the LICENSE
        embed.add_field(
            name="Discord.py Version", value=discord.__version__, inline=True
        ),
        embed.add_field(
            name="Python Version", value=platform.python_version(), inline=True
        ),
        embed.add_field(name="System", value=platform.system(), inline=True),
        embed.add_field(
            name="Uptime",
            value=f"{int(days)} days {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds",
            inline=True,
        ),
        embed.add_field(
            name="Number of Servers", value=str(len(self.bot.guilds)), inline=True
        )
        embed.set_thumbnail(url=f"{self.bot.user.avatar_url}")
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context) -> None:
        message = await ctx.send("Pong!")
        ping_time = (message.created_at - ctx.message.created_at).total_seconds() * 1000
        await message.edit(content=f"Ping! Took: {int(ping_time)}ms")

    @commands.command()
    async def privacy(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title="Privacy Policy",
            description="We do store data. Please read our privacy policy.",
            url="https://github.com/AnotherCat/message-bot/blob/master/PRIVACY_POLICY.md",
            colour=discord.Colour.red(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(
            name="Where to find the privacy policy",
            value="My privacy policy is located on [github](https://github.com/AnotherCat/message-bot/blob/master/PRIVACY_POLICY.md)",
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                title="Invite me to your server!",
                description="[Click here](https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=379968&scope=bot) to invite me!",
                url="https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=379968&scope=bot",
                colour=discord.Colour(0xC387C1),
                timestamp=datetime.now(timezone.utc),
            )
        )

    @commands.command()
    async def docs(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                title="Docs!",
                description="My docs are [here](https://docs.messagemanager.xyz)",
                url="https://docs.messagemanager.xyz",
                colour=discord.Colour(0xC387C1),
                timestamp=datetime.now(timezone.utc),
            )
        )

    @commands.command()
    async def source(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                title="Source Code!",
                description="My [source code](https://github.com/AnotherCat/message-bot)",
                url="https://github.com/AnotherCat/message-bot",
                colour=discord.Colour(0xC387C1),
                timestamp=datetime.now(timezone.utc),
            )
        )

    @commands.command()
    async def support(self, ctx: commands.Context) -> None:
        await ctx.send(
            embed=discord.Embed(
                title="Join my support server for support!",
                description="Click [here](https://discord.gg/xFZu29t) to join!",
                url="https://discord.gg/xFZu29t",
                colour=discord.Colour(0xC387C1),
                timestamp=datetime.now(timezone.utc),
            )
        )


def setup(bot: Bot) -> None:
    bot.add_cog(MainCog(bot))
    print("    Main cog!")
