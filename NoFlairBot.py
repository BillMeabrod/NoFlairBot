import praw
import google.generativeai as genai
import os
import time
import logging
import json

STATE_FILE = "bot_state.json"

def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {k: set(v) for k, v in data.get("replied_users", {}).items()}, set(data.get("final_reply_posted", [])), data.get("violation_counts", {})
    except Exception:
        return {}, set(), {}

def save_state():
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "replied_users": {k: list(v) for k, v in replied_users.items()},
            "final_reply_posted": list(final_reply_posted),
            "violation_counts": violation_counts
        }, f, indent=2)

# Reddit API Credentials
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="NoFlairResponder by /u/ObeseBumblebee",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

subreddit = reddit.subreddit("NBAWestMemeWar")

replied_users, final_reply_posted, violation_counts = load_state()

# Configure the logger
logging.basicConfig(
    filename='log.txt',          
    level=logging.INFO,          
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logging.info("NoFlairBot has booted up and is monitoring the chaos.")
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Rate limiting variables - We don't want to ping the Google API too much. Lets keep this free.
requests_per_thread = 3
violation_limit_before_pinned_comment = 10
requests_per_minute = 5
requests_per_day = 250
minute_counter = 0
daily_counter = 0
minute_reset_time = time.time() + 60  # Reset every minute
daily_reset_time = time.time() + 86400  # Reset every 24 hours

def respond_to_unflaired_comments():
    global minute_counter, daily_counter, minute_reset_time, daily_reset_time

    bot_username = "NoFlairBot"
    subreddit_name = "NBAWestMemeWar"
    prompt_template = """you are a member of a west coast NBA trash-talking subreddit. Users of this subreddit are expected to have a flair to show what team they root for. If they don't, they are considered a coward who doesn't want to say what team they root for. A user named "/u/{username}" has just posted without a flair. They said "{usermessage}" I want you to roast them mercilessly. Make them regret posting flairless. Be brutal, but witty. Use curse words like fuck and shit. Use playground insults, everything is on the table. Their sex life, their ugly face, their mama, whatever you can to make them cry. Do not use homophobic or racist slurs. Always come back to them being flairless. Use short sentences, and mock their username. Do not repeat any part of their message. Push them to flair up or leave. Keep it entertaining and competitive, and most importantly, funny. Keep your response to 2 rapid fire insult sentences."""

    for comment in subreddit.stream.comments(skip_existing=True):  
        post_id = comment.submission.id  
        user_id = comment.author.name  
        user_flair = comment.author_flair_text 
        post_age_days = (time.time() - comment.submission.created_utc) / 86400  # Convert seconds to days

        # Rate limit checks
        current_time = time.time()
        if current_time >= minute_reset_time:
            minute_counter = 0
            minute_reset_time = current_time + 60

        if current_time >= daily_reset_time:
            daily_counter = 0
            daily_reset_time = current_time + 86400

        if minute_counter >= requests_per_minute:
            logging.warning(f"⚠️ Rate limit hit: Max {requests_per_minute} requests per minute reached.")
            time.sleep(max(0, minute_reset_time - current_time))
            continue

        if daily_counter >= requests_per_day:
            logging.warning(f"⚠️ Rate limit hit: Max {requests_per_day} requests per day reached.")
            time.sleep(max(0, daily_reset_time - current_time))
            continue

        if post_id not in replied_users:
            replied_users[post_id] = set()
        
        if post_id not in violation_counts:
            violation_counts[post_id] = 0

        logging.info(f"""Comment from {user_id} with flair "{user_flair}": "{comment.body}". """)
        try:
            # Skipping conditions
            if not user_id:
                logging.info("Skipped comment with deleted user.")
                continue
            if post_id in final_reply_posted:
                continue
            if user_flair:
                logging.info(f"Skipped {user_id} because they have a flair")
                continue
            if user_id in replied_users[post_id]:
                logging.info(f"Skipped {user_id} because they were already replied to.")
                continue
            if user_id == bot_username:                
                continue  
            if "bot" in user_id.lower():
                logging.info(f"Skipped {user_id} because they might be a bot.")
                continue              
            if "modteam" in user_id.lower():
                logging.info(f"Skipped {user_id} because they might be a mod team comment.")
                continue
            if post_age_days > 7:
                logging.info(f"Skipped {user_id} because the post is older than 7 days.")
                continue  

            # Increment violation count for this thread
            violation_counts[post_id] += 1
            logging.info(f"Violation count for thread {post_id}: {violation_counts[post_id]}")

            # Only reply to the first few violators 
            if len(replied_users[post_id]) < requests_per_thread:
                # Generate AI response
                prompt = prompt_template.format(username=comment.author.name, usermessage=comment.body)
                response = model.generate_content(prompt)

                if not response or not hasattr(response, "text") or "error" in response.text.lower():
                    logging.info(f"Skipping response due to API error.")
                    continue  

                # Reply to the comment
                disclaimer = f"\n\n*I am a bot, and this action was performed automatically. You won't be replied to again in this thread. Please [add a user-flair](https://www.reddit.com/r/NBAWestMemeWar/comments/1m6tm99/heres_a_tutorial_on_how_to_create_a_custom_flair/) to follow subreddit rules. [Contact the moderators](https://www.reddit.com/message/compose/?to=/r/{subreddit_name}) if you have questions.*"
                bot_reply = comment.reply(response.text + disclaimer)
                bot_reply.mod.distinguish()            
                
                # Mark user as replied
                replied_users[post_id].add(user_id)

                # Update rate counters
                minute_counter += 1
                daily_counter += 1
            else:
                logging.info(f"Skipped replying to {user_id} - already replied to 3 users in this thread")
            
            # Post final pinned message if violation limit is hit.
            if violation_counts[post_id] >= violation_limit_before_pinned_comment and post_id not in final_reply_posted:
                final_message = (
                    "I'm pinning this because this entire thread is a fucking cesspool of flairless cowards. "
                    "Let's be clear: nobody gives a shit about your worthless opinion if you're too scared to show your team's logo. "
                    "Either go to the sidebar and pick a team, or get the fuck out of here. If your team isn't in the list, edit one of the flairs or go back to your filthy eastern subreddit."
                    f"\n\n*I am a bot, and this action was performed automatically. You won't be replied to again in this thread. Please [add a user-flair](https://www.reddit.com/r/NBAWestMemeWar/comments/1m6tm99/heres_a_tutorial_on_how_to_create_a_custom_flair/) to follow subreddit rules. "
                    f"[Contact the moderators](https://www.reddit.com/message/compose/?to=/r/{subreddit_name}) if you have questions.*"
                )
                final_comment = comment.submission.reply(final_message)
                final_comment.mod.distinguish(sticky=True)
                final_reply_posted.add(post_id)
                logging.info(f"Posted final pinned comment in thread {post_id}")

            save_state()

        except Exception as e:
            logging.error(f"Error processing comment from {user_id}: {str(e)}")  
            continue  

while True:
    respond_to_unflaired_comments()
    time.sleep(60)