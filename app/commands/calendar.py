import discord
import logging
import requests

from discord.ext import commands
from datetime import datetime, timezone

from app.mappings.calendar import EVENTS, SEASON

logger = logging.getLogger(__name__)


class Calendar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="calendar", with_app_command=True, description="Get the weekly 1999 Calendar")
    async def calendar(self, ctx):
        try:
            res = requests.get(
                "https://content.warframe.com/dynamic/worldState.php")
            data = res.json()
            calendar = data['KnownCalendarSeasons'][0]
            current_time = datetime.now(timezone.utc)
            expiry = datetime.fromtimestamp(
                int(calendar['Expiry']['$date']['$numberLong'])/1000, timezone.utc)
            eta = parse_time_left(expiry - current_time)
            year_iteration = calendar.get('YearIteration', 0)
            season = SEASON[calendar['Season']]

            challanges = []
            rewards = {}
            birthdays = []
            overrides = {}
            for day in calendar['Days']:
                rewards[day['day']] = []
                overrides[day['day']] = []
                for event in day['events']:
                    event_type = event['type']
                    event_list = EVENTS[event_type]
                    event_key = event_list['key']
                    unique_name = event[event_key]

                    event_dict = find_event_by_unique_name(EVENTS, unique_name)
                    if not event_dict:
                        description = unique_name.split("/")[-1]
                    else:
                        description = event_dict['description']

                    if event_type == "CET_CHALLENGE":
                        challanges.append(description)
                    elif event_type == "CET_REWARD":
                        rewards[day['day']].append(description)
                    elif event_type == "CET_PLOT":
                        if event_dict:
                            description += f" ({event_dict['day']})"
                        birthdays.append(description)
                    elif event_type == "CET_UPGRADE":
                        overrides[day['day']].append(
                            [description, event_dict.get("for", "")])

            embed = discord.Embed(
                title="1999 Calendar",
                description=f"Current iteration: **{year_iteration}**\nSeason: **{season}**"
            )
            embed.set_footer(text=f"Ends in {eta}")

            text = ""
            for challenge in challanges:
                text += f"- {challenge}\n"
            embed.add_field(name="Challenges", value=text, inline=False)

            text = ""
            for day, reward in rewards.items():
                if reward:
                    text += f"- **{'** <> **'.join(reward)}**\n"
            embed.add_field(name="Rewards", value=text, inline=False)

            text = ""
            for day, override in overrides.items():
                if override:
                    text += "- \n"
                    for o in override:
                        text += f"  - ({o[1]}) {o[0]}\n"
                    text += "\n"
            embed.add_field(name="Overrides", value=text, inline=False)

            text = ""
            for birthday in birthdays:
                text += f"- {birthday}\n"
            embed.add_field(name="Birthdays", value=text, inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(e)
            return await ctx.send(f"Something went wrong!")


async def setup(bot):
    await bot.add_cog(Calendar(bot))


def parse_time_left(time_left: datetime) -> str:
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_left = ""
    if days:
        time_left += f"{days} days, "
    if hours:
        time_left += f"{hours} hours, "
    if minutes:
        time_left += f"{minutes} minutes"
    return time_left


def find_event_by_unique_name(events, unique_name):
    for event_type, event_data in events.items():
        for event in event_data["mappings"]:
            if event["uniqueName"] == unique_name:
                return event
    return {}
