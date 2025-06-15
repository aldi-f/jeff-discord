from discord.ext import commands
from datetime import datetime
import discord
import requests
from funcs import find_internal_warframe_name, find_internal_ability_name
from redis_manager import cache

PLATFORMS = {
    "pc" : ["pc"],
    "switch" : ["switch","ns","swi"],
    "xbox" : ["xb1","xb","xbox"],
    "ps4" : ["ps","playstation","ps4","ps5"],
    "ios" : ["ios"]
}

class profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="profile", with_app_command=True, description="Get warframe user profile stats")
    # @app_commands.guilds(discord.Object(id=992897664087760979))
    async def profile(self, ctx: commands.Context, *, message: str=None, platform: str=None):
        if not message:
            await ctx.send("Please enter a profile name.")
            return
        
        if not platform:
            args_parts = message.split(" ")
            profile_name = " ".join(args_parts)
            platform = None

            if len(args_parts) > 1:
                *profile_name_parts, potential_platform = args_parts
                valid_platforms = [item for row in PLATFORMS.values() for item in row] # flatten
                if potential_platform in valid_platforms:
                    profile_name = " ".join(profile_name_parts)
                    platform = potential_platform
            else:
                profile_name = args_parts[0]
                platform = None

            if platform in PLATFORMS["switch"]:
                prefix = "-swi"
            elif platform in PLATFORMS["ps4"]:
                prefix = "-ps4"
            elif platform in PLATFORMS["xbox"]:
                prefix = "-xb1"
            elif platform in PLATFORMS["ios"] or platform in PLATFORMS["pc"]:
                prefix = ""
            else:
                prefix = ""
        else: # use platform directly if going through slash command
            profile_name = message

        try:
            profile_data = ProfileData(profile_name, prefix)
        except Exception as e:
            await ctx.send(f"No profile found")
            return
        
        view = ProfileView(profile_data=profile_data, author=ctx.author)
        initial_embed = profile_data.generate_main_embed()

        await ctx.send(embed=initial_embed, view=view)


async def setup(bot):
    await bot.add_cog(profile(bot))


class ProfileView(discord.ui.View):
    def __init__(self, *, profile_data, author):
        self.profile_data = profile_data
        self.author = author
        super().__init__(timeout=120)

    @discord.ui.button(label="Main",style=discord.ButtonStyle.gray)
    async def main_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        page_embed = self.profile_data.generate_main_embed()
        await interaction.response.edit_message(embed=page_embed)

    @discord.ui.button(label="Enemy Stats",style=discord.ButtonStyle.gray)
    async def enemy_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        page_embed = self.profile_data.generate_enemy_embed()
        await interaction.response.edit_message(embed=page_embed)

    @discord.ui.button(label="Ability stats",style=discord.ButtonStyle.gray)
    async def ability_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        page_embed = self.profile_data.generate_ability_embed()
        await interaction.response.edit_message(embed=page_embed)

    @discord.ui.button(label="Warframe stats",style=discord.ButtonStyle.gray)
    async def warframe_button(self,interaction:discord.Interaction,button:discord.ui.Button):
        page_embed = self.profile_data.generate_warframe_embed()
        await interaction.response.edit_message(embed=page_embed)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id == self.author.id:
            return True
        else:
            file = discord.File("silicate.jpg")
            await interaction.response.send_message("blehhhh",file=file, ephemeral=True)
            return False

        
