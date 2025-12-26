from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    PollAnswerHandler
)

from app.handlers.start_handler import start
from app.handlers.register_handler import register, handle_registration_callback
from app.handlers.onboarding_handler import onboarding
from app.handlers.menu_handler import menu
from app.handlers.profile_handler_fixed import register_profile_handlers
from app.handlers.community_handler import community_menu, community_posts, study_groups, chat_rooms, community_leaders, create_post, like_posts, comment_post, join_group, join_chat, my_stats
from app.handlers.materials_handler import materials_menu, course_materials, request_material
from app.handlers.help_handler import help_handler, help_callback
from app.handlers.payment_handler_fixed import (
    payment_menu,
    submit_payment,
    receive_payment_proof
)
from app.handlers.admin_handler_fixed import (
    admin_payments, approve, reject, exam_analytics,
    admin_panel, admin_users, 
    admin_results, admin_export_menu, admin_export_csv, admin_export_excel,
    admin_back_main, handle_admin_text_input, edit_question, delete_question, admin_confirm_delete,
    admin_view_payment_details, admin_approve_payment, admin_reject_payment
)
# Only use the fixed version - no conflicts
from app.handlers.admin_question_handler_fixed import (
    admin_questions_menu_enhanced,
    admin_select_course_for_question,
    admin_select_chapter_for_question,
    admin_handle_question_step,
    admin_handle_question_text_input,
    admin_back_to_questions_menu
)
from app.handlers.course_handler import select_course, select_difficulty, start_exam_selected
from app.handlers.question_handler import answer_question, show_detailed_result
from app.handlers.stream_dashboard_handler import (
    natural_science_dashboard, 
    social_science_dashboard,
    handle_natural_science_action,
    handle_social_science_action,
    natural_science_exams,
    social_science_exams
)
from app.handlers.stream_course_handler import (
    select_natural_science_course,
    select_social_science_course,
    handle_stream_course_selection,
    get_stream_course_handler
)
from app.handlers.practice_handler import (
    start_practice,
    practice_by_course,
    practice_course_selected,
    practice_by_chapter,
    practice_course_for_chapter,
    practice_chapter_selected
)
from app.handlers.radio_question_handler_poll import handle_poll_answer

