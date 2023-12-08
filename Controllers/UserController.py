from Controllers.BaseController import BaseController
from Repositories.UserRepository import UserRepository
from Models.User import User

class UserController(BaseController):
    def __init__(self, html, bot) -> None:
        super().__init__(html)
        self.user = User()
        self.bot = bot
    
    async def start_handler(self, message) -> None:
        await message.answer(
            "Hello, I'm a bot that can help you to find a ride. Please, Share your contact so that we can start.",
            reply_markup=self.ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [
                        self.KeyboardButton(text="Share Contact", request_contact=True, is_persistant=True)
                    ]
                ],
            ),
        )

    async def handle_contact_message(self, message) -> None:
        contact = message.contact
        self.userJson = self.user.createProfile(message.from_user.id, message.from_user.username, contact.first_name, contact.last_name, contact.phone_number)
        await message.answer(
            "Are you a driver or a passenger?",
            reply_markup=self.ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [
                        self.KeyboardButton(text="Driver"),
                        self.KeyboardButton(text="Passenger"),
                    ]
                ],
            ),
        )            

    async def role_handler(self, message) -> None:
        self.userJson = self.user.set_user_role(message.text)
        UserRepository().set(self.user.id, self.userJson)
        await message.answer("Thank you for registration")
    
    async def update_profile_handler(self, message, data):
        if UserRepository().exists(message.from_user.id):
            self.userJson = UserRepository().get(message.from_user.id)
            id = self.userJson["id"]
            username = self.userJson["username"]
            firstName = data["firstName"]
            lastName = data["lastName"]
            phone = data["phone"]
            role = data["role"]
            rides_requested = self.userJson["rides_requested"]
            rides_completed = self.userJson["rides_completed"]

            self.userJson = self.user.update_profile(id, username, firstName, lastName, phone, role, rides_requested, rides_completed)
            
            UserRepository().set(self.user.id, self.userJson)
            user = UserRepository().get(self.user.id)
            await message.answer("Your profile was updated")
            text = ("Profile: \n"+f"First Name: {user['firstName']}\nLast Name: {user['lastName']}\nPhone: {user['phone']}\nRole: {user['role']}\n")
            await message.answer(text=text)
        else:
            await message.answer("You don't have a profile, please register first")
            
    async def get_profile_handler(self, message):
        if UserRepository().exists(message.from_user.id):
            user = UserRepository().get(message.from_user.id)
            text = ("Profile: \n"+f"First Name: {user['firstName']}\nLast Name: {user['lastName']}\nPhone: {user['phone']}\nRole: {user['role']}\n")
            await message.answer(text=text)
        else:
            await message.answer("You don't have a profile, please register first")
    
    async def order_ride_handler(self, message):
        await message.answer("Please share your location",
            reply_markup=self.ReplyKeyboardMarkup(
                resize_keyboard=True,
                keyboard=[
                    [
                        self.KeyboardButton(text="Share Location", request_location=True, is_persistant=True)
                    ]
                ],
            ),                     
        )
    
    async def current_location_handler(self, message):
            self.currentLocation = message.location
            await message.answer("Please select your destination",
                reply_markup=self.ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    keyboard=[
                        [
                            self.KeyboardButton(text="Choose location from map", request_location=True, is_persistant=True),
                        ]
                    ],
                ),                     
            )
    
    async def destination_location_handler(self, message):
        self.destinationLocation = message.location
        await message.answer(f"Your ride was ordered, wait for a driver to contact you...")
        keyboard = self.InlineKeyboardBuilder()
        keyboard.add(self.InlineKeyboardButton(text="Accept", callback_data="accept"))
        keyboard.add(self.InlineKeyboardButton(text="Cancel", callback_data="cancel"))
        drivers = self.get_drivers()
        for driver in drivers:
            await self.bot.send_message(driver["id"], "New ride was ordered, please contact the passenger",
                reply_markup=keyboard.as_markup(),
            )
        self.userId = message.from_user.id
            # await self.bot.send_location(driver["id"], self.currentLocation.latitude, self.currentLocation.longitude)
            # await self.bot.send_location(driver["id"], self.destinationLocation.latitude, self.destinationLocation.longitude)
        
        return True

    async def callback_query_handler(self, callback_query):
        if callback_query.data == "accept":
            return True
        elif callback_query.data == "cancel":
            return False
    
    def get_drivers(self):
        drivers = UserRepository().get_drivers()
        return drivers
    
    async def user_type(self, message):
        self.fromDb = UserRepository().get(message.from_user.id)
        return self.fromDb["role"]

    async def accept_ride_handler(self, flag):
        if flag:
            await self.bot.send_message(self.userId, "Your ride was accepted, please wait for the driver to contact you")
            self.fromDb["rides_requested"].append({"currentLocation": str(self.currentLocation), "destinationLocation": str(self.destinationLocation)})
            UserRepository().set(self.userId, self.fromDb)
        else:
            await self.bot.send_message(self.userId, "Your ride was declined, please try again")
        return flag
    
    
    async def show_history_handler(self, message):
        if UserRepository().exists(message.from_user.id):
            user = UserRepository().get(message.from_user.id)
            if len(user["rides_requested"]) > 0:
                for ride in user["rides_requested"]:
                    await message.answer(f"Current Location: {ride['currentLocation']}\nDestination Location: {ride['destinationLocation']}")
            else:
                await message.answer("You don't have any rides")
        else:
            await message.answer("You don't have a profile, please register first")