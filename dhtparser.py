from datetime import datetime


def parse(filepath):
    """Takes the filepath of a text file produced by DHT and returns an instance of Channel with
    a list of users and messages, as well as metadata about the channel"""
    with open(filepath) as file:
        data = eval(file.read())
    meta = data['meta']
    users = []
    for userID, user in meta['users'].items():
        users.append(User(userID=int(userID), name=user['name']))
    userindex = meta['userindex']
    type = meta['servers'][0]['type']
    name = meta['servers'][0]['name']
    data = data['data']
    channelID = int(list(data.keys())[0])
    messages = MessageList()
    for messageID, message in data[str(channelID)].items():
        try:
            text = message['m']
        except KeyError:
            text = ""
        user = search(users, 'userID', int(userindex[message['u']]))
        time = datetime.fromtimestamp(message['t'] / 1000)
        messages.append(Message(messageID, text, time, user))
    messages.sort(key=lambda x: x.time)
    return Channel(channelID, users, messages, name, type)


def search(lst, attr, value):
    """Search a list of objects for ones that have a common attribute"""
    for item in lst:
        if getattr(item, attr) == value:
            return item


class Channel:
    """Represents a single channel / DM in Discord.
    channelID - 18-digit integer that uniquely represents that channel interally in Discord
    users     - List of User objects, representing everyone who is in the channel
    messages  - Instance of MessageList, contains every message sent in the channel
    name      - The name of the channel
    type      - The channel type (eg. DM)"""
    def __init__(self, channelID, users, messages, name, type):
        self.channelID = channelID
        self.users = users
        self.messages = messages
        self.name = name
        self.type = type

    def __repr__(self):
        return f"<Channel:{self.name}, Type:{self.type}>"
    
    def find_user(self, name, strict=True, case=False):
        """Find a user (or users) with the name 'name'. If strict=True, then only exact matches will be returned,
        otherwise any user containing the substring 'name' will be returned. If case=True, then matching will be
        case sensitive"""
        out = []
        for user in self.users:
            if strict:
                if case:
                    if name == user.name:
                        out.append(user)
                else:
                    if name.lower() == user.name.lower():
                        out.append(user)
            else:
                if case:
                    if name in user.name:
                        out.append(user)
                else:
                    if name.lower() in user.name.lower():
                        out.append(user)
        return out

    def find_user_by_id(self, id):
        """Find a user given by the unique 18-digit ID"""
        for user in self.users:
            if user.userID == id:
                return user


class User:
    """Represents a single user in Discord
    userID    - 18-digit integer that uniquely represents that user interally in Discord
    name      - The name of the user. Note: does NOT include the 4 digit tag
    shortname - Attempts to shorten the name by removing anything after the first space or hyphen. Limited usefulness
    """
    def __init__(self, userID, name):
        self.userID = userID
        self.name = name
        self.shortname = name.split(" ")[0].split("-")[0]

    def __repr__(self):
        return f"<User:'{self.name}'>"


class MessageList(list):
    """A list of Message objects, with methods to select messages based on criteria"""
    def __init__(self):
        super().__init__()

    def get_messages_from(self, user):
        """Get messages sent by 'user'"""
        out = MessageList()
        for message in self:
            if message.user == user:
                out.append(message)
        return out

    def get_messages_on(self, date):
        """Get messages sent on the day 'date'. Note: 'date' must be a datetime.date object"""
        out = MessageList()
        for message in self:
            if message.time.date() == date:
                out.append(message)
        return out

    def get_messages_between(self, fromdate, todate):
        """Get messages sent between 'fromdate' and 'todate'. Note: both attributes must be datetime.datetime objects"""
        out = MessageList()
        for message in self:
            if fromdate <= message.time < todate:
                out.append(message)
        return out

    def get_messages_with(self, substring, case=False):
        """Get messages containing 'substring'. Use case=True for case-sensitive searching"""
        out = MessageList()
        if case:
            for message in self:
                if substring:
                    out.append(message)
        else:
            for message in self:
                if substring.lower() in message.text.lower():
                    out.append(message)
        return out

    def get_messages_with_only(self, string, case=False):
        """Get messages that are exclusively 'string'. Use case=True for case-sensitive searching"""
        out = MessageList()
        if case:
            for message in self:
                if message.text == string:
                    out.append(message)
        else:
            for message in self:
                if message.text.lower() == string.lower():
                    out.append(message)
        return out


class Message:
    """Represents a single message sent by a user
    messageID - 18-digit integer that uniquely represents that message interally in Discord
    text      - The text of the message
    time      - The time that message was sent as a datetime.datetime object
    user      - The USer object that sent the message
    """
    def __init__(self, messageID, text, time, user):
        self.text = text
        self.time = time
        self.user = user

    def __repr__(self):
        return f"<Message:'{self.text}', User:{self.user}, Time:{self.time}>"

    def __str__(self):
        return self.text
