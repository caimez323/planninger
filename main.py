import discord, os, re
from discord.ext import commands, tasks
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

reminders = []
timezones = {}
events = {}
bot_timezone_offset = 0


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    check_reminders.start()


#Pas d'utilité ???
@bot.command(name='setbottimezone')
async def set_bot_timezone(ctx, offset: int):
    """
    Définit le décalage horaire du bot en heures.
    Utilisation : !setbottimezone offset
    """
    global bot_timezone_offset
    bot_timezone_offset = offset
    await ctx.send(f'Décalage horaire du bot défini à {offset} heures.')


@bot.command(name='settimezone')
async def set_timezone(ctx, offset: int):
    """
    Définit le décalage horaire de l'utilisateur en heures.
    Utilisation : !settimezone offset +-
    """
    timezones[ctx.author.id] = offset
    await ctx.send(
        f'Décalage horaire défini à {offset} heures pour {ctx.author}.')


@bot.command(name="timeforme", aliases=['myTime'])
async def currentTime(ctx):
    user_timezone = timezones.get(ctx.author.id, 0)
    currentT = datetime.now()
    currentT -= timedelta(hours=user_timezone)
    await ctx.send("Pour {} il est {}".format(ctx.author, currentT))


def parse_duration(duration: str):  #Return timedelta
    match = re.match(r'(\d+)([HhMm])', duration)
    if not match:
        return None
    amount, unit = match.groups()
    amount = int(amount)
    if unit.lower() == 'h':
        return timedelta(hours=amount)
    elif unit.lower() == 'm':
        return timedelta(minutes=amount)
    return None


@bot.command(name='rappel', aliases=['remind'])
async def set_reminder(ctx, *args):
    """
    Définit un rappel.
    - !rappel HH:MM Message du rappel (pour un rappel aujourd'hui)
    - !rappel YYYY-MM-DD HH:MM Message du rappel (pour un rappel à une date spécifique)
    - !rappel 1H Message du rappel (pour un rappel dans 1 heure)
    """
    duration_or_time, date_str, time_str, message = "", "", "", ""
    if len(args) < 2:
        await ctx.send(
            'Format : !rappel HH:MM Message ou !rappel YYYY-MM-DD HH:MM Message ou !rappel 1H Message'
        )
        return

    if len(args) == 2:
        duration_or_time, message = args[0], args[1]
        date_str = None
    elif len(args) > 2:
        date_str, time_str = args[0], args[1]
        message = ' '.join(args[2:])

    try:
        user_timezone = timezones.get(ctx.author.id, 0)

        if date_str is None:
            # Cas où une durée ou une heure seule est fournie
            duration = parse_duration(duration_or_time)
            if duration:
                now = datetime.utcnow() + timedelta(hours=user_timezone)
                reminder_datetime = now + duration
            else:
                reminder_time = datetime.strptime(duration_or_time,
                                                  '%H:%M').time()
                now = datetime.utcnow() + timedelta(hours=user_timezone)
                reminder_datetime = datetime.combine(now.date(), reminder_time)
                if reminder_datetime < now:
                    reminder_datetime += timedelta(days=1)
        else:
            # Cas où une date complète est fournie
            reminder_datetime = datetime.strptime(f"{date_str} {time_str}",
                                                  '%Y-%m-%d %H:%M')
            reminder_datetime -= timedelta(hours=user_timezone)

        reminders.append((reminder_datetime, ctx.author, message))
        await ctx.send(
            f'Rappel défini pour {reminder_datetime.strftime("%Y-%m-%d %H:%M")} (Heure locale).'
        )
    except ValueError:
        await ctx.send(
            'Format de date ou d\'heure invalide. Utilisation correcte : !rappel HH:MM Message ou !rappel YYYY-MM-DD HH:MM Message ou !rappel 1H Message ou !rappel 10m Message'
        )


