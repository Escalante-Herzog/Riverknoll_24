import discord
from datetime import datetime, timedelta
from enum import Enum
from random import randint, choice
import uuid

from collections import deque
from discord.ext import commands
from environs import Env

from discord.ext import tasks, commands

env = Env()
env.read_env()
SUPER_SECRET_API_KEY = env.str("SUPER_SECRET_API_TOKEN")

description = "A simple bot to delegate chores in our house. Originally developed for Riverknoll 24"
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


"""
    Conceptual code that allows
    tasks to have individual histories
    while allowing functionality to be retained.
"""


class Task:
    """
        @:param uuid -> unique 126-bit identifier
        @:param createDate -> instance of datetime created
        @:param daysToAccomplish -> offset of days from createDate
        @:param taskType -> flag for command structure
    """

    def __init__(self, taskId: uuid, createDate: datetime, daysToAccomplishTask: timedelta, taskType=TaskType.NoTask):
        self.taskID = taskId
        self.createDate = createDate
        self.dateOffset = daysToAccomplishTask
        self.taskType = taskType

    def completion_date(self):
        return self.createDate + self.dateOffset

    # TODO validate date
    def addDays(self, days: int) -> bool:
        completion_date = self.createDate + self.dateOffset
        if completion_date > datetime.today():
            self.dateOffset += timedelta(days=days)
            return True
        else:
            print("You have went over the alloted time to complete this task!")
            return False

    # TODO validate date
    def subtractDays(self, days: int) -> bool:
        completion_date = self.createDate + self.dateOffset
        if completion_date > datetime.today():
            delta = timedelta(days=days)
            # check that their is enough buffer from today to completion_date
            tdy = datetime.today()
            if (tdy - delta) > datetime.today():
                self.dateOffset -= timedelta(days=days)
            else:
                print("Sorry but not your falling short on days to procrastinate")
        else:
            print("You have went over the alloted time to complete this task!")

    def __str__(self):
        start_date_str = self.createDate.strftime("%b %d %Y")
        end_date_str = (self.createDate + self.dateOffset).strftime("%b %d %Y")
        return "Task=<TaskId={0},dateCreated={1},dateToAccomplish={2},taskType={3}>" \
            .format(self.taskID, start_date_str, end_date_str, self.taskType.name)


"""
    Handles time deltas that will be important
    in calculating task completion and days left to do task

    @parameter taskType 0 <= [Task(Enum)] <= 3
"""


class TaskScheduler:

    def __init__(self):
        self.task_queue = list()

    # @deprecated("createTask")
    def createAllTasks(self, days: datetime.day):
        # Testing purposes
        for task in self.enumerateTasks():
            task_id = uuid.uuid1()
            now = datetime.now()
            offset = timedelta(days=days)
            task_type = task
            t = Task(task_id, now, offset, task_type)
            self.task_queue.append(t)

    '''
        Optionally returns nextTask of taskType 
        otherwise nextTask in double-ended queue
    '''

    def next_task(self, taskCode):
        if self.task_queue:
            for cnt, task in enumerate(self.task_queue):
                if int(task.taskType.value) == taskCode:
                    return task
        else:
            print("No more tasks in cycle")

    """
        Task has a startDate=datetime.today
        and offsets the alloted time to complete
        :param days -> days to complete task
        :param taskType -> if given useful for commands otherwise TaskType.NoTask
        
        Note: This function only needs to worry about creating taskId's
    """

    def createTask(self, days: datetime.day, taskType=TaskType.NoTask) -> bool:
        task_id = uuid.uuid1()
        now = datetime.now()
        offset = timedelta(days=days)
        if taskType:
            task = Task(task_id, now, offset, taskType)
            self.task_queue.append(task)
            return True
        else:
            task = Task(task_id, now, offset)
            # self.all_tasks.append(task)
            self.task_queue.append(task)
            return True
        return False

    def enumerateTasks(self):
        return [task for task in TaskType]

    def __str__(self):
        repr_str = str()
        cpy = list(self.task_queue)
        while cpy:  # for-each copy
            value = cpy.pop()
            repr_str += str(value) + "\n"
        return str(repr_str)


