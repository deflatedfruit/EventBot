from discord.ext import commands
import discord
import datetime as dt
import functools


HELPMESSAGE = """This is a bot by deflatedfruit to manage the server events\n
Commands:
**!event** - List all the events that are currently scheduled
**!event add <date> <time> <description>** - Add an event. Note: dates must be in the format dd/mm/yy and time in the format hh:mm
**!event remove <date> <time>** - Remove the event scheduled for the given date and time
**!event alert** - Message [at]here with any events happening today
**!event help** - Display this help message
**!status <text>** - Set the bot status message. Leave text blank to reset."""

FILE = "events.txt"

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
        return f"**{self.datestring}**:  {self.desc}"

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
    with open(FILE, mode="r+") as file:
        data = file.read().rstrip()
        if len(data) == 0:
            events = []
        else:
            events = [Event.from_str(lst) for lst in data.split("\n")]
    return list(sorted(events))


bot = commands.Bot(command_prefix="!", help_command=None)

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
    elif ctx.command_failed:
        await cts.send(HELPMESSAGE)

@event.command()
async def help(ctx):
    await ctx.send(HELPMESSAGE)

@bot.command()
async def egg(ctx):
    await ctx.send(file=discord.File("egg.jpg"))

@event.command()
@commands.has_role("Events Manager")
async def add(ctx, date, time, *desc):
    try:
        new = Event(f"{date} {time}", ' '.join(desc))
        with open(FILE, mode="a+") as file:
            file.write(repr(new)+"\n")
    except ValueError:
        await ctx.send("Error: Invalid date format. Must be in the form dd/mm/yy hh:mm")
    else:
        await ctx.send(f"Event '{' '.join(desc)}' at {date} {time} created successfully")

@event.command()
@commands.has_role("Events Manager")
async def remove(ctx, date, time):
    events = read_events()
    if len(events) == 0:
        await ctx.send("Error: There are no events to remove")
    else:
        try:
            datetimeobj = dt.datetime.strptime(f"{date} {time}", "%d/%m/%y %H:%M")
        except ValueError:
            await ctx.send("Error: Invalid date format. Must be in the form dd/mm/yy hh:mm")
        else:
            newEvents = []
            for e in events:
                if e.date != datetimeobj:
                    newEvents.append(e)
            if len(newEvents) == len(events):
                await ctx.send("Error: No event at that date and time")
            else:
                with open(FILE, mode="w+") as file:
                    for e in newEvents:
                        file.write(repr(e)+"\n")
                await ctx.send("Event removed successfully")

@event.command()
@commands.has_role("Events Manager")
async def alert(ctx):
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

@bot.command()
@commands.has_role("Events Manager")
async def status(ctx, text="Games | !event help"):
    await bot.change_presence(activity=discord.Game(name=text))


@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")

@status.error
async def status_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")

alert.error
async def alert_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You must have the **Events Manager** role to perform this command")


bot.run("NzAwMzYwNjA4NDQwMjU0NTA2.XpjyrQ.KGnuhKUPV3DTfTV56o4J4Y3-o6E")
