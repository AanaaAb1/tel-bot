from app.database.session import SessionLocal
from app.models.user import User
from app.models.result import Result
from app.keyboards.main_menu import main_menu
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import statistics

async def show_leaderboard(update, context):
    """Display the leaderboard with user rankings"""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    
    # Get all users with their results
    users = db.query(User).all()
    leaderboard_data = []

    for user in users:
        # Get all results for this user
        results = db.query(Result).filter_by(user_id=user.id).all()
        
        if results:
            # Calculate different score metrics
            scores = [result.score for result in results if result.score is not None]
            if scores:
                best_score = max(scores)
                latest_score = scores[-1] if scores else 0
                average_score = statistics.mean(scores) if scores else 0
                
                # Use best score as default ranking metric
                user_score = best_score
                user_name = user.full_name or f"User_{user.telegram_id}"
                
                leaderboard_data.append({
                    'user_id': user.telegram_id,
                    'user_name': user_name,
                    'score': user_score,
                    'best_score': best_score,
                    'latest_score': latest_score,
                    'average_score': round(average_score, 1),
                    'total_exams': len(results)
                })

    # Sort by score (descending)
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)

    # Assign ranks
    for rank, user_data in enumerate(leaderboard_data, 1):
        user_data['rank'] = rank

    db.close()

    # Format leaderboard message
    if not leaderboard_data:
        message_text = "🏆 **Leaderboard**\n\nNo exam results found yet.\n\nComplete some exams to see your ranking!"
    else:
        message_text = "🏆 **LEADERBOARD** 🏆\n\n"
        message_text += "📊 **Top Performers:**\n\n"
        
        # Show top 10 users
        for user_data in leaderboard_data[:10]:
            rank_emoji = "🥇" if user_data['rank'] == 1 else "🥈" if user_data['rank'] == 2 else "🥉" if user_data['rank'] == 3 else f"{user_data['rank']}."
            message_text += f"{rank_emoji} **{user_data['user_name']}**\n"
            message_text += f"   Score: {user_data['score']} points\n"
            message_text += f"   Best: {user_data['best_score']} | Latest: {user_data['latest_score']} | Avg: {user_data['average_score']}\n"
            message_text += f"   Exams taken: {user_data['total_exams']}\n\n"
        
        if len(leaderboard_data) > 10:
            message_text += f"... and {len(leaderboard_data) - 10} more participants\n\n"
        
        message_text += "📈 **Scoring Method:** Best score across all exams\n"
        message_text += "🎯 Take more exams to improve your ranking!"

    # Create keyboard with options
    keyboard_buttons = [
        [InlineKeyboardButton("📊 Best Scores", callback_data="leaderboard_best")],
        [InlineKeyboardButton("🕒 Latest Scores", callback_data="leaderboard_latest")],
        [InlineKeyboardButton("📈 Average Scores", callback_data="leaderboard_average")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ]
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    await query.edit_message_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def show_leaderboard_best(update, context):
    """Show leaderboard sorted by best scores"""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    
    users = db.query(User).all()
    leaderboard_data = []

    for user in users:
        results = db.query(Result).filter_by(user_id=user.id).all()
        
        if results:
            scores = [result.score for result in results if result.score is not None]
            if scores:
                best_score = max(scores)
                user_name = user.full_name or f"User_{user.telegram_id}"
                
                leaderboard_data.append({
                    'user_id': user.telegram_id,
                    'user_name': user_name,
                    'score': best_score,
                    'total_exams': len(results)
                })

    # Sort by best score
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)

    # Assign ranks
    for rank, user_data in enumerate(leaderboard_data, 1):
        user_data['rank'] = rank

    db.close()

    # Format message
    message_text = "🏆 **LEADERBOARD - BEST SCORES** 🏆\n\n"
    message_text += "🥇 Ranking by highest single exam score\n\n"

    if not leaderboard_data:
        message_text += "No exam results found yet."
    else:
        for user_data in leaderboard_data[:10]:
            rank_emoji = "🥇" if user_data['rank'] == 1 else "🥈" if user_data['rank'] == 2 else "🥉" if user_data['rank'] == 3 else f"{user_data['rank']}."
            message_text += f"{rank_emoji} **{user_data['user_name']}**\n"
            message_text += f"   Best Score: {user_data['score']} points\n"
            message_text += f"   Exams taken: {user_data['total_exams']}\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏆 Main Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])

    await query.edit_message_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def show_leaderboard_latest(update, context):
    """Show leaderboard sorted by latest scores"""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    
    users = db.query(User).all()
    leaderboard_data = []

    for user in users:
        results = db.query(Result).filter_by(user_id=user.id).order_by(Result.created_at.desc()).all()
        
        if results:
            latest_score = results[0].score  # Most recent result
            user_name = user.full_name or f"User_{user.telegram_id}"
            
            leaderboard_data.append({
                'user_id': user.telegram_id,
                'user_name': user_name,
                'score': latest_score,
                'total_exams': len(results)
            })

    # Sort by latest score
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)

    # Assign ranks
    for rank, user_data in enumerate(leaderboard_data, 1):
        user_data['rank'] = rank

    db.close()

    # Format message
    message_text = "🕒 **LEADERBOARD - LATEST SCORES** 🕒\n\n"
    message_text += "🥇 Ranking by most recent exam score\n\n"

    if not leaderboard_data:
        message_text += "No exam results found yet."
    else:
        for user_data in leaderboard_data[:10]:
            rank_emoji = "🥇" if user_data['rank'] == 1 else "🥈" if user_data['rank'] == 2 else "🥉" if user_data['rank'] == 3 else f"{user_data['rank']}."
            message_text += f"{rank_emoji} **{user_data['user_name']}**\n"
            message_text += f"   Latest Score: {user_data['score']} points\n"
            message_text += f"   Total exams: {user_data['total_exams']}\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏆 Main Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])

    await query.edit_message_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def show_leaderboard_average(update, context):
    """Show leaderboard sorted by average scores"""
    query = update.callback_query
    await query.answer()

    db = SessionLocal()
    
    users = db.query(User).all()
    leaderboard_data = []

    for user in users:
        results = db.query(Result).filter_by(user_id=user.id).all()
        
        if results:
            scores = [result.score for result in results if result.score is not None]
            if scores:
                average_score = statistics.mean(scores)
                user_name = user.full_name or f"User_{user.telegram_id}"
                
                leaderboard_data.append({
                    'user_id': user.telegram_id,
                    'user_name': user_name,
                    'score': round(average_score, 1),
                    'total_exams': len(results)
                })

    # Sort by average score
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)

    # Assign ranks
    for rank, user_data in enumerate(leaderboard_data, 1):
        user_data['rank'] = rank

    db.close()

    # Format message
    message_text = "📈 **LEADERBOARD - AVERAGE SCORES** 📈\n\n"
    message_text += "🥇 Ranking by average performance\n\n"

    if not leaderboard_data:
        message_text += "No exam results found yet."
    else:
        for user_data in leaderboard_data[:10]:
            rank_emoji = "🥇" if user_data['rank'] == 1 else "🥈" if user_data['rank'] == 2 else "🥉" if user_data['rank'] == 3 else f"{user_data['rank']}."
            message_text += f"{rank_emoji} **{user_data['user_name']}**\n"
            message_text += f"   Average Score: {user_data['score']} points\n"
            message_text += f"   Exams taken: {user_data['total_exams']}\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🏆 Main Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
    ])

    await query.edit_message_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
