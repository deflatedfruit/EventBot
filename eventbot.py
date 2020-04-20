from discord.ext import commands
import discord
import datetime as dt
import functools
import asyncio
import sys


HELPMESSAGE = """This is a bot by deflatedfruit to manage the server events\n
Commands:
**!schedule** - List this week's schedule
**!schedule modify <text>** - Set the schedule to text
**!event** - List all the events that are currently scheduled
**!event add <date> <time> <description>** - Add an event. Note: dates must be in the format dd/mm/yy and time in the format hh:mm
**!event remove <date> <time>** - Remove the event scheduled for the given date and time
**!event alert** - Message [at]here with any events happening today
**!event help** - Display this help message
**!status <text>** - Set the bot status message. Leave text blank to reset."""

EVENT_FILE = "events.txt"
SCHED_FILE = "sched.txt"
LOG_FILE = "log.txt"

TOKEN = 'TOKEN'
PREFIX = '!'


@functools.total_ordering
class Event:
    def __init__(self, datestr, desc):
        self.desc = desc
        self.date = self.convert_datetime(datestr)
        self.datestring = self.date.strftime("%H:%MBST  %A %d %B")

    def __repr__(self):
        datestr = self.date.strftime("%d/%m/%y %H:%M")
        return f"{datestr} {self.desc}"

    def __str__(self):
        td = self.date - dt.datetime.now()
        h = td.seconds//3600
        m = (td.seconds//60) % 60
        return f"[In {h}h {m}m]  **{self.datestring}**:  {self.desc}"

    def __lt__(self, other):
        return self.date < other.date

    def __eq__(self, other):
        return self.date == other.date

    @classmethod
    def from_str(cls, string):
        lst = string.split(" ")
        return cls(f"{lst[0]} {lst[1]}", ' '.join(lst[2:]))

    @staticmethod
    def convert_datetime(datetimestr):
        date = dt.datetime.strptime(datetimestr, "%d/%m/%y %H:%M")
        return date

    def has_happened(self):
        return dt.datetime.now() > self.date


def read_events():
    with open(EVENT_FILE, mode="r+") as file:
        data = file.read().rstrip()
        if len(data) == 0:
            events = []
        else:
            events = [Event.from_str(lst) for lst in data.split("\n")]
    return list(sorted(events))


def read_schedule():
    with open(SCHED_FILE, mode="r+") as file:
        return file.read()


def log(type, string):
    now = dt.datetime.now().strftime('%H:%M:%S')
    string = string.replace("\n", "\\n")
    with open(LOG_FILE, mode="a") as file:
        file.write(f"[{now}] [{type}] {string}\n")
    print(f"[{now}] [{type}] {string}")


bot = commands.Bot(command_prefix=PREFIX, help_command=None)

@bot.event
async def on_ready():
    log("INF", "Bot Started")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        log("ERR", str(error))


@bot.command()
@commands.has_role("Events Manager")
async def kill(ctx):
    await ctx.send("Killing...")
    log("INF", "Kill command issued. Terminating...")
    await bot.logout()

@bot.command()
@commands.has_role("Events Manager")
async def status(ctx, text="Games | !event help"):
    await bot.change_presence(activity=discord.Game(name=text))
    log("INF", f"Changing status message to '{text}'")


@bot.group(aliases=["sched"])
async def schedule(ctx):
    if ctx.subcommand_passed is None:
        msg = read_schedule()
        await ctx.send(f"**Schedule:**\n{msg}")
        log("CMD", f"Command 'schedule' called by {ctx.author.name}")

@schedule.command()
@commands.has_role("Events Manager")
async def modify(ctx, *text):
    log("CMD", f"Command 'schedule modify' called by {ctx.author.name}")
    new = []
    for a in text:
        new.append(a.encode("utf-8").decode("unicode_escape"))
    with open(SCHED_FILE, mode="w+") as file:
        file.write(' '.join(new))
    await ctx.send("Schedule updated successfully")
    log("INF", "Schedule changed")
    

@bot.group(aliases=["events"])
async def event(ctx):
    if ctx.subcommand_passed is None:
        events = read_events()
        out = []
        for e in events:
            if not e.has_happened():
                out.append(e)
        outstr = "\n".join([str(e) for e in out])
        await ctx.send(f"The following events are scheduled:\n\n{outstr}\n\nFor timezone conversions, please visit https://www.thetimezoneconverter.com/")
        log("CMD", f"Command 'event' called by {ctx.author.name}")

@event.command()
async def help(ctx):
    await ctx.send(HELPMESSAGE)
    log("CMD", f"Command 'event help' called by {ctx.author.name}")

@event.command()
@commands.has_role("Events Manager")
async def add(ctx, date, time, *desc):
    log("CMD", f"Command 'event add' called by {ctx.author.name}")
    d = ' '.join(desc)
    try:
        new = Event(f"{date} {time}", d)
        with open(EVENT_FILE, mode="a+") as file:
            file.write(repr(new)+"\n")
    except ValueError:
        await ctx.send("Error: Invalid date format. Must be in the form dd/mm/yy hh:mm")
        log("ERR", f"Command 'event add' failed - bad date format")
    else:
        await ctx.send(f"Event '{' '.join(desc)}' at {date} {time} created successfully")
        log("INF", f"Added event '{d}'")

@event.command()
@commands.has_role("Events Manager")
async def remove(ctx, date, time):
    log("CMD", f"Command 'event remove' called by {ctx.author.name}")
    events = read_events()
    if len(events) == 0:
        log("ERR", f"Command 'event remove' failed due to empty events file")
        await ctx.send("Error: There are no events to remove")
    else:
        try:
            datetimeobj = dt.datetime.strptime(f"{date} {time}", "%d/%m/%y %H:%M")
        except ValueError:
            await ctx.send("Error: Invalid date format. Must be in the form dd/mm/yy hh:mm")
            log("ERR", f"Command 'event remove' failed - bad date format")
        else:
            newEvents = []
            for e in events:
                if e.date != datetimeobj:
                    newEvents.append(e)
            if len(newEvents) == len(events):
                await ctx.send("Error: No event at that date and time")
                log("ERR", f"Command 'event remove' failed - no event at given date")
            else:
                with open(EVENT_FILE, mode="w+") as file:
                    for e in newEvents:
                        file.write(repr(e)+"\n")
                await ctx.send("Event removed successfully")
                log("INF", f"Removed event[s] at {date} {time}")

@event.command()
@commands.has_role("Events Manager")
async def alert(ctx):
    log("CMD", f"Command 'event alert' called by {ctx.author.name}")
    events = read_events()
    today = []
    for e in events:
        if e.date.date() == dt.datetime.now().date():
            today.append(e)
    if len(today) == 0:
        await ctx.send("There are no events scheduled for today")
    elif len(today) == 1:
        await ctx.send(f"@here Join us at {event.datestring} for {event.desc}!")
    elif len(today) > 1:
        out = '\n'.join([f"**{event.date.strftime('%H:%M')}**: {event.desc}" for event in today])
        await ctx.send(f"@here We have {len(today)} events today:\n{out}")


@kill.error
async def kill_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")

@status.error
async def status_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")


@modify.error
async def modify_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")


@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")

alert.error
async def alert_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")


bot.run(TOKEN)
