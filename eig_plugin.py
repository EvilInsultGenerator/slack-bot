from slackbot.bot import respond_to
from slackbot.bot import listen_to
import sqlite3
import urllib.request
import re
import os.path
import rollbar
import slackbot_settings

rollbar.init(slackbot_settings.ROLLBAR_KEY)

@respond_to('^help', re.IGNORECASE)
def help(message):
    try :
        message.reply('Commands:')
        message.reply('\'generate\': Generates insult')
        message.reply('\'change_lang <lang>\': Change insult language')
        message.reply('\'list_lang\': Lists available languages')
        message.reply('\'help\': Lists available commands')
    except:
        rollbar.report_exc_info()

@respond_to('generate')
def generate(message):
    try :
        lang = sqlite_get_user_lang(message.body['user'])
        req = urllib.request.urlopen('https://evilinsult.com/generate_insult.php?lang='+lang)
        message.reply(req.read())
    except:
        rollbar.report_exc_info()

@respond_to('change_lang (..)')
def change_lang(message, lang):
    supported_languages = ["zh","es","en","hi","ar","pt","bn","ru","ja","jv","sw","de","ko","fr","te","mr","tr","ta","vi","ur","el"]
    
    if lang in supported_languages :
        try :
            sqlite_change_language(message.body["user"], lang)
            message.reply("Language Change Successful")
        except:
            rollbar.report_exc_info()
    else :
        try:
            message.reply("Unsupported language requested.\nPlease view 'list_lang' for a list of supported languages.")
        except:
            rollbar.report_exc_info()

@respond_to('list_lang')
def list_lang(message):
    supported_languages = ["zh","es","en","hi","ar","pt","bn","ru","ja","jv","sw","de","ko","fr","te","mr","tr","ta","vi","ur","el"]
    response = "Supported Languages:\n"
    for lang in supported_languages :
        response = response + lang + "\n"
    try:
        message.reply(response)
    except:
        rollbar.report_exc_info()

def sqlite_get_user_lang(user):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "eig_bot.db")
    conn = sqlite3.connect(db_path)
    sql = "SELECT lang FROM users WHERE user='"+user+"';";
    c = conn.cursor()
    c.execute(sql)
    data=c.fetchone()
    if not data:
        sql = "INSERT INTO users(user, lang) VALUES ('"+user+"', 'en');"
        c.execute(sql)
        conn.commit()
        conn.close()
        return 'en'
    else :
        lang = data[0]
        conn.close()
        return lang

def sqlite_change_language(user, language):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "eig_bot.db")
    conn = sqlite3.connect(db_path)
    sql = "UPDATE users SET lang='" + language + "' WHERE user='"+ user +"';"
    c = conn.cursor()
    c.execute(sql)
    conn.commit()
    conn.close()