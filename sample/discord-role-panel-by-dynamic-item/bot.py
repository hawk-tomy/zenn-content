# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "discord.py>=2.4.0"
# ]
# ///

from __future__ import annotations

import re
from os import getenv

from discord import AllowedMentions, ButtonStyle, Client, Embed, Guild, Intents, Interaction, Member, Role, abc
from discord.app_commands import CommandTree, command
from discord.ui import Button, DynamicItem, View


class DynamicRoleButton(DynamicItem[Button[View]], template=r"RoleButton:(?P<id>[0-9a-f]+)"):
    def __init__(self, role_id: int, label: str):
        self.role_id = role_id
        super().__init__(Button(label=label, style=ButtonStyle.primary, custom_id=f"RoleButton:{role_id:x}"))

    @classmethod
    async def from_custom_id(cls, interaction: Interaction, item: Button[View], match: re.Match[str]):
        return cls(int(match.group("id"), 16), item.label or "")

    async def callback(self, interaction: Interaction):
        # get guild
        guild = interaction.guild
        assert guild is not None

        # get member
        member = guild.get_member(interaction.user.id)
        if member is None:
            member = await guild.fetch_member(interaction.user.id)
        assert member is not None

        # get role
        role = guild.get_role(self.role_id)
        if role is None:
            role = await guild.fetch_role(self.role_id)
        assert role is not None

        assert isinstance(guild, Guild) and isinstance(member, Member) and isinstance(role, Role)

        # add or remove role
        if role in member.roles:
            await member.remove_roles(role)
            msg = f"Removed {role.mention} from you."
        else:
            await member.add_roles(role)
            msg = f"Added {role.mention} to you."
        await interaction.response.send_message(content=msg, ephemeral=True, allowed_mentions=AllowedMentions.none())


@command(name="create-role-panel")
async def create_role_panel(interaction: Interaction, title: str, description: str | None, role: Role, label: str):
    # get channel
    assert interaction.channel is not None and isinstance(interaction.channel, abc.Messageable)

    view = View(timeout=None)
    view.add_item(DynamicRoleButton(role.id, label))
    await interaction.channel.send(embeds=[Embed(title=title, description=description)], view=view)

    await interaction.response.send_message(content="Created role panel.", ephemeral=True)


class Bot(Client):
    def __init__(self):
        intents = Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = CommandTree(self)

    async def setup_hook(self):
        self.add_dynamic_items(DynamicRoleButton)

        self.tree.add_command(create_role_panel)
        await self.tree.sync()

    async def on_ready(self):
        assert self.user is not None
        print(f"Logged on as {self.user} (ID: {self.user.id})")


def main():
    bot = Bot()
    token = getenv("DISCORD_BOT_TOKEN")
    assert token is not None
    bot.run(token)


if __name__ == "__main__":
    main()