class HouseMate:

    def __init__(self, user_id, name, guild, nick=None):
        self.user_id = user_id
        self.name = name
        self.guild = guild
        if nick:
            self.nick = nick

    def changeNickname(self, nick: str) -> bool:
        if nick:
            self.nick = nick
            return True
        else:
            return False

    def changeHouse(self, house_name: str) -> bool:
        if house_name:
            self.guild = house_name
            return True
        else:
            return False

    def __str__(self):
        return "<UserId={0},name={1},guild={2}>".format(self.user_id, self.name, self.guild)


class House:

    def __init__(self, house_name):
        self.house_name = house_name
        self.house_mates = list()
        self.task_schedulear = TaskScheduler()

    def mention_member(self):
        pass

    def add_house_member(self, member: HouseMate):
        try:
            if member:
                self.house_mates.append(member)
        except:
            print("Member: {0} could not be added".format(member.name))

    def runAllTasks(self, days):
        self.task_schedulear.createAllTasks(days)

    def schedueleTaskByDay(self, days):
        self.task_schedulear.createTask(days)

    def __str__(self):
        string_repr = str("<House={}".format(self.house_name))
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
    embed.add_field(name="$add_member @mention_user", value="add a member by mentioning them!", inline=False)
    embed.add_field(name="$next arg(Dish, Trash, Room)", value="Returns the date that chore must be accomplished",
                    inline=False)
    embed.add_field(name="$coin_flip", value="Returns odds of being choosen", inline=False)

    await ctx.send(author, embed=embed)


'''
    Usage: @mention conversion to Member object
'''


@bot.command(name="add_member")
async def add_member(ctx, member: discord.Member):
    if member.nick:
        bot.rk24.add_house_member(HouseMate(member.id, member.name, member.guild, member.nick))
    else:
        bot.rk24.add_house_member(HouseMate(member.id, member.name, member.guild))


@bot.command(name="next")
async def next(ctx, taskType=None):
    if taskType is None:
        await ctx.send('No task specified, use {}'.format(bot.rk24.task_schedulear.enumerateTasks()))
    if bot.rk24.task_schedulear.task_queue:
        lower = taskType.lower()
        if lower == "dish" or lower == "dishes":
            task = bot.rk24.task_schedulear.next_task(1)
            await ctx.send("Take out the dishes by: {}".format(task.completion_date().strftime("%m/%d/%Y")))
        if lower == "trash":
            task = bot.rk24.task_schedulear.next_task(2)
            await ctx.send("Take out the trash by: {}".format(task.completion_date().strftime("%m/%d/%Y")))
    else:
        await ctx.send('No more tasks in cycle')


# TODO create registrar form that builds House Object
@bot.command(name="registar")
async def registar(ctx):
    pass


@bot.command(name="coin_flip")
async def coin_flip(ctx):
    try:
        await ctx.send(
            "Coin flip is {0} which has a chance of {1}%" \
                .format(choice(bot.rk24.house_mates), \
                        ((1 / len(bot.rk24.house_mates)) * 100)))
    except IndexError:
        await ctx.send("No-one to choose from")


@bot.command(name="members")
async def members(ctx):
    await ctx.send(str(bot.rk24))


# Global Variable
bot.rk24 = House("Riverknoll_24")

if __name__ == '__main__':
    '''
        Temporary home of things that 
        need to run on their own for memory sake
    '''
    # Below is quick Testsuite
    # Tasks have to be created with the TaskType.EnumName
    bot.rk24.task_schedulear.createTask(12, taskType=TaskType.Trash)
    bot.rk24.task_schedulear.createTask(24, taskType=TaskType.Dishes)
    bot.rk24.task_schedulear.createAllTasks(30)

    print(bot.rk24.task_schedulear.task_queue)
    print(bot.rk24.task_schedulear)
bot.run(SUPER_SECRET_API_KEY)
# EOF
