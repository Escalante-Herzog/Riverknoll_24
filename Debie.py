import discord
from datetime import datetime, timedelta
from enum import Enum
from random import randint
import uuid

from collections import deque
from discord.ext import commands
from environs import Env

from discord.ext import tasks, commands


class ClientHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=10.0)
    async def bulker(self):
        pass


if __name__ == '__main__':
    env = Env()
    env.read_env()
    SUPER_SECRET_API_KEY = env.str("SUPER_SECRET_API_TOKEN")

    description = "A simplebot to delegate chores in our house. Originally developed for Riverknoll24"
    bot = commands.Bot(command_prefix="$", description=description)
    client = ClientHandler(bot) #wrapper for bot


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


class TaskMemento:

    def __init__(self):
        self.task_histories = dict()  # <K=taskId, V=Task<TaskType={0},toBeAccomplishedByDate={1}>

    def createTask(self, taskId, timeDelta):
        pass

    def updateHistory(self, taskId, timeDelta):
        pass


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

    # TODO validate date
    def addDays(self, days: int):
        completion_date = self.createDate + self.dateOffset
        if completion_date > datetime.today():
            self.dateOffset += timedelta(days=days)
        else:
            print("You have went over the alloted time to complete this task!")

    # TODO validate date
    def subtractDays(self, days: int):
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
        self.task_queue = deque()

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
        while self.task_queue:
            value = self.task_queue.pop()
            repr_str += str(value) + "\n"
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
        self.house_name = house_name
        self.house_mates = list()
        self.task_schedulear = TaskScheduler()

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

    """
        Functionality skips task by checking majority along with
        shifting a given point to person
    """

    def skipTask(self, user):
        pass

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
    embed.add_field(name="$Chores", value="Returns entire 4-week cycle of chores", inline=False)
    embed.add_field(name="$Dishes", value="Returns next person to do Dishes", inline=False)
    embed.add_field(name="$Trash", value="Returns next person to do Trash", inline=False)

    await ctx.send(author, embed=embed)


@bot.command(name="time_check")
async def time_check(ctx):
    # target_channel = bot.get_channel("720106934992240651")
    await discord.utils.sleep_until(datetime.now() + timedelta(seconds=10))
    await ctx.send('Clean the dishes')


@bot.command
async def printAll(ctx):
    # Below is quick Testsuite
    rk24 = House("Riverknoll_24")
    mate1 = HouseMate("Marcelo Escalante", "Riverknoll_24")
    mate2 = HouseMate("Nolan Aimes")

    rk24.add_house_member(mate1)
    rk24.add_house_member(mate2)

    # rk24.schedueleTaskByDay(7)  # a week per task
    rk24.runAllTasks(7);
    rk24.task_schedulear.createTask(12)
    printStr = str(rk24.task_schedulear)
    # rk24.skipTask(@mention.DevTest#8726) example

    await ctx.send(printStr)


bot.run(SUPER_SECRET_API_KEY)
# EOF