class ProfileData():
    wf_status_url = "https://api.warframestat.us/profile/"
    def __init__(self, username, platform):
        self.wf_official_url = f"https://content{platform}.warframe.com/dynamic/getProfileViewingData.php"
        # self.wf_status = requests.get(f"{self.wf_status_url}{username}").json()
        self.wf_official = requests.get(f"{self.wf_official_url}?n={username}").json()

    @property
    def username(self) -> str:
        return self.wf_official['Results'][0]["DisplayName"]
    
    @property
    def mastery_rank(self) -> str:
        mastery = int(self.wf_official['Results'][0].get("PlayerLevel",0))
        if mastery > 30:
            return f"L{(mastery-30)}"
        return f"{mastery}"
    
    @property
    def clan(self) -> str:
        return self.wf_official['Results'][0].get('GuildName',"-").split("#")[0]
    
    @property
    def account_created(self) -> str:
        created_date = self.wf_official['Results'][0]['Created']
        return datetime.fromtimestamp(int(created_date['$date']['$numberLong'][:-3])).strftime('%Y-%m-%d')


    def generate_loadout(self) -> dict:
        return
        focus_trees = {
            "AP_DEFENSE" : "Vazarin",
            "AP_TACTIC" : "Naramon",
            "AP_WARD" : "Unariu",
            "AP_ATTACK": "Madurai",
            "AP_POWER" : "Zenurik",
        }

        valid_keys = {
            "suits": "Warframe",
            "primary" : "Primary",
            "secondary": "Secondary",
            "melee": "Melee",
        }

        current_loadout = {}

        loadout_map = self.wf_status['loadout']
        for key in valid_keys:
            if key in loadout_map:
                current_loadout[valid_keys[key]] = loadout_map[key][0].get('name',loadout_map[key][0].get('uniqueName',"-"))

        current_loadout["Focus Tree"] = focus_trees.get(self.wf_official['Results'][0]['LoadOutPreset'].get('FocusSchool'),"-")

        return current_loadout
    

    def generate_fashion(self) -> dict:
        return
        valid_color_keys = {
            "primaryColor" : "Primary Color",
            "attachmentsColor": "Attachments Color",
            "syandanaColor" : "Syandana Color",
        }
        valid_color_types = [
            "primary",
            "secondary",
            "tertiary",
            "accents",
            "emissive",
            "energy",
        ]

        current_fashion = {}
        
        loadout_map = self.wf_status["loadout"]
        current_fashion["name"] = loadout_map["suits"][0]["name"]

        #TODO get all configs, not just the first one
        warframe_config = loadout_map["suits"][0]["configs"][0]

        current_fashion["fashion_parts"] = []

        for skin in warframe_config["skins"]:
            if "EmptyCustomization" not in skin["uniqueName"] and "Cyst" not in skin["uniqueName"]:
                current_fashion["fashion_parts"].append(skin["item"]["name"])


        for part in valid_color_keys.keys():
            config = warframe_config.get(part)
            if config:
                current_fashion[valid_color_keys[part]] = {}
                for color_type in valid_color_types:
                    if color_type in config:
                        if isinstance(config[color_type],dict):
                            current_fashion[valid_color_keys[part]][color_type] = "#" + config[color_type]["hex"]
                        else:
                            current_fashion[valid_color_keys[part]][color_type] = [color["hex"] for color in config[color_type]]

        return current_fashion
    
    def enemy_total_stats(self) -> dict:
        stats = self.wf_official["Stats"]
        return {
            "kills" : sum(enemy.get("kills",0) for enemy in stats["Enemies"]),
            "headshots" : sum(enemy.get("headshots",0) for enemy in stats["Enemies"]),
            "executions" : sum(enemy.get("executions",0) for enemy in stats["Enemies"]),
            "deaths" : sum(enemy.get("deaths",0) for enemy in stats["Enemies"]),
            "assists" : sum(enemy.get("assists",0) for enemy in stats["Enemies"]),
        }
    
    def enemy_top_kills(self, top_n: int = 5) -> list:
        stats = self.wf_official["Stats"]
        data = [
            {
                "type" : enemy["type"],#.split("/")[-1],
                "kills" : enemy.get("kills",0)
            }
            for enemy in sorted(stats["Enemies"], key=lambda enemy: enemy.get("kills", 0), reverse=True) if "kills" in enemy ][:top_n]
        return data

    #TODO: Parse unique names
    #TODO: Filter operator abilities out
    @property
    def ability_total_stats(self)-> int:
        stats = self.wf_official["Stats"]
        if "Abilities" not in stats:
            return 0
        return sum(ability.get("used",0) for ability in stats['Abilities'])
    
    #TODO: Parse unique names
    def ability_top_used(self, top_n: int = 5) -> list:
        stats = self.wf_official["Stats"]
        abilities = filter(lambda x: find_internal_ability_name(x["type"], cache) and "OperatorTransferenceAbility" not in x["type"], stats['Abilities'])
        data = [
            {
                "type" : ability["type"],#.split("/")[-1],
                "used" : ability["used"]
            }
            for ability in sorted(abilities, key=lambda ability: ability.get("used", 0), reverse=True)][:top_n]
        return data
    
    #TODO: Parse unique names
    def ability_bottom_used(self, bottom_n: int = 5) -> list:
        stats = self.wf_official["Stats"]
        abilities = filter(lambda x: find_internal_ability_name(x["type"], cache) and "OperatorTransferenceAbility" not in x["type"], stats['Abilities'])
        data = [
            {
                "type" : ability["type"],#.split("/")[-1],
                "used" : ability["used"]
            }
            for ability in sorted(abilities, key=lambda ability: ability.get("used", 0), reverse=True)][-bottom_n:]
        return data
    
    #TODO: Parse unique names
    def warframe_top_used_by_type(self, type:str = "equipTime", top_n: int = 5)-> list:
        stats = self.wf_official["Stats"]
        warframes = filter(lambda x: find_internal_warframe_name(x["type"], cache) and "Wraith/Reaper" not in x["type"], stats['Weapons'])
        frames_top_by_time = [
            {
                "type": frame['type'], #.split('/')[-1],
                f"{type}": int(frame.get(type,0))
            } 
            for frame in sorted(warframes, key=lambda x: x.get(type, 0), reverse=True)][:top_n]

        return frames_top_by_time
    
    #TODO: Parse unique names
    def warframe_bottom_used_by_type(self, type:str = "equipTime", bottom_n: int = 5)-> list:
        stats = self.wf_official["Stats"]
        warframes = filter(lambda x: find_internal_warframe_name(x["type"], cache) and "Wraith/Reaper" not in x["type"], stats['Weapons'])
        frames_bottom_by_time = [
            {
                "type": frame['type'],#.split('/')[-1],
                f"{type}": int(frame.get(type,0))
            } 
            for frame in sorted(warframes, key=lambda x: x.get(type, 0), reverse=True)][-bottom_n:]
        
        return frames_bottom_by_time
    
    # Embed methods
    def generate_main_embed(self):
        embed = discord.Embed(
            title=f"({self.username}) - Main",
            colour=discord.Colour.blue()
        )
        text = f"""
**Mastery Rank**: {self.mastery_rank}
**Clan**: {self.clan}
**Account Created**: {self.account_created}
"""     
        embed.description = text

        return embed
    
    def generate_loadout_embed(self):
        loadout_data = self.generate_loadout()
        embed = discord.Embed(
            title=f"({self.username}) - Loadout",
            colour=discord.Colour.blue()
        )
        text = "Current loadout:\n"
        for key,value in loadout_data.items():
            text += f"**{key}**: {value}\n"

        embed.description = text

        return embed
    
    def generate_fashion_embed(self):
        fashion_data = self.generate_fashion()
        embed = discord.Embed(
            title=f"({self.username}) - Fashion",
            colour=discord.Colour.blue()
        )
        text = f"Current fashion for {fashion_data['name']}"
        embed.description = text

        fashion_parts = ""
        for part in fashion_data['fashion_parts']:
            fashion_parts += f"- {part}\n"
        embed.add_field(name="Fashion parts", value=fashion_parts, inline=False)

        for color_part,color_types in fashion_data.items():
            # they are in the same dictionary so eh...
            if color_part!= "name" and color_part!= "fashion_parts":

                embed.add_field(name=color_part, value="- " + "\n- ".join(color_types), inline=False)

        return embed

    def generate_enemy_embed(self):
        enemy_total_stats = self.enemy_total_stats()
        embed = discord.Embed(
            title=f"({self.username}) - Enemies",
            colour=discord.Colour.blue()
        )
        text = ""
        for stat, amount in enemy_total_stats.items():
            text += f"**{stat}**: {amount}\n"

        embed.description = text

        top_kills = ""
        for rank, enemy in enumerate(self.enemy_top_kills(), start=1):
            enemy_type = enemy["type"]
            kills = enemy.get("kills", 0)
            top_kills +=f"{rank}. {enemy_type}: {kills}\n"

        embed.add_field(name="Top Kills", value=top_kills, inline=False)
        return embed

    def generate_ability_embed(self):
        embed = discord.Embed(
            title=f"({self.username}) - Abilities",
            colour=discord.Colour.blue()
        )
        text = f"**Total Ability Casts**: {self.ability_total_stats}\n"

        embed.description = text

        top_abilities= ""
        for rank, ability in enumerate(self.ability_top_used(), start=1):
            ability_name = find_internal_ability_name(ability["type"], cache)
            usage = ability["used"]
            top_abilities +=f"{rank}. {ability_name}: {usage}\n"
        embed.add_field(name="Top Abilities Used", value=top_abilities, inline=False)

        bottom_abilities= ""
        for rank, ability in enumerate(self.ability_bottom_used(), start=1):
            ability_name = find_internal_ability_name(ability["type"], cache)
            usage = ability["used"]
            bottom_abilities +=f"{rank}. {ability_name}: {usage}\n"
        embed.add_field(name="Least Abilities Used", value=bottom_abilities, inline=False)

        return embed


    def generate_warframe_embed(self):
        embed = discord.Embed(
            title=f"({self.username}) - Warframes",
            colour=discord.Colour.blue()
        )
        sort_types = {
            "equipTime": "Equip Time",
            "xp": "XP",
            "kills": "Kills",
            "assists": "Assists"
        }

        for key, name in sort_types.items():
            top_names = ""
            for rank, warframe in enumerate(self.warframe_top_used_by_type(key), start=1):
                wf_name = find_internal_warframe_name(warframe['type'], cache)
                top_names +=f"{rank}. {wf_name}: {warframe[key]}\n"
            embed.add_field(name=f"Top by {name}", value=top_names, inline=True)

            bottom_names = ""
            for rank, warframe in enumerate(self.warframe_bottom_used_by_type(key), start=1):
                wf_name = find_internal_warframe_name(warframe['type'], cache)
                bottom_names +=f"{rank}. {wf_name}: {warframe[key]}\n"
            embed.add_field(name=f"Bottom by {name}", value=bottom_names, inline=True)

            # empty field hack
            embed.add_field(name="\u200B", value="\u200B", inline=True)



        return embed
    