"""
Materials handler for the Smart Test Exam
"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.keyboards.main_menu import main_menu

async def materials_menu(update, context):
    """Display materials menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Materials menu text
    materials_text = """
📚 Learning Materials

Here you will find useful materials for exam preparation:

📖 Theoretical materials
📝 Example problems and solutions  
📊 Reference tables
💡 Study tips

Choose the category that interests you:
    """
    
    # Create inline keyboard for materials
    keyboard = [
        [InlineKeyboardButton("📖 Theory", callback_data="materials_theory")],
        [InlineKeyboardButton("📝 Examples", callback_data="materials_examples")],
        [InlineKeyboardButton("📊 References", callback_data="materials_reference")],
        [InlineKeyboardButton("💡 Tips", callback_data="materials_tips")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        materials_text,
        reply_markup=reply_markup
    )

async def materials_theory(update, context):
    """Display theoretical materials"""
    query = update.callback_query
    await query.answer()
    
    theory_text = """
📖 Theoretical Materials

Main topics to study:

🔬 Natural Sciences:
• Physics - mechanics basics, thermodynamics
• Chemistry - periodic table, reactions
• Biology - cellular structure, genetics

📐 Mathematics:
• Algebra - equations, inequalities
• Geometry - plane and spatial figures
• Calculus - derivatives, integrals

🌍 Humanities:
• History - main periods and events
• Literature - classic works
• Geography - continents, climate, population

Choose a subject for detailed study:
    """
    
    keyboard = [
        [InlineKeyboardButton("🔬 Physics", callback_data="theory_physics")],
        [InlineKeyboardButton("⚗️ Chemistry", callback_data="theory_chemistry")],
        [InlineKeyboardButton("🧬 Biology", callback_data="theory_biology")],
        [InlineKeyboardButton("📐 Mathematics", callback_data="theory_math")],
        [InlineKeyboardButton("📜 History", callback_data="theory_history")],
        [InlineKeyboardButton("📚 Literature", callback_data="theory_literature")],
        [InlineKeyboardButton("🌍 Geography", callback_data="theory_geography")],
        [InlineKeyboardButton("⬅️ Back", callback_data="materials")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        theory_text,
        reply_markup=reply_markup
    )

async def materials_examples(update, context):
    """Display example problems"""
    query = update.callback_query
    await query.answer()
    
    examples_text = """
📝 Example Problems and Solutions

Practical examples with detailed solutions:

🧮 Mathematics:
• Algebraic equations
• Geometry problems
• Motion problems

🔬 Natural Sciences:
• Physics problems in mechanics
• Chemical equations
• Biological processes

📚 Humanities:
• Historical events
• Literary analysis
• Geography problems

Choose a category to view examples:
    """
    
    keyboard = [
        [InlineKeyboardButton("🧮 Mathematics", callback_data="examples_math")],
        [InlineKeyboardButton("🔬 Physics", callback_data="examples_physics")],
        [InlineKeyboardButton("⚗️ Chemistry", callback_data="examples_chemistry")],
        [InlineKeyboardButton("🧬 Biology", callback_data="examples_biology")],
        [InlineKeyboardButton("📜 History", callback_data="examples_history")],
        [InlineKeyboardButton("📚 Literature", callback_data="examples_literature")],
        [InlineKeyboardButton("⬅️ Back", callback_data="materials")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        examples_text,
        reply_markup=reply_markup
    )

async def materials_reference(update, context):
    """Display reference materials"""
    query = update.callback_query
    await query.answer()
    
    reference_text = """
📊 Reference Materials

Quick access to important information:

📐 Formulas and Constants:
• Mathematical formulas
• Physical constants
• Chemical elements

🗓️ Chronology:
• Important historical dates
• Science development periods
• Literary epochs

🌍 Geographic Data:
• Country capitals
• Area and population
• Climate zones

📚 Term Dictionaries:
• Scientific terminology
• Historical concepts
• Literary terms
    """
    
    keyboard = [
        [InlineKeyboardButton("📐 Formulas", callback_data="reference_formulas")],
        [InlineKeyboardButton("🗓️ Chronology", callback_data="reference_chronology")],
        [InlineKeyboardButton("🌍 Geography", callback_data="reference_geography")],
        [InlineKeyboardButton("📚 Terms", callback_data="reference_terms")],
        [InlineKeyboardButton("⬅️ Back", callback_data="materials")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        reference_text,
        reply_markup=reply_markup
    )

async def materials_tips(update, context):
    """Display study tips"""
    query = update.callback_query
    await query.answer()
    
    tips_text = """
💡 Study Tips

Useful recommendations for effective learning:

🎯 Planning:
• Create a study schedule
• Break down material into parts
• Take regular breaks

📖 Studying Material:
• Use various sources
• Take notes
• Create diagrams and tables

🧠 Memorization:
• Apply mnemonic techniques
• Review material at intervals
• Connect new information to known concepts

📝 Exam Preparation:
• Solve test questions
• Study exam format
• Practice with time limits

💪 Motivation:
• Set specific goals
• Track your achievements
• Don't be afraid to ask for help
    """
    
    keyboard = [
        [InlineKeyboardButton("🎯 Planning", callback_data="tips_planning")],
        [InlineKeyboardButton("📖 Studying", callback_data="tips_studying")],
        [InlineKeyboardButton("🧠 Memorization", callback_data="tips_memory")],
        [InlineKeyboardButton("📝 Exams", callback_data="tips_exams")],
        [InlineKeyboardButton("💪 Motivation", callback_data="tips_motivation")],
        [InlineKeyboardButton("⬅️ Back", callback_data="materials")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        tips_text,
        reply_markup=reply_markup
    )

# Handle specific material categories
async def handle_material_category(update, context):
    """Handle generic material category selection"""
    query = update.callback_query
    await query.answer()
    
    category = query.data.replace("theory_", "").replace("examples_", "").replace("reference_", "").replace("tips_", "")
    
    # Provide category-specific content based on the selection
    if "theory" in query.data:
        content = f"📖 Detailed information about: {category.title()}"
    elif "examples" in query.data:
        content = f"📝 Example problems for: {category.title()}"
    elif "reference" in query.data:
        content = f"📊 Reference materials for: {category.title()}"
    elif "tips" in query.data:
        content = f"💡 Tips for: {category.title()}"
    else:
        content = "📚 Materials for the selected topic"
    
    # Create back button based on the original category
    if "theory" in query.data:
        back_data = "materials_theory"
    elif "examples" in query.data:
        back_data = "materials_examples"
    elif "reference" in query.data:
        back_data = "materials_reference"
    elif "tips" in query.data:
        back_data = "materials_tips"
    else:
        back_data = "materials"
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Back", callback_data=back_data)]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{content}\n\n⚠️ This feature is under development.\nFull content will be available soon!",
        reply_markup=reply_markup
    )

async def course_materials(update, context):
    """Display course-specific materials"""
    query = update.callback_query
    await query.answer()
    
    # Extract course name from callback data
    course_data = query.data.replace("materials_course_", "")
    
    course_text = f"""
📚 Course Materials: {course_data.replace('_', ' ').title()}

Available materials for study:

📖 Theoretical materials
📝 Practical exercises
📊 Reference materials
💡 Methodological recommendations

Choose the type of materials:
    """
    
    keyboard = [
        [InlineKeyboardButton("📖 Theory", callback_data=f"course_theory_{course_data}")],
        [InlineKeyboardButton("📝 Practice", callback_data=f"course_practice_{course_data}")],
        [InlineKeyboardButton("📊 Reference", callback_data=f"course_reference_{course_data}")],
        [InlineKeyboardButton("💡 Methodology", callback_data=f"course_methods_{course_data}")],
        [InlineKeyboardButton("⬅️ Back", callback_data="materials")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        course_text,
        reply_markup=reply_markup
    )

async def request_material(update, context):
    """Handle material request functionality"""
    query = update.callback_query
    await query.answer()
    
    request_text = """
📋 Material Request

If you need specific materials that are not available in the menu, 
you can request them from the administrator.

📧 Please describe what materials you need:
• Subject/course
• Topic or section
• Type of materials (theory, practice, references)

Your request will be processed within 24 hours.
    """
    
    keyboard = [
        [InlineKeyboardButton("📧 Request Material", callback_data="send_material_request")],
        [InlineKeyboardButton("📞 Contact Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("⬅️ Back", callback_data="materials")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        request_text,
        reply_markup=reply_markup
    )