def register_handlers(app):
    # Poll answer handler for radio-style questions - register first
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    
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

    # Callback query handlers - order matters: specific patterns first, general last
    app.add_handler(CallbackQueryHandler(handle_registration_callback, pattern="^(level_|stream_)"))
    app.add_handler(CallbackQueryHandler(onboarding, pattern="^(level_|stream_)"))
    app.add_handler(CallbackQueryHandler(answer_question, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(submit_payment, pattern="submit_payment"))
    
    # Admin panel handlers (must be before general menu handler)
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="^admin$"))
    app.add_handler(CallbackQueryHandler(admin_users, pattern="^admin_users$"))
    app.add_handler(CallbackQueryHandler(admin_view_payment_details, pattern="^view_payment_"))
    app.add_handler(CallbackQueryHandler(admin_approve_payment, pattern="^approve_payment_"))
    app.add_handler(CallbackQueryHandler(admin_reject_payment, pattern="^reject_payment_"))
    app.add_handler(CallbackQueryHandler(admin_payments, pattern="^admin_payments$"))
    app.add_handler(CallbackQueryHandler(admin_questions_menu_enhanced, pattern="^admin_questions$"))
    app.add_handler(CallbackQueryHandler(admin_results, pattern="^admin_results$"))
    app.add_handler(CallbackQueryHandler(admin_export_menu, pattern="^admin_export$"))
    app.add_handler(CallbackQueryHandler(admin_export_csv, pattern="^admin_export_csv$"))
    app.add_handler(CallbackQueryHandler(admin_export_excel, pattern="^admin_export_excel$"))
    app.add_handler(CallbackQueryHandler(admin_back_main, pattern="^admin_back_main$"))
    app.add_handler(CallbackQueryHandler(admin_confirm_delete, pattern="^admin_confirm_delete_"))
    app.add_handler(CallbackQueryHandler(admin_select_course_for_question, pattern="^admin_select_course"))
    app.add_handler(CallbackQueryHandler(admin_select_course_for_question, pattern="^admin_select_course_"))
    app.add_handler(CallbackQueryHandler(admin_select_course_for_question, pattern="^admin_select_course_back$"))
    app.add_handler(CallbackQueryHandler(admin_select_chapter_for_question, pattern="^admin_select_chapter_"))
    app.add_handler(CallbackQueryHandler(admin_handle_question_step, pattern="^admin_question_"))
    
    # Admin question text input handler (must be before general text handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, admin_handle_question_text_input))

    # Practice handlers - FIXED: Unique patterns to avoid conflicts
    app.add_handler(CallbackQueryHandler(start_practice, pattern="^practice$"))
    app.add_handler(CallbackQueryHandler(practice_by_course, pattern="^practice_course$"))
    app.add_handler(CallbackQueryHandler(practice_course_selected, pattern=r"^practice_course_(\d+)$"))  # Start practice for course
    app.add_handler(CallbackQueryHandler(practice_by_chapter, pattern="^practice_chapter$"))
    app.add_handler(CallbackQueryHandler(practice_course_for_chapter, pattern=r"^practice_course_chapter_(\d+)$"))  # Show chapters for practice
    app.add_handler(CallbackQueryHandler(practice_chapter_selected, pattern=r"^practice_chapter_(\d+)$"))

    # Stream course selection handler (must be before general course handler)
    app.add_handler(get_stream_course_handler())
    
    # Stream dashboard handlers (specific patterns first)
    app.add_handler(CallbackQueryHandler(natural_science_dashboard, pattern="^natural_science_dashboard$"))
    app.add_handler(CallbackQueryHandler(social_science_dashboard, pattern="^social_science_dashboard$"))
    app.add_handler(CallbackQueryHandler(handle_natural_science_action, pattern="^ns_"))
    app.add_handler(CallbackQueryHandler(handle_social_science_action, pattern="^ss_"))
    app.add_handler(CallbackQueryHandler(natural_science_exams, pattern="^ns_exams$"))
    app.add_handler(CallbackQueryHandler(social_science_exams, pattern="^ss_exams$"))
    app.add_handler(CallbackQueryHandler(select_natural_science_course, pattern="^select_ns_course$"))
    app.add_handler(CallbackQueryHandler(select_social_science_course, pattern="^select_ss_course$"))
    
    # Course selection handlers - NEW FLOW: Course → Difficulty → Chapters → Questions
    app.add_handler(CallbackQueryHandler(select_course, pattern="^exam_course_"))
    app.add_handler(CallbackQueryHandler(select_difficulty, pattern="^difficulty_"))
    app.add_handler(CallbackQueryHandler(start_exam_selected, pattern="^start_exam_"))

    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(materials_menu, pattern="^materials$"))
    app.add_handler(CallbackQueryHandler(course_materials, pattern="^materials_course_"))

    # Profile handlers - Use the new ProfileHandler class
    register_profile_handlers(app)
    app.add_handler(CallbackQueryHandler(community_menu, pattern="^community$"))
    app.add_handler(CallbackQueryHandler(community_posts, pattern="^community_posts$"))
    app.add_handler(CallbackQueryHandler(study_groups, pattern="^study_groups$"))
    app.add_handler(CallbackQueryHandler(chat_rooms, pattern="^chat_rooms$"))
    app.add_handler(CallbackQueryHandler(community_leaders, pattern="^community_leaders$"))
    app.add_handler(CallbackQueryHandler(create_post, pattern="^create_post$"))
    app.add_handler(CallbackQueryHandler(like_posts, pattern="^like_posts$"))
    app.add_handler(CallbackQueryHandler(comment_post, pattern="^comment_post$"))
    app.add_handler(CallbackQueryHandler(join_group, pattern="^join_group$"))
    app.add_handler(CallbackQueryHandler(join_chat, pattern="^join_chat$"))
    app.add_handler(CallbackQueryHandler(my_stats, pattern="^my_stats$"))

    # Menu handler with specific patterns only - removed general fallback to avoid conflicts
    app.add_handler(CallbackQueryHandler(menu, pattern="^(exams|payment|materials|admin|help|analytics|back_to_main|courses|practice|community)$"))

    # Admin text input handler (must be before the general text handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_admin_text_input))

    # Result command handler
    app.add_handler(MessageHandler(filters.Regex(r'^/result_\d+$'), show_detailed_result))
    
    # Payment proof handler (text, photos, documents)
    app.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
        receive_payment_proof
    ))
