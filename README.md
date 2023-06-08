# Checkmate AI

## Index

-   [Philosophy of CheckmateAI](#philosophy-of-checkmateai)
-   [Current State of the Project](#Current-State-of-the-Project)
    -   [Why are there 2 different branches with distinct functionality in each one of them?](#Why-are-there-2-different-branches-with-distinct-functionality-in-each-one-of-them?)
-   [How to use CheckmateAI](#How-to-use-CheckmateAI)
-   [Future](#Future)

## Philosophy of CheckmateAI

-   With the artificial intelligence boom in 2023, the authors of this project decided to leverage the power of AI (specifically OpenAI's creations) to help users become better learners.
-   We believe in iteratively building a chatbot that we can use to help us initiate novel conversations without needing for an actual human study partner.
-   The eventual goal for this bot is to be able to ignite surprising conversations and generate eureka moments for curious learners.

## Current State of the Project

There are 2 branches in this project:

-   main
    -   The `main` branch has the feature of storing data from Roam Research and initiate conversations based on that.
    -   One can upload Roam export and talk about it with the bot.
-   yt_parse
    -   The `yt_parse` branch has the functionality to summarize YouTube videos and talk about it.

### Why are there 2 different branches with distinct functionality in each one of them?

We're trying to make the bot process knowledge and we decided to do it with 2 different sources of information while building (Roam Research exports, YouTube video transcripts)

As we get closer to feeling that the bot is able to spark up interesting conversations, we'll focus on making it work with more different sources of knowledge and they'll all be available in the `main` branch.

## How to use CheckmateAI

YouTube Summarization / Question-Answering:

1. Clone the repository with `git clone https://github.com/ritiksahni/checkmateAI`
2. Move to the cloned repository: `cd checkmateAI`
3. Switch to `yt_parse` branch.
4. Add `.env` file with the following data:

```env
OPENAI_API_KEY="<OPENAI_API_KEY>"
BOT_TOKEN="<TELEGRAM-BOT-TOKEN>"
```

**Note**: For information on obtaining the bot token, visit https://blog.devgenius.io/how-to-set-up-your-telegram-bot-using-botfather-fd1896d68c02

5. Run `pip3 install -r requirements.txt`
6. Run `python3 main.py`

If you see "Bot Started And Waiting For New Messages", you've successfully executed the program. Text the bot on Telegram that you created with BotFather.

If it doesn't work, **create an issue or reach out to the authors**.

---

## Future

We will make a public version of the bot in the so you won't have to deploy it for yourself once we figure out the base of good AI-generated conversations and user-management on Telegram.

---

Authors:

Ritik Sahni - [Twitter](https://twitter.com/ritiksahni22)

Ziding Zhang - [Twitter](https://twitter.com/ziding?lang=en)
