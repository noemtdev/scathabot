from constants import API_KEY
import aiohttp

class Web:
    def __init__(self):
        self.api_key = API_KEY

    async def get_uuid(self, username, aiohttp_session=None):

        if not aiohttp_session:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as response:
                    if response.status == 204:
                        return None
                    
                    data = await response.json()
                    return data["id"], data["name"]
                
        else:
            async with aiohttp_session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as response:
                if response.status == 204:
                    return None
                
                data = await response.json()
                return data["id"], data["name"]
            
    
    async def get_selected_profile(self, uuid, aiohttp_session=None):
        if not aiohttp_session:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.hypixel.net/v2/skyblock/profiles?key={self.api_key}&uuid={uuid}") as response:
                    data = await response.json()

                    if data["success"] == False:
                        return None
                    
                    for profile in data["profiles"]:
                        if profile.get("selected"):
                            return profile
                        
                    return None

        else:
            async with session.get(f"https://api.hypixel.net/v2/skyblock/profiles?key={self.api_key}&uuid={uuid}") as response:
                data = await response.json()

                if data["success"] == False:
                    return None
                
                for profile in data["profiles"]:
                    if profile.get("selected"):
                        return profile
                    
                return None


