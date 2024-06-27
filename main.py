import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Liste des rappels
reminders = []
timezones = {}


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    check_reminders.start()


@bot.command(name='settimezone')
async def set_timezone(ctx, offset: int):
    """
    Définit le décalage horaire de l'utilisateur en heures.
    Utilisation : !settimezone offset (ex: !settimezone 2 pour UTC+2)
    """
    timezones[ctx.author.id] = offset
    await ctx.send(
        f'Décalage horaire défini à {offset} heures pour {ctx.author}.')


@bot.command(name='rappel')
async def set_reminder(ctx, *args):
    message = ""
    time_str = ""
    date_str = ""
    """
    Définit un rappel.
    Utilisation :
    - !rappel HH:MM Message du rappel (pour un rappel aujourd'hui)
    - !rappel YYYY-MM-DD HH:MM Message du rappel (pour un rappel à une date spécifique)
    """
    if len(args) < 2:
        await ctx.send(
            'Utilisation correcte : !rappel HH:MM Message ou !rappel YYYY-MM-DD HH:MM Message'
        )
        return

    if len(args) == 2:
        time_str, message = args[0], args[1]
        date_str = None
    elif len(args) > 2:
        date_str, time_str = args[0], args[1]
        message = ' '.join(args[2:])

    try:
        user_timezone = timezones.get(ctx.author.id, 0)

        if date_str is None:
            # Cas où seule l'heure est fournie
            reminder_time = datetime.strptime(time_str, '%H:%M').time()
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
            f'Rappel défini pour {reminder_datetime.strftime("%Y-%m-%d %H:%M")} (votre fuseau).'
        )
    except ValueError:
        await ctx.send(
            'Format de date ou d\'heure invalide. Utilisation correcte : !rappel HH:MM Message ou !rappel YYYY-MM-DD HH:MM Message'
        )


@tasks.loop(seconds=60)  # Vérifie les rappels toutes les minutes
async def check_reminders():
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


bot.run(os.environ["TOKEN"])
