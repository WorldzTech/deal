from .models import Chat


# UserModel.objects.get(mobilePhone='1234')
def start_chat(byUser, toUser, title):
    chat = Chat.objects.create(p1=byUser, p2=toUser, title=title)

    return chat


def send_message(byUser, chat, content):
    if chat:
        if chat.add_message(who=byUser, content=content):
            return True
        else:
            return False
    else:
        return False
