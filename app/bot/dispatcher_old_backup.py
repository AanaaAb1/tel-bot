
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
from app.handlers.admin_handler import (
    admin_payments, approve, reject, exam_analytics,
    admin_panel, admin_users, admin_questions_menu,
    admin_results, admin_export_menu, admin_export_csv, admin_export_excel,
    admin_add_question_start, admin_edit_question_start, admin_delete_question_start,
    admin_back_main, handle_admin_text_input, edit_question, delete_question, admin_confirm_delete,
    admin_view_payment_details, admin_approve_payment, admin_reject_payment,
    # Exam creation handlers
    admin_add_exam_start, admin_select_course_for_exam, admin_save_exam
)
from app.handlers.profile_handler_fixed import (
    profile_menu, copy_referral_code, copy_invitation_link, view_referral_history
)
from app.handlers.course_handler import select_course, start_exam_selected
from app.handlers.question_handler import answer_question, show_detailed_result
from app.handlers.radio_question_handler import handle_poll_answer
from app.handlers.practice_handler import (
    start_practice,
    practice_by_course,
    practice_course_selected,
    practice_by_chapter,
    practice_course_for_chapter,
    practice_chapter_selected
)

def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("payments", admin_payments))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("reject", reject))
    app.add_handler(CommandHandler("analytics", exam_analytics))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("edit_question", edit_question))
    app.add_handler(CommandHandler("delete_question", delete_question))

    app.add_handler(CallbackQueryHandler(handle_registration_callback, pattern="^(level_|stream_)"))
    app.add_handler(CallbackQueryHandler(onboarding, pattern="^(level_|stream_)"))
    app.add_handler(CallbackQueryHandler(answer_question, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(submit_payment, pattern="submit_payment"))
    # Admin panel handlers (must be before general menu handler)
    # More specific handlers first, then general ones
    app.add_handler(CallbackQueryHandler(admin_users, pattern="^admin_users$"))
    app.add_handler(CallbackQueryHandler(admin_view_payment_details, pattern="^view_payment_"))
    app.add_handler(CallbackQueryHandler(admin_approve_payment, pattern="^approve_payment_"))
    app.add_handler(CallbackQueryHandler(admin_reject_payment, pattern="^reject_payment_"))
    app.add_handler(CallbackQueryHandler(admin_payments, pattern="^admin_payments$"))
    # Exam creation handlers
    app.add_handler(CallbackQueryHandler(admin_add_exam_start, pattern="^admin_add_exam$"))
    app.add_handler(CallbackQueryHandler(admin_select_course_for_exam, pattern="^select_course_for_exam_"))
    app.add_handler(CallbackQueryHandler(admin_questions_menu, pattern="^admin_questions$"))
    app.add_handler(CallbackQueryHandler(admin_results, pattern="^admin_results$"))
    app.add_handler(CallbackQueryHandler(admin_export_menu, pattern="^admin_export$"))
    app.add_handler(CallbackQueryHandler(admin_export_csv, pattern="^admin_export_csv$"))
    app.add_handler(CallbackQueryHandler(admin_export_excel, pattern="^admin_export_excel$"))
    app.add_handler(CallbackQueryHandler(admin_add_question_start, pattern="^admin_add_question$"))
    app.add_handler(CallbackQueryHandler(admin_edit_question_start, pattern="^admin_edit_question$"))
    app.add_handler(CallbackQueryHandler(admin_delete_question_start, pattern="^admin_delete_question$"))
    app.add_handler(CallbackQueryHandler(admin_back_main, pattern="^admin_back_main$"))
    app.add_handler(CallbackQueryHandler(admin_confirm_delete, pattern="^admin_confirm_delete_"))

    # Profile handlers - Specific patterns first
    app.add_handler(CallbackQueryHandler(profile_menu, pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(copy_referral_code, pattern="^copy_code_"))
    app.add_handler(CallbackQueryHandler(copy_invitation_link, pattern="^copy_link_"))
    app.add_handler(CallbackQueryHandler(view_referral_history, pattern="^referral_history_"))

    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    # Menu handler with specific patterns first, then general fallback
    app.add_handler(CallbackQueryHandler(menu, pattern="^(exams|payment|materials|admin|help|analytics|back_to_main|courses|practice|leaderboard|leaderboard_best|leaderboard_latest|leaderboard_average)$"))
    app.add_handler(CallbackQueryHandler(menu))

    # Admin exam creation text handler (must be before the general admin text handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, admin_save_exam))
    # Admin text input handler (must be before the general text handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_admin_text_input))

    # Result command handler
    app.add_handler(MessageHandler(filters.Regex(r'^/result_\d+$'), show_detailed_result))

    # Poll answer handler for radio-style questions
    app.add_handler(PollAnswerHandler(handle_poll_answer))

    # Payment proof handler (text, photos, documents)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
        receive_payment_proof
    ))
