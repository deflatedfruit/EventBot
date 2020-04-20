# EventBot
Events manager for Discord

An 'event' is a one-off item that happens at a specific date and time
The 'schedule' is simply a multiline string that is intended to contain any repeating events [TODO: Add support for repeating events and remove !schedule]

Commands:  
!schedule - List this week's schedule  
!schedule modify <text> - Set the schedule to text  
!event - List all the events that are currently scheduled  
!event add <date> <time> <description> - Add an event. Note: dates must be in the format dd/mm/yy and time in the format hh:mm  
!event remove <date> <time> - Remove the event scheduled for the given date and time  
!event alert - Message [at]here with any events happening today  
!event help - Display this help message  
!status <text> - Set the bot status message. Leave text blank to reset.  
!kill - Terminate the bot 
  
  
Aliases:  
event: events  
schedule: sched  
  
If anyone knows how to schedule messages, please tell.

