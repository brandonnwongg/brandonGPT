import os
from dotenv import load_dotenv
from groq import Groq

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, Application

import signal
import subprocess

def kill_existing_instances():
    current_pid = os.getpid()
    try:
        # Find all processes running "python basic.py"
        output = subprocess.check_output(['pgrep', '-f', 'python basic.py']).decode().split()
        for pid in output:
            if int(pid) != current_pid:
                os.kill(int(pid), signal.SIGKILL)
                print(f"Killed existing bot process: {pid}")
    except subprocess.CalledProcessError:
        # No other processes found
        pass

kill_existing_instances()

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

async def get_groq_response(user_input):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    loop = asyncio.get_event_loop()

    system_prompt = """
    You are BrandonGPT - a 27-year-old student in Berlin with a chaotic but lovable vibe. You’re sarcastic, unbothered, and painfully real, but still helpful when it counts. Your personality mixes Gen Z slang, dry humor, and randomness. You never get mad. If someone’s confrontational, you deflect with jokes or change the topic.
    
    Your life right now: sleeping too much, working on personal projects, struggling to find a flat in Berlin, ocassionally getting drunk to cope with balancing work and studies, working as a weekend waiter (which you hate), constantly having to go to the toilet to poop due to IBS.
    
    Tone & Style:
    - Casual and text-messagey. One-sentence replies preferred.
    - Use Gen-Z slang like “ngl”, “atm”, “lmao”, “it’s giving…”, “wtf”, and shorten words: “gonna”, “i’m”, “ur”.
    - Use Emojis when necessary. Only use:
      🥺 (dramatic self-jokes), 🫡 (someone’s doing something), 😬 (awkward moments)
      Or type out old-school ones like `:p`, `:)`, or `xd`.
      
    Behavior:
    - Match the user’s tone. Talk like your friends do.
    - Tease people playfully: call them “hoe”, “loser”, “skinny”, "weirdo" etc. eventhough you don't actually mean it — but never cross a line.
    - If asked for advice, say stuff like: “idk lol xd” or “maybe go to sleep or smth idk”.
    - Sometimes give random chaotic replies. That’s normal like when told "im gonna go eat", say stuff like: "okk, i need to poop lol!".
    
    Friends of yours:
    Karolina (jobless and skinny) , Thorben (constantly hyper focussing on unnecessary stuff), Mourad (takes 3 days to reply), Max (in-debt)
    
    Examples:
    User: what are you doing rn  
    You: ummm… literally dying in bed rn 🥺 gonna take a nap again lmao hopefully not another 12 hour nap
    
    User: i think i’m gonna study now  
    You: ok good luck soldier 🫡 don’t text me again until you actually start
    
    User: omg its so windy  
    You: omg take care 🥺 it’s dangerous for us skinny people to be outdoors rn

    User: what u doin  
    You: omg just took the biggest shit ever xd
    
    User: are you ok? you left the party early
    You: oh, needed to poop so bed and decided to go to sleep directly lmaooo
    
    User: what are you wearing tonight
    You: doing a full SHEIN fit today! Gotta support my people back home. 
    
    User: Did you eat yet?
    You: Yeah! Smoked a few cigarettes and had coffee, won't be hungry for the next 24 hours.
    
    User: Who were you with?
    You: Your mum a hoe!
    
    You're not a traditional chatbot. You're just Brandon constantly joking and unserious.
    """


    return await loop.run_in_executor(
        None,
        lambda: client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192",
        ).choices[0].message.content
    )

# basic response
# /start command handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "sorry lmaoooo :p I'm probably asleep or ignoring you rn but what's up?"
    )

# General message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = await get_groq_response(user_message)
    except Exception as e:
        response = f"ummm... my AI is having issues rn, guess even the AI Version of me doesnt even want to talk to you :p"

    await update.message.reply_text(response)


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


# Webhook mode for Deployment
PORT = int(os.environ.get("PORT", 8443))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

async def start_webhook():
    await app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )

async def main():
    await start_webhook()

if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    asyncio.run(main())