@tasks.loop(seconds=60)  # Fonction qui se lance toutes les minutes
async def check_reminders():

    #Rappel
    now = datetime.utcnow()  # Utiliser l'heure UTC pour les rappels
    to_remove = []
    for reminder in reminders:
        reminder_time, user, message = reminder
        if now >= reminder_time:
            try:
                await user.send(f'C\'est l\'heure de votre rappel : {message}')
                to_remove.append(reminder)
            except discord.HTTPException as e:
                print(f'Erreur lors de l\'envoi du rappel : {e}')

    # Supprime les rappels envoyés
    for reminder in to_remove:
        reminders.remove(reminder)

    #Events

    now = datetime.utcnow()
    to_remove = []

    for event_name, details in events.items():
        event_datetime = details['datetime']
        if now >= event_datetime:
            attendees = details['attendees']
            channel = discord.utils.get(bot.get_all_channels(), name='flappy')
            if channel:
                mention_list = ' '.join(
                    [f"<@{user_id}>" for user_id in attendees])
                await channel.send(
                    f"C'est l'heure de l'événement '{event_name}'! {mention_list}"
                )
            to_remove.append(event_name)

    # Supprime les événements passés en dehors de la boucle d'itération
    for event_name in to_remove:
        del events[event_name]


@bot.command(name='plannif', aliases=['event', 'orga', 'plan'])
async def plan_event(ctx, day: str, time: str, *, event_name: str):
    """
    Planifie un nouvel événement.
    Utilisation : !plan YYYY-MM-DD HH:MM EVENTNAME
    """
    try:
        event_datetime = datetime.strptime(f"{day} {time}", '%Y-%m-%d %H:%M')
        # Appliquer le décalage horaire du bot ici
        event_datetime -= timedelta(hours=bot_timezone_offset)
        if event_name in events:
            await ctx.send(f"Un événement nommé '{event_name}' existe déjà.")
            return

        events[event_name] = {'datetime': event_datetime, 'attendees': []}
        # Afficher l'heure locale en prenant en compte le décalage horaire du bot
        # Le pb c'est que ça affiche l'heure de prévu.
        # Le bot lui est décallé en vérité mais bon
        # TODO a corriger
        display_time = event_datetime + timedelta(hours=bot_timezone_offset)
        await ctx.send(
            f"Événement '{event_name}' planifié pour le {display_time.strftime('%Y-%m-%d %H:%M')} (heure locale)."
        )
    except ValueError:
        await ctx.send(
            "Format de date ou d'heure invalide. Utilisation correcte : !plan YYYY-MM-DD HH:MM EVENTNAME"
        )


@bot.command(name='planning', aliases=['consult'])
async def consult_events(ctx):
    """
    Consulte les événements planifiés.
    Utilisation : !planning
    """
    if not events:
        await ctx.send("Aucun événement planifié.")
        return

    message = "Événements planifiés :\n"
    for event_name, details in events.items():
        event_datetime = details['datetime']
        # Afficher l'heure locale en prenant en compte le décalage horaire du bot
        display_time = event_datetime + timedelta(hours=bot_timezone_offset)
        attendees = details['attendees']
        message += f"- {event_name} : {display_time.strftime('%Y-%m-%d %H:%M')} (heure locale) (Participants : {len(attendees)})\n"

    await ctx.send(message)


#Todo add pour se désinscrire
@bot.command(name='inscr',aliases=['register','add'])
async def register_event(ctx, event_name: str):
    """
    S'inscrire à un événement.
    Utilisation : !register_event EVENTNAME inscription
    """
    if event_name not in events:
        await ctx.send(f"Événement '{event_name}' non trouvé.")
        return

    event = events[event_name]
    if ctx.author.id in event['attendees']:
        await ctx.send(f"Vous êtes déjà inscrit à l'événement '{event_name}'.")
        return

    event['attendees'].append(ctx.author.id)
    await ctx.send(f"Vous êtes inscrit à l'événement '{event_name}'.")


@bot.command(name="botTime")
async def displayBotTime(ctx):
    currentT = datetime.now()
    currentT -= timedelta(hours=bot_timezone_offset)
    await ctx.send("Pour le bot il est {}".format(currentT))


#######
token = os.getenv("DISCORD_TOKEN") or os.environ['TOKEN'] or ""
bot.run(token)
