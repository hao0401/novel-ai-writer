from app.database import Base, engine, SessionLocal
from app.models import Chapter, Character, Novel, Outline, User, WorldSetting
from app.utils.security import hash_password
from app.utils.text import count_cn_words


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "demo").first()
        if not user:
            user = User(username="demo", pen_name="青页作者", password_hash=hash_password("123456"))
            db.add(user)
            db.commit()
            db.refresh(user)

        novel = db.query(Novel).filter(Novel.user_id == user.id, Novel.title == "《深青档案》").first()
        if novel:
            print("Seed data already exists.")
            return

        novel = Novel(
            user_id=user.id,
            title="《深青档案》",
            genre="都市",
            style="悬疑爽文",
            target_platform="番茄小说",
            synopsis="落魄写手陆知行收到能预言现实的投稿回执，被迫进入平台、旧稿和隐秘组织交织的内容迷局。",
            tags="都市,悬疑,逆袭,AI创作,强剧情",
            selling_points="把网文投稿、AI创作和都市悬疑结合，主角用文本推演能力反制现实危机。",
            status="创作中",
        )
        db.add(novel)
        db.commit()
        db.refresh(novel)

        db.add(Character(
            novel_id=novel.id,
            name="陆知行",
            role_type="主角",
            identity="落魄写手",
            personality="克制、敏锐、有底线",
            goal="查清父亲旧稿失踪真相",
            ability="从文字细节推演人物未来选择",
            background="长期在创作和现实压力之间挣扎",
            relation_to_protagonist="本人",
            plot_function="成长线与解谜线核心",
        ))
        db.add(WorldSetting(
            novel_id=novel.id,
            world_background="现实都市之下存在由故事、流量和读者情绪驱动的隐秘秩序。",
            era_environment="近未来内容平台高度竞争，AI 辅助创作普及。",
            geography="海城、旧城区档案馆、平台总部。",
            organizations="青页编辑部、暗稿会、平台风控组。",
            hierarchy="普通作者、签约作者、头部作者、规则掌控者。",
            power_system="对文本因果的感知、改写和承担代价。",
            important_rules="越强的改写越需要现实代价。",
            taboos="不能改写已公开发布的核心事实。",
        ))
        outline = Outline(
            novel_id=novel.id,
            outline_type="章节大纲",
            chapter_number=1,
            chapter_title="第1章 旧稿里的预言",
            chapter_goal="建立投稿回执预言的强钩子。",
            main_plot="主角收到异常回执，发现父亲旧稿与现实吻合。",
            conflict="平台邀约与未知警告同时出现。",
            highlight="主角第一次验证旧稿预言。",
            cliffhanger="旧稿多出一行新标题。",
            expected_words=2000,
        )
        db.add(outline)
        db.commit()
        db.refresh(outline)
        content = "凌晨三点，陆知行盯着屏幕上那封投稿回执，指尖迟迟没有落下。\n\n回执最后一行写着：明天上午九点十七分，青页大厦三楼会议室，不要签那份合同。"
        db.add(Chapter(
            novel_id=novel.id,
            outline_id=outline.id,
            chapter_number=1,
            title=outline.chapter_title,
            content=content,
            highlights="投稿回执预言形成开篇钩子。",
            foreshadowing="父亲旧稿和青页大厦合同。",
            status="草稿",
            word_count=count_cn_words(content),
        ))
        db.commit()
        print("Seed data created. demo / 123456")
    finally:
        db.close()


if __name__ == "__main__":
    run()
