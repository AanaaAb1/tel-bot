from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.keyboards.main_menu import main_menu
from app.database.session import SessionLocal
from app.models.user import User
import random
from datetime import datetime, timedelta

# Sample community posts and discussions
COMMUNITY_POSTS = [
    {
        "id": 1,
        "title": "Study Tips for Mathematics",
        "author": "Student_Alex",
        "content": "I found that practicing problem sets daily really helps improve mathematical thinking!",
        "likes": 15,
        "comments": 3,
        "category": "Study Tips"
    },
    {
        "id": 2,
        "title": "Biology Lab Techniques",
        "author": "BioLover",
        "content": "Share your favorite lab techniques and safety tips here!",
        "likes": 8,
        "comments": 5,
        "category": "Biology"
    },
    {
        "id": 3,
        "title": "Physics Formula Mastery",
        "author": "PhysicsFan",
        "content": "What's the best way to memorize complex physics formulas?",
        "likes": 12,
        "comments": 7,
        "category": "Physics"
    },
    {
        "id": 4,
        "title": "Chemistry Reactions Help",
        "author": "ChemStudent",
        "content": "Need help with organic chemistry reactions. Any resources?",
        "likes": 6,
        "comments": 4,
        "category": "Chemistry"
    },
    {
        "id": 5,
        "title": "Social Science Discussion",
        "author": "SocialScholar",
        "content": "Let's discuss current events and their impact on society!",
        "likes": 20,
        "comments": 12,
        "category": "Social Science"
    }
]

# Study groups information
STUDY_GROUPS = [
    {
        "id": 1,
        "name": "Mathematics Study Group",
        "description": "Daily math practice and problem solving",
        "members": 25,
        "subject": "Mathematics"
    },
    {
        "id": 2,
        "name": "Biology Discussion Circle",
        "description": "Biology concepts and lab work discussions",
        "members": 18,
        "subject": "Biology"
    },
    {
        "id": 3,
        "name": "Physics Explorers",
        "description": "Physics theories and practical applications",
        "members": 22,
        "subject": "Physics"
    },
    {
        "id": 4,
        "name": "Social Science Forum",
        "description": "Current events and social analysis",
        "members": 30,
        "subject": "Social Science"
    }
]

