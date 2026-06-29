import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from app import app, db, BotUser, BotSettings, Article

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    user = update.effective_user
    tid = str(user.id)
    with app.app_context():
        u = BotUser.query.filter_by(telegram_id=tid).first()
        if not u:
            u = BotUser(
                telegram_id=tid,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            db.session.add(u)
            db.session.commit()
    kb = [[InlineKeyboardButton("📚 Lessons", callback_data="show_articles")]]
    await update.message.reply_text(
        f"Welcome, {user.first_name}!",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def btn_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    bot = context.bot

    if data == "show_articles":
        await show_articles(query.message.chat_id, bot)
    elif data.startswith("article_"):
        article_id = int(data.split("_")[1])
        await show_article_children(query.message.chat_id, article_id, bot)
    elif data.startswith("back_to_"):
        parent_id = int(data.split("_")[2])
        chat_id = query.message.chat_id
        # Delete media message if exists, then show articles/children
        try:
            await query.message.delete()
        except:
            pass
        
        if parent_id == 0:
            await show_articles(chat_id, bot)
        else:
            await show_article_children(chat_id, parent_id, bot)

async def show_articles(chat_id, bot):
    with app.app_context():
        articles = Article.query.filter_by(parent_id=None, is_active=True).order_by(Article.order).all()
        if not articles:
            await bot.send_message(chat_id=chat_id, text="No articles yet.")
            return
        kb = []
        for a in articles:
            children_count = Article.query.filter_by(parent_id=a.id, is_active=True).count()
            label = f"{a.title} ({children_count})" if children_count else a.title
            kb.append([InlineKeyboardButton(label, callback_data=f"article_{a.id}")])
        await bot.send_message(chat_id=chat_id, text="Select a section:", reply_markup=InlineKeyboardMarkup(kb))

async def show_article_children(chat_id, article_id, bot):
    with app.app_context():
        article = Article.query.get(article_id)
        if not article:
            await bot.send_message(chat_id=chat_id, text="Article not found.")
            return

        children = Article.query.filter_by(parent_id=article_id, is_active=True).order_by(Article.order).all()

        if children:
            text = article.content[:1000] if article.content else ""
            if len(article.content) > 1000:
                text += "\n\n...(truncated)"
            if not text:
                text = "Select a subsection:"
            kb = []
            for c in children:
                sub_count = Article.query.filter_by(parent_id=c.id, is_active=True).count()
                label = f"{c.title} ({sub_count})" if sub_count else c.title
                kb.append([InlineKeyboardButton(label, callback_data=f"article_{c.id}")])
            kb.append([InlineKeyboardButton("◀️ Back", callback_data=f"back_to_{article.parent_id or 0}")])
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode='HTML',
                link_preview_options=LinkPreviewOptions(is_disabled=article.disable_link_preview)
            )
        else:
            text = article.content[:1000] if article.content else ""
            if len(article.content) > 1000:
                text += "\n\n...(truncated)"
            kb = [[InlineKeyboardButton("◀️ Back", callback_data=f"back_to_{article.parent_id or 0}")]]

            if article.media_path:
                media_full_path = os.path.join('static', article.media_path)
                if os.path.exists(media_full_path):
                    if article.media_type == 'photo':
                        await bot.send_photo(
                            chat_id=chat_id,
                            photo=open(media_full_path, 'rb'),
                            caption=text if text else None,
                            parse_mode='HTML',
                            reply_markup=InlineKeyboardMarkup(kb)
                        )
                    else:
                        await bot.send_video(
                            chat_id=chat_id,
                            video=open(media_full_path, 'rb'),
                            caption=text if text else None,
                            parse_mode='HTML',
                            reply_markup=InlineKeyboardMarkup(kb)
                        )
                    return
                
            await bot.send_message(
                chat_id=chat_id,
                text=text if text else "No content",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode='HTML',
                link_preview_options=LinkPreviewOptions(is_disabled=article.disable_link_preview)
            )

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set in environment")
        return

    with app.app_context():
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', lambda u, c: u.message.reply_text('/start - start\n/help - help\n/lessons - lessons')))
        application.add_handler(CommandHandler('lessons', start))
        application.add_handler(CallbackQueryHandler(btn_handler))
        logger.info('Starting bot...')
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
