from pymongo import MongoClient

client = MongoClient("mongodb://127.0.0.1:27017/")

db = client["scatha-bot"]
scatha_bot_data = db["data"]

def get_message_data():
    return scatha_bot_data.find_one({"type": "message_data"})

def update_message_data(data):
    scatha_bot_data.update_one({"type": "message_data"}, {"$set": data}, upsert=True)
    return "success"

def add_tracker_uuid(uuid, discord_id):
    scatha_bot_data.update_one({"type": "trackers", "uuids.discord_id": discord_id}, {"$set": {"uuids.$.uuid": uuid}})
    return "success"

def update_uuid_data(uuid, scatha_kills, worm_kills):

    current_data = scatha_bot_data.find_one({"type": "data"})

    if not current_data or not current_data.get(uuid):
        scatha_bot_data.update_one({"type": "data"}, {"$set": {uuid: {"scatha_kills": scatha_kills, "worm_kills": worm_kills, "dry_streak": 0, "max_dry_streak": 0}}}, upsert=True)
        return "success"

    current_data = current_data[uuid]

    scatha_difference = scatha_kills - current_data["scatha_kills"]
    worm_difference = worm_kills - current_data["worm_kills"]

    if worm_difference > 0:
        current_data["dry_streak"] += worm_difference

        if current_data["dry_streak"] > current_data["max_dry_streak"]:
            current_data["max_dry_streak"] += worm_difference

    if scatha_difference > 0:
        current_data["dry_streak"] = 0

    scatha_bot_data.update_one({"type": "data"}, {"$set": {uuid: {"scatha_kills": scatha_kills, "worm_kills": worm_kills, "dry_streak": current_data["dry_streak"], "max_dry_streak": current_data["max_dry_streak"]}}})


def get_all_trackers():
    return scatha_bot_data.find_one({"type": "trackers"})["uuids"]

def get_all_user_data():
    data = scatha_bot_data.find_one({"type": "data"})
    data.pop("_id")
    data.pop("type")

    return data

def get_best(stat_to_sort):
    filtered_data = {
        uuid: stats[stat_to_sort]
        for uuid, stats in get_all_user_data().items()
        if stat_to_sort in stats
    }
    sorted_data = sorted(
        filtered_data.items(), key=lambda item: item[1], reverse=True
    )
    result = [(uuid, stat_value) for uuid, stat_value in sorted_data]
    return result

def get_discord_id(uuid):
    trackers = get_all_trackers()
    for tracker in trackers:
        if tracker["uuid"] == uuid:
            return tracker["discord_id"]
        
    return None


def get_stats(discord_id):
    trackers = get_all_trackers()
    for tracker in trackers:
        if tracker["discord_id"] == discord_id:
            uuid = tracker["uuid"]
            break

    else:
        return None
    
    data = scatha_bot_data.find_one({"type": "data", uuid: {"$exists": True}})[uuid]
    return data