async def community_menu(update, context):
    """Display the community main menu"""
    try:
        message_text = "👥 **Community Hub**\n\n"
        message_text += "Connect with fellow students, share knowledge, and grow together!\n\n"
        message_text += "📊 **Community Stats:**\n"
        message_text += f"• Active Members: {len(get_active_members())}\n"
        message_text += f"• Study Groups: {len(STUDY_GROUPS)}\n"
        message_text += f"• Total Posts: {len(COMMUNITY_POSTS)}\n"
        message_text += f"• Today Active: {random.randint(50, 120)} users\n\n"

        keyboard = [
            [InlineKeyboardButton("📝 Community Posts", callback_data="community_posts")],
            [InlineKeyboardButton("👥 Study Groups", callback_data="study_groups")],
            [InlineKeyboardButton("💬 Chat Rooms", callback_data="chat_rooms")],
            [InlineKeyboardButton("🏆 Community Leaders", callback_data="community_leaders")],
            [InlineKeyboardButton("➕ Create Post", callback_data="create_post")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.edit_message_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

    except Exception as e:
        print(f"Error in community_menu: {e}")
        if hasattr(update, 'callback_query') and update.callback_query:
            await update.callback_query.answer("Error loading community menu")
        else:
            await update.message.reply_text("❌ Error loading community menu. Please try again.")

async def community_posts(update, context):
    """Display community posts"""
    try:
        message_text = "📝 **Community Posts**\n\n"
        message_text += "Latest discussions and posts from the community:\n\n"

        # Show top 5 posts
        for i, post in enumerate(COMMUNITY_POSTS[:5], 1):
            message_text += f"**{i}. {post['title']}**\n"
            message_text += f"👤 By: {post['author']} • 📂 {post['category']}\n"
            message_text += f"💬 {post['content'][:100]}{'...' if len(post['content']) > 100 else ''}\n"
            message_text += f"👍 {post['likes']} likes • 💭 {post['comments']} comments\n\n"

        keyboard = [
            [InlineKeyboardButton("👍 Like Posts", callback_data="like_posts")],
            [InlineKeyboardButton("💭 Comment", callback_data="comment_post")],
            [InlineKeyboardButton("➕ New Post", callback_data="create_post")],
            [InlineKeyboardButton("🔙 Back to Community", callback_data="community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in community_posts: {e}")
        await update.callback_query.answer("Error loading posts")

async def study_groups(update, context):
    """Display available study groups"""
    try:
        message_text = "👥 **Study Groups**\n\n"
        message_text += "Join study groups to learn together with peers:\n\n"

        for group in STUDY_GROUPS:
            message_text += f"**📚 {group['name']}**\n"
            message_text += f"📝 {group['description']}\n"
            message_text += f"👥 {group['members']} members • 📂 {group['subject']}\n\n"

        keyboard = [
            [InlineKeyboardButton("➕ Join Group", callback_data="join_group")],
            [InlineKeyboardButton("👑 Create Group", callback_data="create_group")],
            [InlineKeyboardButton("🔙 Back to Community", callback_data="community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in study_groups: {e}")
        await update.callback_query.answer("Error loading study groups")

async def chat_rooms(update, context):
    """Display chat rooms"""
    try:
        message_text = "💬 **Chat Rooms**\n\n"
        message_text += "Join real-time discussions with fellow students:\n\n"

        chat_rooms_list = [
            {"name": "General Discussion", "members": random.randint(15, 50), "topic": "General"},
            {"name": "Mathematics Help", "members": random.randint(10, 30), "topic": "Mathematics"},
            {"name": "Science Discussion", "members": random.randint(20, 45), "topic": "Science"},
            {"name": "Social Studies", "members": random.randint(12, 35), "topic": "Social Science"}
        ]

        for room in chat_rooms_list:
            message_text += f"💬 **{room['name']}**\n"
            message_text += f"👥 {room['members']} active • 📂 {room['topic']}\n\n"

        keyboard = [
            [InlineKeyboardButton("🚀 Join Chat", callback_data="join_chat")],
            [InlineKeyboardButton("🔙 Back to Community", callback_data="community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in chat_rooms: {e}")
        await update.callback_query.answer("Error loading chat rooms")

async def community_leaders(update, context):
    """Display community leaders"""
    try:
        message_text = "🏆 **Community Leaders**\n\n"
        message_text += "Top contributors and helpful members:\n\n"

        leaders = [
            {"name": "StudyMaster_Alex", "points": 2450, "badges": ["🏅 Top Helper", "📚 Study Champion"]},
            {"name": "MathGenius", "points": 2100, "badges": ["🧮 Math Expert", "💡 Problem Solver"]},
            {"name": "ScienceGuide", "points": 1950, "badges": ["🔬 Science Star", "📖 Knowledge Sharer"]},
            {"name": "CommunityHelper", "points": 1800, "badges": ["🤝 Community Hero", "⭐ Top Contributor"]}
        ]

        for i, leader in enumerate(leaders, 1):
            message_text += f"**{i}. {leader['name']}**\n"
            message_text += f"⭐ Points: {leader['points']}\n"
            message_text += f"🏆 Badges: {', '.join(leader['badges'])}\n\n"

        keyboard = [
            [InlineKeyboardButton("⭐ View My Stats", callback_data="my_stats")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
            [InlineKeyboardButton("🔙 Back to Community", callback_data="community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in community_leaders: {e}")
        await update.callback_query.answer("Error loading community leaders")

async def create_post(update, context):
    """Handle post creation"""
    try:
        message_text = "➕ **Create New Post**\n\n"
        message_text += "Share your knowledge, ask questions, or start a discussion!\n\n"
        message_text += "📝 **Post Categories:**\n"
        message_text += "• Study Tips & Tricks\n"
        message_text += "• Question Help\n"
        message_text += "• Subject Discussions\n"
        message_text += "• General Chat\n\n"
        message_text += "💡 **Tips for great posts:**\n"
        message_text += "• Be clear and descriptive\n"
        message_text += "• Use appropriate tags\n"
        message_text += "• Be respectful to others\n"
        message_text += "• Share useful resources\n\n"

        keyboard = [
            [InlineKeyboardButton("📚 Study Tips", callback_data="create_study_tip")],
            [InlineKeyboardButton("❓ Ask Question", callback_data="ask_question")],
            [InlineKeyboardButton("💭 Start Discussion", callback_data="start_discussion")],
            [InlineKeyboardButton("🔙 Cancel", callback_data="community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in create_post: {e}")
        await update.callback_query.answer("Error loading post creation")

def get_active_members():
    """Get list of active community members (mock data)"""
    sample_members = [
        "Student_Alex", "BioLover", "PhysicsFan", "ChemStudent", 
        "SocialScholar", "MathGenius", "ScienceGuide", "StudyMaster",
        "CommunityHelper", "KnowledgeSeeker", "StudyBuddy", "PeerHelper"
    ]
    return sample_members

async def like_posts(update, context):
    """Handle liking posts"""
    try:
        await update.callback_query.answer("👍 Post liked! Thank you for the feedback!")
    except Exception as e:
        print(f"Error in like_posts: {e}")

async def comment_post(update, context):
    """Handle commenting on posts"""
    try:
        message_text = "💭 **Comment on Post**\n\n"
        message_text += "Select a post to comment on:\n\n"
        
        keyboard = []
        for i, post in enumerate(COMMUNITY_POSTS[:3], 1):
            keyboard.append([InlineKeyboardButton(f"💭 Comment on: {post['title'][:30]}...", callback_data=f"comment_{post['id']}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Posts", callback_data="community_posts")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in comment_post: {e}")
        await update.callback_query.answer("Error loading comment options")

async def join_group(update, context):
    """Handle joining study groups"""
    try:
        await update.callback_query.answer("🎉 Successfully joined the study group!")
        
        message_text = "🎉 **Welcome to the Study Group!**\n\n"
        message_text += "You've been added to the group chat.\n"
        message_text += "You can now:\n"
        message_text += "• Share study materials\n"
        message_text += "• Ask questions\n"
        message_text += "• Collaborate on projects\n"
        message_text += "• Schedule study sessions\n\n"

        keyboard = [
            [InlineKeyboardButton("💬 Open Group Chat", callback_data="open_group_chat")],
            [InlineKeyboardButton("📚 Study Resources", callback_data="group_resources")],
            [InlineKeyboardButton("🔙 Back to Groups", callback_data="study_groups")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in join_group: {e}")
        await update.callback_query.answer("Error joining group")

async def join_chat(update, context):
    """Handle joining chat rooms"""
    try:
        await update.callback_query.answer("🚀 Joining chat room...")
        
        message_text = "🚀 **Welcome to the Chat Room!**\n\n"
        message_text += "You're now connected to the community chat.\n"
        message_text += "Features available:\n"
        message_text += "• Real-time messaging\n"
        message_text += "• Voice messages\n"
        message_text += "• File sharing\n"
        message_text += "• Study group coordination\n\n"

        keyboard = [
            [InlineKeyboardButton("💬 Send Message", callback_data="send_message")],
            [InlineKeyboardButton("🎤 Voice Message", callback_data="voice_message")],
            [InlineKeyboardButton("📎 Share File", callback_data="share_file")],
            [InlineKeyboardButton("🔙 Exit Chat", callback_data="community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in join_chat: {e}")
        await update.callback_query.answer("Error joining chat")

async def my_stats(update, context):
    """Display user's community stats"""
    try:
        # Mock user stats - in real implementation, get from database
        user_stats = {
            "posts_created": random.randint(1, 15),
            "comments_made": random.randint(5, 50),
            "likes_received": random.randint(10, 100),
            "groups_joined": random.randint(1, 5),
            "help_score": random.randint(50, 500)
        }

        message_text = "⭐ **Your Community Stats**\n\n"
        message_text += f"📝 **Posts Created:** {user_stats['posts_created']}\n"
        message_text += f"💭 **Comments Made:** {user_stats['comments_made']}\n"
        message_text += f"👍 **Likes Received:** {user_stats['likes_received']}\n"
        message_text += f"👥 **Groups Joined:** {user_stats['groups_joined']}\n"
        message_text += f"🤝 **Help Score:** {user_stats['help_score']}\n\n"
        message_text += "🏆 **Achievements:**\n"
        message_text += "• 📚 Knowledge Contributor\n"
        message_text += "• 🤝 Community Helper\n"
        message_text += "• 💬 Active Member\n\n"

        keyboard = [
            [InlineKeyboardButton("📈 View Progress", callback_data="view_progress")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
            [InlineKeyboardButton("🔙 Back to Community", callback_data="community")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        print(f"Error in my_stats: {e}")
        await update.callback_query.answer("Error loading your stats")
