# Planninger : Python Discord Bot

This bot was made with discord.py.
The aim is to plan events and set reminder more easily.

## Usage

## Remind / Rappel
`!remind/!rappel`

They are multiple syntax that you can use, and the bot will send you a private message when it is time.
- !remind HH:MM Message
`!remind 10:41 Medical Apointment`
- !remind YYYY-MM-DD HH:MM Message
`!remind 2024-07-30 9:00 Going to be hot this day`
- !remind XH/XM Message
`!remind 15m the chicken is chickened`

The command also work with !rappel for the baguette O fromage

### settimezone
`!settimezone`

The bot will probably not be hosted in the same UTC as you.
You will certainly need to setup your personnal time shift with this command.
`!settimezone +4`

(You also can set minus)

### myTime/timeforme
`!myTime`

Use this command to see how the bot see you in term of date/time. This way you can set your time zone with more accuracy
`!myTime`

The bot will answer you with this syntax :
`Pour {USER} il est YYYY-MM-DD HH:MM:SS:uSSSSSS`


## Event Planner 

You also can plan event with the bot, and people can register in the event

### setbottimezone
`!setbottimezone`

This command is used if the bot is not on the same time zone than you, otherwise it will not notify you at the right time.
`!setbottimezone 4`

IMPORTANT SIDENOTE : Since the bot will notify you on an hour depending on one time zone. This mean that if you set the bot to +2 for example, it will notify user from only one time zone since it will not take into account the time zone of users but its own.

### plan
`!plan/!event/!orga`

This command is used to plan an event.
You will need to specify a date and a name for the event.
`!plan 2000-01-01 12:00 kill ender dragon`

This will create an event for the bot, with the hour being the local hour setup with the bot timezone.

### planning
`!planning/!consult/!pg`

Use this command to see all planned event and the number of people that are register for this event.
`!panning`

### register
`!inscr/!register/!rg/!add`

Now you need to register to an event to be notified of the event.
Of course you will need to specify the name of the event you want to attend.
`!register kill ender dragon`

You then will be added to the event and notified when it is time !

### unregister
`!unregister,!unreg,!removeme,!rm`

Also you can quit an event with
`!removeme kill the ender dragon`

### botTime
`!botTime`

Due to the time zone difference that can occurs, you also can check the time the bot is currently seeing.
`!botTime`
You will see something like:
`Pour le bot il est {BOTIME}`

### helpPlan
`!helpPlan`

You also can type `!helpPlan` to have a quick overview of all the command possible.

## FAQ

They shouldn't have any problem but DM me otherwise
