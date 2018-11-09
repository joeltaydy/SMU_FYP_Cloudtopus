from datetime import datetime
from background_task import background
from telethon.tl.types import Channel, Chat
from Module_TeamManagement.models import Telegram_Chats
from Module_CommunicationManagement.src import tele_util

@background(schedule=0)
def test_tasks(message):
    print(message)

@background(schedule=0)
def getAllChatMembers(username,chat_type,chat_name):
    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Running background event: Get All Members')

    tele_chat_type = {
        'Channel':Channel,
        'Group':Chat,
    }

    telegram_chat = Telegram_Chats.objects.get(name=chat_name)
    client = tele_util.getClient(username)

    members, count = tele_util.getMembers(client,chat_name,tele_chat_type[chat_type])
    telegram_chat.members = '_'.join(members)
    telegram_chat.save()

    tele_util.disconnectClient(client)

    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Ending background event: Get All Members')

@background(schedule=0)
def sendMessage(username,chat_type,chat_name,message):
    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Running background event: Sending Telegram Message')

    client = tele_util.getClient(username)

    if chat_type == 'Group':
        tele_util.sendGroupMessage(client,chat_name,message)
    elif chat_type == 'Channel':
        tele_util.sendChannelMessage(client,chat_name,message)

    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Sent message to ('+ chat_type +'): ' + chat_name)
    tele_util.disconnectClient(client)

    print('[' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '] Ending background event: Sending Telegram Message')