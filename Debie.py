from datetime import datetime, timedelta
from enum import Enum
from random import randint

import discord
from discord.ext import commands

"""

"""

SUPER_SECRET_API_KEY = "NOTHING FOR YOU TO SEE"

description = "A simplebot to delegate chores in our house. Originally developed for Riverknoll24"
bot = commands.Bot(command_prefix="$", description=description)


@bot.event
async def on_connect():
    print("Developer Test Server has connected!")


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


@bot.event
async def on_resume():
    print("Session has been resumed")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)


class TaskType(Enum):
    NoTask = 0
    Dishes = 1
    Trash = 2
    Room = 3


class Task:
    def __init__(self, taskType: TaskType, daysToAccomplishTask: datetime):
        self.taskType = taskType
        self.daysToAccomplishTask = daysToAccomplishTask

    def __str__(self):
        dateStartedStr = datetime.today().strftime("%b %d %Y")
        dateFinishedStr = self.daysToAccomplishTask.strftime("%b %d %Y")
        print("Day started task: {0} Day to finish task: {0}".format(dateStartedStr, dateFinishedStr))
        return "<TaskType={0},daysLeft={0}>".format(self.taskType.name, dateFinishedStr)


"""
    Handles time deltas that will be important
    in calculating task completion and days left to do task

    @parameter taskType 0 <= [Task(Enum)] <= 3
"""


class TaskScheduler:

    def __init__(self):
        self.tasks = list()

    """
        Init or change the time designated to finish tasks
    """

    def addDays(self):
        pass

    def subDays(self):
        pass

    def changeDaysToCompleteTasks(self, days: datetime.day) -> bool:
        for task in self.enumerateTasks():
            dayOffset = timedelta(days=days)
            daysToAccomplishTask = datetime.today() + dayOffset
            t = Task(task, daysToAccomplishTask)
            self.tasks.append(t)

    def enumerateTasks(self):
        return [task for task in TaskType]

    def __str__(self):
        repr_str = str()
        for t in list(self.tasks):
            repr_str += str(t) + "\n"
        return str(repr_str)


class HouseMate:

    def __init__(self, legal_name=None, of_house=None):
        self.legal_name = legal_name
        self.of_house = of_house
        self.tasks = list()

        self.nick = str
        if legal_name.split()[0]:
            self.nick = legal_name.split(" ")[0]

    def changeNickname(self, nick: str) -> bool:
        if nick:
            self.nick = nick
            return True
        else:
            return False

    def changeHouse(self, house_name: str) -> bool:
        if house_name:
            self.of_house = house_name
            return True
        else:
            return False

    def __str__(self):
        return "<Housemate={0},nickname={0}>".format(self.legal_name, self.nick)


class House:

    def __init__(self, house_name, users=None):
        self.house_mates = list()
        self.task_schedulear = TaskScheduler()

    def add_house_member(self, member: HouseMate):
        try:
            if member:
                self.house_mates.append(member)
        except:
            print("Member: {0} could not be added".format(member.name))

    def schedueleTaskByDay(self, dayNumber: int):
        self.task_schedulear.changeDaysToCompleteTasks(dayNumber)
        print(self.task_schedulear)

    """
        Functionality skips task by checking majority along with
        shifting a given point to person
    """

    def skipTask(self, user):
        pass

    def __str__(self):
        string_repr = str("<House=")
        for member in list(self.house_mates):
            string_repr += str(member) + "\n"

        return string_repr + ">"


@bot.command(name="commands", description="I am here to help")
async def commands(ctx):
    colors = {
        1: discord.Colour.blue(),
        2: discord.Colour.green(),
        3: discord.Colour.purple(),
        4: discord.Colour.gold()
    }
    author = ctx.message.author
    # Create embed template
    embed = discord.Embed(title="Help", colour=colors[randint(1, 4)])
    # Add to embed template

    embed.set_author(name="Help")
    embed.add_field(name="$Chores", value="Returns entire 4-week cycle of chores", inline=False)
    embed.add_field(name="$Dishes", value="Returns next person to do Dishes", inline=False)
    embed.add_field(name="$Trash", value="Returns next person to do Trash", inline=False)

    await ctx.send(author, embed=embed)


@bot.command(name="$Dishes", description="See whose turn it is to wash dishes")
async def dishes(ctx):
    pass


@bot.command(name="$Skip", description="Skip cycle if majority says its okay")
async def skip(ctx):
    pass


if __name__ == '__main__':
    # Below is quick Testsuite
    rk24 = House("Riverknoll_24")
    mate1 = HouseMate("Marcelo Escalante", "Riverknoll_24")
    mate2 = HouseMate("Nolan Aimes")

    rk24.add_house_member(mate1)
    rk24.add_house_member(mate2)

    rk24.schedueleTaskByDay(7)  # a week per task
    # rk24.skipTask(@mention.DevTest#8726) example

    # print(rk24)

bot.run(SUPER_SECRET_API_KEY)
# EOF
