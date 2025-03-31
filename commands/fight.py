import logging
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes
)
from sqlalchemy.orm.attributes import flag_modified
from db.db import Item, User, Monster
from db.dbSession import session
from gui.keyboards import main_menu_keyboard

def get_random_monster():
    monsters = session.query(Monster).all()
    monster = random.choice(monsters)
    from copy import deepcopy
    return deepcopy(monster)

async def fight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_tg_id = str(update.effective_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()

    if not user:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сначала создайте персонажа с помощью /start.",
            reply_markup=main_menu_keyboard()
        )
        return

    if user.energy <= 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="У вас закончилась энергия. Подождите, пока она восстановится.",
            reply_markup=main_menu_keyboard()
        )
        return

    mock_skills = [
        {"id": 1, "name": "Огненный шар", "mana_cost": 10, "type": "damage", "power": 15},
        {"id": 2, "name": "Лечение", "mana_cost": 8, "type": "heal", "power": 20},
        {"id": 3, "name": "Щит", "mana_cost": 5, "type": "buff_defense", "power": 7}
    ]

    monster = get_random_monster()
    current_round = 1
    monster_current_hp = monster.health
    user_current_hp = user.health
    user_current_mana = user.mana
    
        
        
    inventory_items = user.inventory if isinstance(user.inventory, dict) else {}
    
    if inventory_items:
        item_ids = [int(item_id) for item_id in inventory_items.keys()]
        items = session.query(Item).filter(Item.item_id.in_(item_ids)).all() if item_ids else []
        
        items_dict = {str(item.item_id): item for item in items}
        
        inv = []
        for item_id, count in inventory_items.items():
            item = items_dict.get(item_id)
            if item:
                inv.append({
                    "id": item.item_id,
                    "name": item.name,
                    "type": item.type,
                    "count": count,
                    "power": item.power 
                })

    context.user_data['fight_context'] = {
        'monster': monster,
        'monster_hp': monster_current_hp,
        'user_hp': user_current_hp,
        'user_mana': user_current_mana,
        'round': current_round,
        'user_energy': user.energy,
        'items': inv,
        'skills': mock_skills,
        'buffs': {'attack': 0, 'defense': 0}
    }
    
    await send_round_info(update, context, user, monster, current_round)

