import "@typespec/openapi3";

@service({ title: "Telegram Game API", version: "1.0.0" })
@useDependency("@typespec/openapi3")
namespace TelegramGameApi;

model StartRequest {
  tg_id: string;
  username?: string;
}

model StartResponse {
  message: string;
  user_id: int32;
}

model ProfileRequest {
  tg_id: string;
}

model ProfileResponse {
  name: string;
  level: int32;
  experience: int32;
  skills: Skill[];
}

model Skill {
  name: string;
  level: int32;
}

model FightStartRequest {
  tg_id: string;
}

model FightActionRequest {
  tg_id: string;
  action: string;
  skill_id?: int32;
  item_id?: int32;
}

model FightResponse {
  message: string;
  user_hp: int32;
  enemy_hp: int32;
  result?: "win" | "lose" | "draw";
}

model BuyRequest {
  tg_id: string;
  item_id: int32;
}

model ItemsRequest {
  tg_id: string;
}

model ShopItem {
  id: int32;
  name: string;
  description: string;
  price: int32;
}

model ShopResponse {
  message: string;
  items: ShopItem[];
}

model QuestActionRequest {
  tg_id: string;
  action: string;
  quest_id?: int32;
}

model QuestResponse {
  message: string;
  quest_id?: int32;
  success?: boolean;
}

@route("/start")
@post
op createUser(@body StartRequest): StartResponse;

@route("/profile")
@post
op getProfile(@body ProfileRequest): ProfileResponse;

@route("/fight/start")
@post
op startFight(@body FightStartRequest): FightResponse;

@route("/fight/action")
@post
op fightAction(@body FightActionRequest): FightResponse;

@route("/shop/buy")
@post
op buyItem(@body BuyRequest): ShopResponse;

@route("/shop/items")
@post
op getItems(@body ItemsRequest): ShopResponse;

@route("/quest")
@post
op handleQuest(@body QuestActionRequest): QuestResponse;