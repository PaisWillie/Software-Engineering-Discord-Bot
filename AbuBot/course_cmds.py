import discord
from AbuBot.course_module import Course
from discord.ext import commands
from addons.prefixed_cog import prefixed_cog

course_mod = Course()

@prefixed_cog
class GetCourses(commands.Cog):
     def __init__(self, bot):
          self.bot = bot

     @commands.command()
     async def course(self, ctx, dept, code):
          course_data = course_mod.find_course(dept+" "+code)
          if course_data == "Error":
               await ctx.send(f"Failed to retrieve course data for {str(dept+' '+code).upper()}")
          else:
               embed = discord.Embed(title=course_data[0], color=discord.Color.purple(), description=course_data[2]+'\n\n'+course_data[1]+"; "+course_data[3])
               if course_data[4]:
                    embed.add_field(name="Other Info", value=course_data[4])
               await ctx.send(embed=embed)
          if isinstance(ctx.channel, discord.channel.DMChannel):
               print(f"{ctx.author.name} ran command {ctx.message.content} in private messages.")
          else:
               print(f"{ctx.author.name} ran command {ctx.message.content} in {ctx.guild.name}.")


     @commands.command()
     async def search(self, ctx, *query):
          course_list = course_mod.search_for_course(query)
          courses = "\n".join(course_list)
          if len(courses) > 1950:
               await ctx.send(f"Please provide a more specific query. `{' '.join(query)}` provided too many results to display.")
          elif len(courses) == 0:
               await ctx.send(f"`{' '.join(query)}` returned no results. Please ensure you are typing full words that appear in the course name (eg. \"discrete mathematics\" vs. \"discrete math\")")
          else:
               embed = discord.Embed(title=f"Courses Containing Keyword(s) `{', '.join(query)}`", color=discord.Color.blue(), description=courses)
               await ctx.send(embed=embed)
          if isinstance(ctx.channel, discord.channel.DMChannel):
               print(f"{ctx.author.name} ran command {ctx.message.content} in private messages.")
          else:
               print(f"{ctx.author.name} ran command {ctx.message.content} in {ctx.guild.name}.")

     @commands.command()
     async def reqs(self, ctx, dept, code):
          course_data = course_mod.find_course(dept+" "+code)
          if course_data == "Error":
               await ctx.send(f"Failed to retrieve prerequisite data for {str(dept+' '+code).upper()}")
          else:
               embed = discord.Embed(title=f"Requisites/Info for {course_data[0]}", color=discord.Color.blue(), description=course_data[4] if course_data[4] else "Not Available")
               await ctx.send(embed=embed)
          if isinstance(ctx.channel, discord.channel.DMChannel):
               print(f"{ctx.author.name} ran command {ctx.message.content} in private messages.")
          else:
               print(f"{ctx.author.name} ran command {ctx.message.content} in {ctx.guild.name}.")
