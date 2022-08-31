# NamjaNinjaBot
NamjaNinjaBot is a Telegram bot buddy for Soka Gakkai Singapore (SGS) NDP 2022 participants to obtain NDP training and meeting details easily and quickly.\
 \
Currently, the participants need to obtain information of trainings, meetings and encouragements from different sources such as trainers or websites. NamjaNinjaBot aims to streamline that by providing a central place for participants to obtain all the necessary information easily.\
 \
Frontend: Telegram App\
Backend: Django\
Database: MySQL\
 \
Click [here](https://t.me/NamjaNinjabot) to open Telegram and view the bot.\
 \
This github repository contain the codes used to create the frontend of the Telegram bot.

## Commands

* /start: Lists all the queries NamjaNinjaBot can help with
* /about: Learn more about NamjaNinjaBot
* /feedback: Allow users to provide feedback about the bot
* /help: Provides users with the list of commands that they can use
* /share: Generates a message to allow users to share the bot with other participants
* /cancel: Escape login or feedback conversation

## Features

* Users need to key in a valid participant code before allowing them to send queries to the bot
* User will be blocked for continuous incorrect participant code entry
* Logging of important activities for NamjaNinjaBot performance monitoring and to ensure that the bot is used for its intended purpose only
* Users can provide feedback to the bot
* List of queries:
  * Next NDP activity? - Shows the upcoming NDP activity along with details such as what to bring, attire to wear, zoom link, or things to note
  * Show all NDP activities - Shows the full list of upcoming NDP activities
  * Zoom link? - Gives the zoom link used for virtual trainings or meetings
  * Countdown - Shows the time left to the next NDP activity and NDP 2022
  * Daily encouragement - Provides daily encouragement based on [Soka Global Website](https://www.sokaglobal.org/)
  * Last updated? - Shows which updated training schedule NamjaNinjaBot was based on

## Source

NamjaNinjaBot utilises data obtained from NDP 2022 organising committee, [Soka Global Website](https://www.sokaglobal.org/) and NDP 2022 [Soka Gakkai Singapore (SGS)](https://sokasingapore.org/) Committee and Trainers.

## Author

**Foong Zhi Yu**\
GitHub: [foongzy](https://github.com/foongzy)\
LinkedIn: [foong-zhi-yu](https://www.linkedin.com/in/foong-zhi-yu/)

## License

NamjaNinjaBot is released under the MIT License. You can view the license [here](https://github.com/foongzy/NamjaNinjaBot/blob/master/LICENSE.txt).
