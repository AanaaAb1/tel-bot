from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    PollAnswerHandler,
    filters
)

from app.handlers.start_handler import start
from app.handlers.register_handler import register, handle_registration_callback
from app.handlers.onboarding_handler import onboarding
from app.handlers.menu_handler import menu
from app.handlers.materials_handler import materials_menu, course_materials, request_material
from app.handlers.help_handler import help_handler, help_callback
from app.handlers.payment_handler import (
    submit_payment,
    receive_payment_proof
)
from app.handlers.profile_handler_fixed import (
    profile_menu, copy_referral_code, copy_invitation_link, view_referral_history
)
from app.handlers.exam_handler_fixed import start_exam
from app.handlers.course_handler_fixed import select_course, start_exam_selected
from app.handlers.practice_handler_fixed import (
    start_practice,
    practice_by_course,
    practice_course_selected,
    practice_by_chapter,
    practice_course_for_chapter,
    practice_chapter_selected
)
from app.handlers.question_handler import answer_question, show_detailed_result
from app.handlers.radio_question_handler import handle_poll_answer

def register_handlers(app):
    # Basic commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("help", help_handler))

    # Registration callbacks
    app.add_handler(CallbackQueryHandler(handle_registration_callback, pattern="^(level_|stream_)"))
    app.add_handler(CallbackQueryHandler(onboarding, pattern="^(level_|stream_)"))
    
    # Question answering
    app.add_handler(CallbackQueryHandler(answer_question, pattern="^ans_"))
    
    # Payment handling
    app.add_handler(CallbackQueryHandler(submit_payment, pattern="submit_payment"))
    
    # Profile handlers - Specific patterns first
    app.add_handler(CallbackQueryHandler(profile_menu, pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(copy_referral_code, pattern="^copy_code_"))
    app.add_handler(CallbackQueryHandler(copy_invitation_link, pattern="^copy_link_"))
    app.add_handler(CallbackQueryHandler(view_referral_history, pattern="^referral_history_"))

    # Practice handlers with access control
    app.add_handler(CallbackQueryHandler(start_practice, pattern="^practice$"))
    app.add_handler(CallbackQueryHandler(practice_by_course, pattern="^practice_course$"))
    app.add_handler(CallbackQueryHandler(practice_course_selected, pattern="^practice_course_"))
    app.add_handler(CallbackQueryHandler(practice_by_chapter, pattern="^practice_chapter$"))
    app.add_handler(CallbackQueryHandler(practice_course_for_chapter, pattern="^practice_course_"))
    app.add_handler(CallbackQueryHandler(practice_chapter_selected, pattern="^practice_chapter_"))

    # Exam handlers with access control
    app.add_handler(CallbackQueryHandler(start_exam, pattern="^exams$"))
    app.add_handler(CallbackQueryHandler(select_course, pattern="^exam_course_"))
    app.add_handler(CallbackQueryHandler(start_exam_selected, pattern="^start_exam_"))

    # Materials handlers
    app.add_handler(CallbackQueryHandler(materials_menu, pattern="^materials$"))
    app.add_handler(CallbackQueryHandler(course_materials, pattern="^course_materials_"))
    app.add_handler(CallbackQueryHandler(request_material, pattern="^request_material_"))

    # Help handler
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    
    # Menu handler (main fallback)
    app.add_handler(CallbackQueryHandler(menu, pattern="^(exams|payment|materials|help|back_to_main|courses|practice|leaderboard|leaderboard_best|leaderboard_latest|leaderboard_average|profile)$"))
    app.add_handler(CallbackQueryHandler(menu))

    # Result command handler
    app.add_handler(MessageHandler(filters.Regex(r'^/result_\d+$'), show_detailed_result))

    # Poll answer handler for radio-style questions
    app.add_handler(PollAnswerHandler(handle_poll_answer))

    # Payment proof handler (text, photos, documents)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
        receive_payment_proof
    ))