async def send_round_info(update, context, user, monster, round_num):
    fight_context = context.user_data['fight_context']
    
    keyboard = []
    
    keyboard.append([InlineKeyboardButton("⚔️ Атаковать", callback_data="fight_attack")])
    
    for item in fight_context['items'][:3]:
        keyboard.append([InlineKeyboardButton(f"🎒 {item['name']} - {item['count']}шт", 
                                          callback_data=f"fight_useitem_{item['id']}")])
    
    for skill in fight_context['skills'][:3]:
        keyboard.append([InlineKeyboardButton(f"🔮 {skill['name']} (🔵{skill['mana_cost']})", 
                                          callback_data=f"fight_useskill_{skill['id']}")])
    
    keyboard.append([InlineKeyboardButton("🏃 Бежать", callback_data="fight_flee")])
    
    buffs_text = ""
    if fight_context['buffs']['attack'] > 0:
        buffs_text += f"\n⚔️ Бафф атаки: +{fight_context['buffs']['attack']}"
    if fight_context['buffs']['defense'] > 0:
        buffs_text += f"\n🛡️ Бафф защиты: +{fight_context['buffs']['defense']}"
    
    message = (
        f"⚔️ Раунд {round_num} ⚔️\n"
        f"Ваше здоровье: {fight_context['user_hp']}/{user.health}\n"
        f"Мана: {fight_context['user_mana']}/{user.mana}\n"
        f"Здоровье {monster.name}: {fight_context['monster_hp']}/{monster.health}\n"
        f"{buffs_text}\n\n"
        f"Выберите действие:"
    )
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def fight_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    u_tg_id = str(query.from_user.id)
    user = session.query(User).filter_by(tg_id=u_tg_id).first()
    fight_context = context.user_data.get('fight_context')
    
    if not fight_context or not user:
        await query.edit_message_text(text="Бой уже завершен.")
        return
    
    monster = fight_context['monster']
    action = query.data.split('_')[1]
    result_message = ""
    
    if action == "attack":
        user_attack = calculate_user_attack(user, fight_context['buffs']['attack'])
        monster_damage = max(1, user_attack - monster.defense)
        fight_context['monster_hp'] -= monster_damage
        result_message = f"Вы атаковали и нанесли {monster_damage} урона!"
        
    elif action == "useitem":
        item_id = int(query.data.split('_')[2])
        item = next((i for i in fight_context['items'] if i['id'] == item_id), None)
        if not item:
            result_message = "Предмет не найден!"
        else:
            effect_message = apply_item_effect(user, item, fight_context)
            
            print("Item",item)
            print("Item_id",item_id)
            user.inventory[str(item['id'])] = user.inventory.get(str(item['id']), 0) - 1
            if user.inventory[str(item['id'])] <= 0:
                del user.inventory[str(item['id'])]
                logging.info(f"Предмет {item['name']} удален из инвентаря пользователя {u_tg_id}")

            flag_modified(user, "inventory")
            result_message = f"Вы использовали {item['name']}!\n" + effect_message
            try:
                session.add(user)
                session.commit()
                effect_message = apply_item_effect(user, item, fight_context)
                result_message = f"Вы использовали {item['name']}!\n" + effect_message
            except Exception as e:
                session.rollback()
                logging.error(f"Ошибка при сохранении инвентаря: {e}")
                result_message = "Ошибка при использовании предмета!"
    
    elif action == "useskill":
        skill_id = int(query.data.split('_')[2])
        skill = next((s for s in fight_context['skills'] if s['id'] == skill_id), None)
        if not skill:
            result_message = "Навык не найден!"
        elif fight_context['user_mana'] < skill['mana_cost']:
            result_message = "Недостаточно маны для использования навыка!"
        else:
            effect_message = apply_skill_effect(user, skill, fight_context)
            fight_context['user_mana'] -= skill['mana_cost']
            result_message = f"Вы использовали {skill['name']}!\n" + effect_message
    
    elif action == "flee":
        if random.random() < 0.6:
            user.energy -= 1
            session.commit()
            await query.edit_message_text(
                text="Вы успешно сбежали от монстра! (Энергия -1)",
            )
            context.user_data.pop('fight_context', None)
            return
        else:
            result_message = "Вам не удалось сбежать!"

    if fight_context['monster_hp'] <= 0:
        reward_gold = random.randint(10, 20) * fight_context['round']
        reward_xp = random.randint(20, 30) * fight_context['round']
        
        user.gold += reward_gold
        user.xp += reward_xp
        user.energy -= 1
        session.commit()
        
        await query.edit_message_text(
            text=f"{result_message}\n\nВы победили монстра {monster.name}!\n"
                 f"Получено: {reward_gold} золота и {reward_xp} опыта."
        )
        context.user_data.pop('fight_context', None)
        return
    
    if action != "flee":
        monster_attack = calculate_monster_attack(monster)
        user_defense = user.defense + fight_context['buffs']['defense']
        user_damage = max(1, monster_attack - user_defense)
        fight_context['user_hp'] -= user_damage
        result_message += f"\n{monster.name} атакует в ответ и наносит {user_damage} урона!"
    
    if fight_context['user_hp'] <= 0:
        user.energy -= 1
        session.commit()
        
        context.user_data.pop('fight_context', None)
        await query.edit_message_text(
            text=f"{result_message}\n\nВы проиграли в бою с {monster.name}! (Энергия -1)",
        )
        return
    
    if fight_context['buffs']['attack'] > 0:
        fight_context['buffs']['attack'] = max(0, fight_context['buffs']['attack'] - 1)
    if fight_context['buffs']['defense'] > 0:
        fight_context['buffs']['defense'] = max(0, fight_context['buffs']['defense'] - 1)
    
    fight_context['round'] += 1
    await query.edit_message_text(text=result_message)
    await send_round_info(update, context, user, monster, fight_context['round'])

def calculate_user_attack(user, attack_buff=0):
    base_attack = user.attack + attack_buff
    final_attack = base_attack + random.randint(-base_attack // 10, base_attack // 10)
    return max(1, final_attack)

def calculate_monster_attack(monster):
    base_attack = monster.attack
    final_attack = base_attack + random.randint(-base_attack * 15 // 100, base_attack * 15 // 100)
    return max(1, final_attack)

def apply_item_effect(user, item, fight_context):
    effect_message = ""
    
    if item['type'] == "heal":
        heal_amount = item['power']
        max_hp = user.health
        fight_context['user_hp'] = min(max_hp, fight_context['user_hp'] + heal_amount)
        effect_message = f"Восстановлено {heal_amount} здоровья."
    
    elif item['type'] == "buff_attack":
        fight_context['buffs']['attack'] = item['power']
        effect_message = f"Ваша атака увеличена на {item['power']} на 3 раунда."
    
    elif item['type'] == "escape":
        user.energy -= 1
        session.commit()
        effect_message = "Вы использовали дымовую шашку и сбежали!"
        fight_context['user_hp'] = 0
    
    return effect_message

def apply_skill_effect(user, skill, fight_context):
    effect_message = ""
    
    if skill['type'] == "damage":
        damage = skill['power'] + user.magic_attack // 2
        fight_context['monster_hp'] -= damage
        effect_message = f"Нанесено {damage} магического урона."
    
    elif skill['type'] == "heal":
        heal_amount = skill['power'] + user.magic_attack // 2
        max_hp = user.health
        fight_context['user_hp'] = min(max_hp, fight_context['user_hp'] + heal_amount)
        effect_message = f"Восстановлено {heal_amount} здоровья."
    
    elif skill['type'] == "buff_defense":
        fight_context['buffs']['defense'] = skill['power']
        effect_message = f"Ваша защита увеличена на {skill['power']} на 3 раунда."
    
    return effect_message