# Act Two — Authored Content (multi-agent workflow)

I'll assemble the full Act Two shooting script now. This is a delivery task, so I'll write the complete Markdown directly as my response.

# ACT TWO SHOOTING SCRIPT — "THE THEATRICAL CROWN"
### Zone: The Twisted Castle Kingdom · Pillar: PROJECTILE COMBAT + ARENA DODGING
*An ordered, build-from-this engineering script. Top-down 2D pygame. Combat NON-LETHAL. Telegraphs honest. Restraint rewarded immediately. Bosses out-THOUGHT, not out-DPS'd.*

---

## HOW TO READ THIS DOC

- **Dialogue** is a list of `{speaker, text}`. **Choices** are `{prompt, options:[{label, tag, effect, result:[...]}]}` where `tag ∈ {mercy, survival, cruelty, neutral}` and `effect` is the engine keyword to fire.
- **Map sketches** use: `#`=wall · `P`=processional path · `f`=festival floorboards (open kill-floor) · `C`=crate/pillar cover · `cart`=overturned cart/podium cover · `r`=rubble · `b`=bush · `g`=gate/gap · `=`=velvet rope · `S`=spotlight rig · `@`=player spawn · `K`=cage (captive) · `H`=Herald podium · `A`=Ankam podium · `$`=shop stall · `▮`=decree board / banner-fragment.
- **Polish notes are already folded in.** Where a line was revised per the script-doctor pass, it is marked `[VOICE-FIX #n]`. Feasibility cuts are applied and marked `[FEAS #n]`.
- **Carry-in flags from Act One** that branch content: `ankam_mercy` / `ankam_survival` / `ankam_cruel` (Ankam's Act One disposition) → drives `ankamReturn` variant.

---

# SCENE 1 — THE GILDED GATE
**id:** `kingdom_gate` · **Title:** *The Gilded Gate*

**Purpose:** Arrival. Establish gold-and-rot tone + the Festival of Gratitude nobody is grateful for. Reintroduce Rook. Teach that the kingdom runs on enforced cheer. Plant the captured-villager thread. First taste of projectile combat as a "welcome."

**Present:** Player (`@`), Rook, Loudspeaker Cart (prop), Cheer Warden (gate sentry / tutorial enemy).

### MAP — Gate Approach (single-screen cinematic + tutorial strip)
```
########################################
# (rise / vista of castle town below)  #
#   @....P.........P..........P......g  #   g = gate (locked until tutorial clears)
#        ^Rook    [cart deco]    [Cheer #
#   b b                          Warden]#
########################################
   ^ tutorial lunge/dodge happens on the open P strip toward g
```
Camera reveals the gilded-corpse town below on entry; the courtesy-volley tutorial plays out on the open path; gate `g` opens after.

### BEATS
1. Player + Rook crest the rise; the castle town glitters below — gold leaf flaking off wet timber.
2. A loudspeaker-cart trundles past blaring mandatory gratitude.
3. A **Cheer Warden** clocks the player and "welcomes" them with a warning shot — **first telegraphed projectile; dash-dodge taught in fiction.**
4. Rook explains the Festival of Gratitude; the captured villager (Old Wend's daughter) is to be "awarded" to Sufflok on the main stage.
5. **CHOICE — set the player's stated goal** (mercy/survival/cruelty).
6. Gate opens; Rook can't follow openly (his face is on posters) — he peels off to the back alleys; the player walks in alone.

### DIALOGUE
1. **Rook:** "There it is. The Twisted Castle Kingdom. Looks like someone gilded a corpse and called it a celebration."
2. **Rook:** "See the gold leaf? It's peeling. Whole place is gold paint over wet wood. You lean on the wrong wall here and your hand comes away shining and rotten at the same time. That's the kingdom. Remember it."
3. **???:** *(A cart rolls past on squealing wheels. A brass horn bolted to its roof blares the same line over and over, too loud, slightly warped.)*
4. **Loudspeaker Cart:** "GRA-TI-TUDE IS MAN-DA-TORY. SMILE AT INTERVALS. UN-GRATEFUL CITIZENS WILL BE NOTED. ENJOY THE FESTIVAL OF GRATITUDE. SMILE AT INTERVALS."
5. **Rook:** "Festival of Gratitude. Every soul in there is grateful at gunpoint. You don't clap, a warden writes your name down. You clap wrong, a warden writes your name down. Survival tip — clap medium."
6. **Cheer Warden:** "HALT, traveler. New face. New faces are SO exciting and also a SECURITY CONCERN. Hold still while I assess your festival spirit."
7. **???:** *(The warden raises a stubby brass launcher. A bright bead of light winks at its mouth — a clear, slow, honest warning glow. It is aimed at the ground three steps ahead of you.)*
8. **Cheer Warden:** "Just a courtesy volley! Don't take it personally! Everyone gets a courtesy volley! DASH-DANCE for me, won't you? It's tradition!"
9. **???:** *(The bead brightens — then a confetti-charge POPS where you were standing. You felt the wind of it. Step through the gap the next time it telegraphs, and it can't touch you. That is the whole game here: read the flash, move through it, not away from it.)*

> **TUTORIAL HOOK (engine):** The courtesy volley fires on a fixed loop until the player successfully **dashes THROUGH** the telegraphed line once (i-frames clear it). On success, advance dialogue; gate unlocks. No damage is dealt on the first loop even if hit — this is the teaching beat.

10. **Rook:** "Easy! That's just the welcome. In this town the guards SHOOT instead of swing. Everything flashes before it fires — that bead of light, that's your tell. When it flashes, you dash THROUGH the line, not back from it. Back from it is where the next one lands."
11. **Rook:** "And listen — this isn't a supply run anymore. They've got someone. A villager from up our valley. Old Wend's daughter. They're calling her the festival's 'guest of honor.' They're going to put her on the main stage and 'award' her to Sufflok like a ribbon. In front of a cheering crowd that's too scared to look away."
12. **Rook:** "I can't walk in there. My face is on every other post. But you came out of the SKY. There's no poster for that yet. So you go in the front, I go in the cracks, and somewhere in the middle we steal her back. You good?"

### CHOICE — "Why are you really going in there?"
| label | tag | effect |
|---|---|---|
| *"To get her out. Nobody gets 'awarded' to anyone."* | **mercy** | `set_goal_rescue` |
| *"A festival this loud is the best cover for slipping out alive."* | **survival** | `set_goal_survive` |
| *"By the time I leave, this castle is going to be afraid of me."* | **cruelty** | `set_goal_fear` |

**MERCY result:**
- **You:** "Nobody gets handed to a tyrant like a prize. I don't care how the crowd claps. We get her out, and we get her home."
- **Rook:** "...You say that out loud in there and a warden writes it down. Say it quiet, mean it loud. Come on. Let's go steal a person back from a party."

**SURVIVAL result:**
- **You:** "Everyone's looking at the stage. Wardens included. That's the only time a place like this stops looking at the exits. We use the noise. We grab her in the gap, and we're gone before the applause stops."
- **Rook:** "Cold. Smart-cold, the kind I like. Yeah. The crowd's the loudest the second before Sufflok's name. That's our window. Don't fall in love with the plan — just be standing in the right place when it cracks open."

**CRUELTY result:**
- **You:** "They run on fear. Fine. I'll give them something newer to be afraid of than him. By the time I'm done, the wardens flinch when I walk."
- **Rook:** "...Hey. HEY. The girl. We're here for the girl, remember? Fear's a tool, sure. But you keep reaching for the same tool, one day it's the only one in your hand. ...Just go. I'll be in the cracks."

> **EXIT:** Gate `g` opens. Rook departs to alleys (despawns from hub overworld, reappears scripted later). Player enters Scene 2.

---

# SCENE 2 — THE COURT TOWN & THE STAGING YARD
**id:** `court_town_hub` · **Title:** *The Court Town & the Staging Yard*

**Purpose:** Act Two HUB. Frightened citizens performing joy. Establish CHITS economy + shopkeeper stall location. Surface castle gossip. Introduce the RIGGED DECREE puzzle (contest built to lose). Stage the captive's holding spot (Yew, in a gilded "guest cage"). Optional moral beat with a terrified warden recruit.

**Present:** Player, Cheer Warden (drilling citizens), Rehearsing Citizen, Frightened Citizen, Yew (in cage, distant), Festival Clerk (at decree board), Rook (in a shadow gap), Warden Recruit (choice NPC blocking path to shop).

### MAP — Staging Yard (hub, free-roam)
```
##########################################
#  [entry from gate]                     #
#  P............ ▮ DECREE BOARD ..........#
#        [Clerk]        THRONE-PROP       #
#   $ SHOP        ███████████  banners    #
#  (west awning)  █  throne  █  WE LOVE   #
#                 ███████████  TO GIVE    #
#   [Recruit]                             #
#   blocks path        [stage stairs] K   #  K = Yew's gilded "guest cage"
#   to $                  ↑ to Festival   #
#   ..Rook (shadow gap between grandstands)#
##########################################
```
Free-roam hub. Banners drip in drizzle: `WE LOVE TO GIVE`, `THANK YOU FOR TAKING`, `GRATITUDE BUILDS CHARACTER`, plus a fifth scrubbed half-blank. Decree board `▮` near the throne-prop. Shop `$` west under the ugly awning. Cage `K` by the stage stairs (rescue objective, always visible).

### BEATS
1. Player enters the staging yard: half-built grandstands, giant gilded throne-prop, banners drying in rain.
2. Citizens rehearse cheering on cue, terrified of doing it wrong; one whispers real info when wardens aren't looking.
3. **DECREE BOARD** posts the Festival Petition — a contest whose wording guarantees the petitioner loses and is mocked.
4. Player glimpses **Yew** in the "guest cage" dressed up as a place of honor.
5. Player is pointed to the **Weird Shopkeeper's** crooked stall (west) for supplies, chits, and truth-shaped gossip.
6. **CHOICE** — optional moral beat with a terrified Warden Recruit blocking the path to the shop.

### DIALOGUE
1. **???:** *(The staging yard is enormous and unfinished. A throne the size of a hay cart sits center, dripping gold paint. Banners sag in the drizzle: WE LOVE TO GIVE. THANK YOU FOR TAKING. GRATITUDE BUILDS CHARACTER. Someone has scrubbed a fifth banner half-blank.)*
2. **Cheer Warden:** "FROM THE TOP! On my mark you are OVERJOYED. Not pleased. OVERJOYED. Pleased is a fineable offense. And — MARK!"
3. **Rehearsing Citizen:** "Hoo. Ray. Hoo... ray. We are. So grateful. To give. Everything. We have. Hoo. Ray."
4. **Cheer Warden:** "FLATTER. I heard a HALF-second of doubt in that 'hooray.' Doubt is the enemy of the Festival. Again. Smile until it HURTS, and then keep going past the hurt. That's the FUN part."
5. **Frightened Citizen:** *(low, not moving her lips)* "Don't look at me when I talk. Look at the throne. Good. You're new — you don't have the festival flinch yet. Everyone in here has it. You'll get it."
6. **Frightened Citizen:** *(still smiling at nothing)* "They've got a girl in the guest cage by the stage stairs. They put RIBBONS on the bars. Call her the guest of honor. She's from the valley. Whatever you are — and I think you're something — somebody should cut those ribbons before the third bell."
7. **???:** *(Past her shoulder, by the stage stairs: a cage gilded to look like a gift box, bow and all. Inside, a young woman sits very straight, refusing to perform fear. Her eyes find yours for exactly one second. She does not wave. She does not smile. Good for her.)*
8. **Yew:** *(too far to hear, but you can read it on her mouth)* "— don't. Make a scene. Not yet."
9. **???:** *(A lacquered DECREE BOARD stands near the throne, ringed by citizens who badly want something and are afraid to ask. A herald-clerk in a too-big coat hovers beside it, delighted.)*
10. **Festival Clerk:** "STEP UP, step up! By the boundless generosity of the Festival, ANY citizen may submit a Petition for a Boon! Win the Petition and the Court grants your heart's desire! It's FAIR! It's a CONTEST! It's GOVERNANCE AS ENTERTAINMENT!"
11. **Festival Clerk:** "The Petition reads — ahem — 'The petitioner shall be granted whatsoever they ASK FOR, provided they ask for NOTHING the Court does not WISH to give.' Beautiful, isn't it? Airtight. Nobody's ever won. Ha! Nobody CAN. ...You should try, though. The crowd loves a loser."
12. **???:** *(You read it twice. It is rigged — of course it's rigged. But rigged things are built out of words, and words have edges. Tuck that away. The exact WORDING is the whole game.)*
13. **Rook:** *(from a shadowed gap between grandstands)* "Pssst. Over here, don't crowd me. You see the decree board? It's a humiliation engine. People walk up, ask for a pony, walk away owing the Court a pony. The crowd laughs, the Court looks generous for letting them lose. Don't play it straight — straight is how it eats you." `[VOICE-FIX #1]`
14. **Rook:** "But — and I hate that I'm saying this — there might be a real answer hiding in that garbage wording. If you can ask for something the Court can't refuse without admitting the whole thing's a lie... that's a key, not a contest. Chew on it. First, though — go see the shopkeeper. Crooked stall, west side, under the ugliest awning you've ever seen. They've got gear, and they've got mouth. Some of the mouth is even true."
15. **Rook:** "Money here is CHITS — little brass festival tokens. Wardens drop them, the Court hands them out for 'good cheer,' people lose them in the gutters. Pick them up. The shopkeeper doesn't take gratitude as payment. Smart of them, really."

### CHOICE — "A young warden recruit is shaking through her cheer drill, clearly new and clearly terrified. She's blocking the path to the shop. What do you do?"
| label | tag | effect |
|---|---|---|
| *"Breathe. You don't have to mean it. Just get through the day."* | **mercy** | `calm_recruit` |
| *"Where do the wardens stash their off-duty chits? Quietly."* | **survival** | `give_chits` |
| *"Stand aside, recruit. You really don't want to make me ask twice."* | **cruelty** | `scare_recruit` |

**MERCY result (`calm_recruit`):**
- **You:** "Hey. Look at me, not the warden. You don't have to MEAN the cheering. You just have to get through today, and then the next one. Breathe. There you go."
- **Warden Recruit:** "I— you're not supposed to— nobody talks to me like I'm... thank you. There's a chit pouch the last recruit dropped behind the prop crate. I never reported it. Take it. And — the guest cage ribbons are knotted, not locked. That's all I'll say."
- **???:** *(She slips you a small handful of chits. Mercy bought a fact and a friend in one breath. Worth more than the coins.)*
> **PAYOFF (legible, immediate):** grant chits + set flag `ribbon_intel` (ribbons are knotted-not-locked → reinforces the rescue is doable by hand).

**SURVIVAL result (`give_chits`):**
- **You:** "You look like you'd rather be anywhere else. Tell you what — point me to where the off-duty wardens drop their chits, and I was never here asking."
- **Warden Recruit:** "...The prop crate. Behind the throne. They toss their pouches there during drills so they don't rattle. I didn't tell you. I'm too scared to have told you anything."
- **???:** *(A quiet trade. No one's better off and no one's worse. You pocket the location and move on — which is its own kind of mercy out here, and its own kind of nothing.)*
> **PAYOFF:** mark a chit-stash pickup behind the throne prop crate.

**CRUELTY result (`scare_recruit`):**
- **You:** "You're in my way, recruit. I've had a long week and a longer fall through the sky. Stand aside, and don't make me ask a second time."
- **Warden Recruit:** "Y-yes. Sir. Ma'am. Sky-person. There's — there's a chit pouch behind the prop crate, take it, take whatever, just — please don't tell my warden I froze, please—"
- **???:** *(She bolts. You got the chits and the path. You also just taught the newest, smallest person in this castle that the answer to fear is more fear. The lesson takes fast here. Too fast.)*
> **PAYOFF + COST:** grant chits; nudge **castle-fear / cruelty** counter (this recruit-fear beat thematically rhymes with Ankam's "fear rolls downhill" in Scene 5).

> **EXIT:** Free-roam. Player may visit **Shop (Scene 3)** any time, then return to the **Decree Board** to begin the puzzle / build-up (Scene 4). Recommended order: Shop → Puzzle.

---

# SCENE 3 — THE CROOKED STALL (SHOP)
**id:** `shopkeeper_stall` · **Title:** *The Crooked Stall*

**Purpose:** Introduce the Weird Shopkeeper, the CHITS shop, the consumable inventory, and the SLING UPGRADE. Deliver half-true castle gossip + the one real sliver about the portal. The shopkeeper is circular, suspicious, oddly kind, never quite lying.

**Present:** Player, Weird Shopkeeper.

> **[FEAS #3]** The "somehow bigger inside" is a single flavor line + a standard **shop overlay menu** opened on interact. **Do NOT build a TARDIS interior transition.**

### MAP — Shop Overlay
```
+------------------ SHOP ------------------+
| [ugliest awning in the kingdom]          |
| ITEMS                 CHITS: ###          |
|  Pressed Bandage        8                 |
|  Smokebead             14                 |
|  Wax-Lined Pouch       18  (1x)           |
|  Whipcord Sling        42  (1x)           |
|  Grateful Loaf          6                 |
|  Counterfeit Token     24  (1x)           |
| [Talk] [Buy] [Leave]                      |
+------------------------------------------+
```

### SHOP STOCK (from `shop.items`)
| id | name | cost (chits) | effect | one-time? |
|---|---|---|---|---|
| `bandage` | Pressed Bandage | 8 | `heal` (closes 2 hearts) | no |
| `smokebead` | Smokebead | 14 | `smoke_escape` (~3s invisibility) | no |
| `pebble_pouch` | Wax-Lined Pouch | 18 | `ammo_capacity_up` (+6 pebbles, refills fuller per zone) | **yes** |
| `whipcord_sling` | Whipcord Sling | 42 | `upgrade_sling` (HOLD = charged harder KO) | **yes** |
| `chit_loaf` | Grateful Loaf | 6 | `heal_small` (1 heart) | no (stackable) |
| `festival_token` | Counterfeit Festival Token | 24 | `decree_loophole` (legal fair-footing for the contest) | **yes** |

**Flavor (display on hover/inspect):**
- **Pressed Bandage:** "A tight roll of clean linen with a smell of someone's grandmother in it. Closes two hearts. 'Fixes most things a hero does to himself' — not nothing and not enough."
- **Smokebead:** "Crack it underfoot and you become, for three glorious seconds, a rumor. Spotlights slide off you, pikemen aim at where you were. 'Theater-grade fog, perfectly legal, do not ask which theater.'"
- **Wax-Lined Pouch:** "Carries six more pebbles and refills fuller at each new zone. 'More stones, same gentle intent.' Permanent upgrade; buy it once."
- **Whipcord Sling:** "Your worn sling, rebraided with a tensioned whipcord. HOLD to charge a shot that drops a guard in one clean snap — still a knockout, never a kill. 'Hit nothing fatal. Hit it twice as hard. Both true.'"
- **Grateful Loaf:** "Festival bread stamped with Sufflok's grinning seal. Restores one heart, tastes faintly of obligation. 'Eat the propaganda.' Cheap, stackable, ironic."
- **Counterfeit Festival Token:** "A brass token that 'proves' you are a registered, grateful contestant. Present it and the rigged decree must, by its own wording, let you enter on fair footing. He won't say where he got the die-stamp."

### PRICING RULES — `discountForMercy` (legible restraint payoff; design-contract requirement)
- **MERCY (dominant lean, or arrives sling-stowed with a KO-not-killed record this zone):** all prices **−25% (round down)**; **Grateful Loaf gifted free on first visit**; **2 lore lines** offered. Shopkeeper notices warmly + suspiciously.
- **SURVIVAL (neutral baseline):** fair prices, no gift, **fullest practical intel + first crack at restock**, 2 lore lines.
- **CRUELTY (dominant lean):** **−10%** nervous "please-just-leave" discount on *consumables only*; **Whipcord + Counterfeit Token SPIKE +30%**; **free loaf withheld**; **only 1 lore line** per visit. *The world literally sells the frightened player less truth.*

> **AMMO/ECONOMY GUARDRAIL** `[FEAS — fairness]`: Wax-Lined Pouch is the pressure valve. With MERCY discount ≈ 13 chits; a clean Scene-6 forecourt run (chit drops + recruit/Ankam gifts) clears ~25–40 chits → affordable for MERCY/SURVIVAL pre-boss. CRUELTY pays full + Whipcord spike, but CRUELTY's boss resolution needs **no** pebbles, so it is poorer, never softlocked.

### INTRO DIALOGUE (`shopkeeperIntro`) — first entry
1. **???:** *(The awning over the crooked stall is the ugliest thing in a kingdom that prides itself on gilded ugliness. It is the color of a bruise that has read about other bruises. You duck under it — and the stall is somehow bigger inside than the awning could ever cover.)*
2. **Weird Shopkeeper:** "There you are. Took you a moment. Most people take a lifetime, so — early! Punctual sky-thing. I do approve."
3. **Weird Shopkeeper:** "Don't gawp at the size of the place. The awning's small. The stall is not. The trick is that I measure my shop in how much it has to HOLD, not in how much room it takes up. Same as a person, really. Same as YOU, I'd wager. A small, terrified outside holding a great deal more than it looks like it can."
4. **Weird Shopkeeper:** "Now. You've got the look of someone about to do something loud and ill-advised on a stage. I sell things for exactly that. Browse. Touch nothing that hums. And we'll see what truths I'm willing to part with today. Spoiler: one. I always part with exactly one. It's a rule, and I'm the one who made it, and I still can't break it. Funny how that works."

### GREETING (`greeting`) — repeat visits
1. **Weird Shopkeeper:** "Ah. AH. There you are. I knew there'd be a there-you-are today — I felt it in the bad knee, and the bad knee is rarely wrong, only occasionally."
2. **Weird Shopkeeper:** "Welcome, welcome, mind the crooked leg of the stall, mind the crooked leg of ME. You've got the look of someone the castle hasn't finished deciding about. That's the best kind of customer. Undecided people buy more."
3. **Weird Shopkeeper:** "Coin here is chits. Little brass nothings the court mints so it can pretend everyone's rich. You'll prize them loose from guards who lie down for you, from stashes nobody guards because nobody admits they're there, and from doing favors the festival forgot to ban."
4. **Weird Shopkeeper:** "I sell bandages, smoke, more room for your stones, and — lean in — a way to make that sad little sling of yours BITE. I also sell talk. Half of it's true. I'll never tell you which half, because then I'd only be worth half as much, you see how that works."
5. **Weird Shopkeeper:** "So. What does an undecided person want today: to last longer, to vanish cleaner, to throw harder, or just to hear a thing they shouldn't?"

### WARES PATTER (the full in-fiction menu walk; play once after intro)
1. **Weird Shopkeeper:** "You're the sky one. Don't make the face. Everyone makes the face. Yes, I knew. No, nobody told me. I just keep a list of things that haven't happened yet and tick them off as they arrive — you were near the top." *(retain ONCE here; see VOICE-FIX #6 — the schedule motif is otherwise cut from this scene)* `[VOICE-FIX #6]`
2. **Weird Shopkeeper:** "Now. You'll want THINGS. Everyone who lives wants things; it's the dead who travel light. Let me show you the wares. Don't touch the ones that hum."
3. **Weird Shopkeeper:** "BANDAGES — rolled tight, clean-ish, mends a heart back into you when the wardens nip too deep. SMOKEBEADS — crush one and for a breath or three the whole world forgets which shadow you're in. PEBBLE POUCH — because an empty sling is just a sad bit of leather and regret."
4. **Weird Shopkeeper:** "And THIS. Come closer. The WHIPCORD SLING. Your little sling, but meaner — hold the throw, let it wind up, and it cracks out a shot with weight behind it. Knocks the cheer clean out of a warden through cover. Still won't kill. I don't sell killing. I find it bad for repeat business and worse for the soul. You only get the one soul; I checked."

### GOSSIP / FREE-WITH-PURCHASE (the Herald script + decree hint + portal sliver)
5. **Weird Shopkeeper:** "Free with purchase: GOSSIP. The Festival's centerpiece is a big loud man — the Court Herald. Calls the waves, runs the stage, never throws a punch himself; he CONDUCTS. Pikemen, spotlights that'll cook you where they sweep, confetti cannons that spray more than confetti. He's a maestro of other people's violence."
6. **Weird Shopkeeper:** "Here's the true bit, and I only give one per visit so listen: the Herald cannot improvise. He has a SCRIPT. Knock the script out of his hands — or out of his MOUTH — and he's just a frightened man in a loud coat, and the crowd will SEE it. Crowds are cruel to a man they've stopped believing in. You can use that. You can use it kind, or you can use it like a knife."
7. **Weird Shopkeeper:** "Oh — and the decree board. The petition. People keep ASKING the Court for things. Foolish. You never ask a trap what it wants to give. You ask it for the one thing it would have to STOP being a trap to refuse. ...That's all. That's the whole hint. I've said too much; I always say exactly too much."
8. **Weird Shopkeeper:** "One more thing, since you've a kind face under the terror. The SKY you fell through. The seam of it. I've seen the like before — a long, long time before, mind the dust on that memory. It doesn't open where you fell. It opens where someone WANTS it badly enough. Remember that. Not now. Later. You'll know the later when you're in it."

### LORE BANK (`lore`) — gated by lean (MERCY/SURVIVAL = 2/visit, CRUELTY = 1/visit)
1. **Weird Shopkeeper:** "You fell through a door, didn't you. No — don't make the face, the face confirms it. We get one of you every so often. The court calls it 'the sky misbehaving.' I call it traffic."
2. **Weird Shopkeeper:** "Doors that open BOTH ways were outlawed. Not closed. Outlawed. There's a difference, and the difference is somebody up the hill is very afraid of one swinging the wrong direction."
3. **Weird Shopkeeper:** "Sufflok didn't grow here either, you know. Or he did. The story changes depending who's listening and whether they tip. But there's a version — a quiet one, the kind told with the lamp turned down — where he came through a door just like yours. Scared. Small. Decided to never be small again."
4. **Weird Shopkeeper:** "The Crown they're so proud of? It's paint and pageantry over something old. The CASTLE is the real crown. They built a festival of GRATITUDE around it because a thing you're forced to thank is a thing you've stopped asking questions about."
5. **Weird Shopkeeper:** "That announcer with the golden mouth — the Herald — he can't hurt you. Not with his hands. He hurts you by READING. Every cruelty here comes off a script. Which means a script can be read OUT OF TURN. By someone with the nerve. Two chits says you're the hypothetical."
6. **Weird Shopkeeper:** "And the door home — your door — it's not lost. It's INVENTORIED. Filed. Locked in a ledger, because the worst thing they could do to a way out wasn't destroy it. It was make it PAPERWORK. — Or it opens where someone wants out badly enough. Both are true. That's what frightens me about it; doors don't usually get to be two things. ...That's all I've got. That's already more than I've got. Buy the bandage." `[VOICE-FIX #7]`

### BARKS (`barks`) — random one-liners on idle/browse
- "Chits up front. I've extended credit exactly once and he's a spotlight rig now."
- "Buy something or buy nothing, both are purchases of a kind."
- "Everything here is legal. Everything here is legal in SOME kingdom. I didn't say this one."
- "You're eyeing the Whipcord. Good eye. Bad sling, good eye."
- "The bread's stamped with his face so you can eat your gratitude. Festival irony, two chits cheaper than the salve."
- "Knock 'em out, don't end 'em. The unconscious carry fuller pockets — ask me how I know, then don't."
- "I had a brother in your situation once. Or I had a situation once. Or a brother. The stall ate the details."
- "Smoke's grade-A. Theater grade. Same fog they hide the wires with, funny enough."
- "Prices are softer for the gentle. Coin's a coward; it likes a kind hand."
- "No, I won't tell you about the door. ...Buy two things and I'll tell you a corner of it."
- "Don't haggle. The stall hears haggling and the leg gets crooked-er."
- "You break it, you bought a story about breaking it. Cheaper than the item, honestly."

### CHOICE — "The shopkeeper is watching you the way a cat watches a door. How do you deal with them?"
| label | tag | effect |
|---|---|---|
| *"Thank you. Genuinely. You didn't have to help a stranger."* | **mercy** | `shop_discount` |
| *"How much of that is true, and how much are you selling me?"* | **survival** | `shop_open` |
| *"You know too much. Who do you really work for?"* | **cruelty** | `shop_guarded` |

**MERCY result (`shop_discount`):**
- **You:** "Whatever you are, however you know what you know — thank you. You didn't have to tell a scared stranger anything true. I'll remember it."
- **Weird Shopkeeper:** "...Hm. People say thank you to me about as often as the moon does. Here. Take a few chits off the top, and a bandage on the house. Not charity. An INVESTMENT. I'd like you to keep existing on schedule. I've grown fond of the schedule." *(schedule motif retained here per VOICE-FIX #6)*
- **???:** *(The prices soften. The shopkeeper, impossibly, looks a little less ancient for a moment. Kindness costs you nothing and bought you the only honest discount in the kingdom.)*

**SURVIVAL result (`shop_open`):**
- **You:** "You talk in circles, and circles are how people hide the straight line. So tell me plainly — how much of that is true, and how much are you just moving product?"
- **Weird Shopkeeper:** "Oh, I LIKE you. Sharp. Fine, plainly: the script is true. The spotlights cook, true. The decree's a trap, true. The portal bit — true, but small and old. Everything else is seasoning. A merchant who only sells facts starves. A merchant who only sells lies hangs. I split the difference and I sell EDGES. You'll do the same before this is over."
- **???:** *(No discount, but the full shelf, and a merchant who now respects you. In a place like this, being taken seriously is its own kind of armor.)*

**CRUELTY result (`shop_guarded`):**
- **You:** "You knew I was coming. You know about the sky, the script, the cage. People who know that much are working for somebody. So — who? Sufflok? Don't make me ask the unfriendly way."
- **Weird Shopkeeper:** "Ooh. The KNIFE comes out. I work for ROUND THINGS and a quiet life, friend, and you have just made the room less quiet. I'll still sell to you — coin's coin, and yours spends — but the GOSSIP window has closed for today. You shook the tree. The fruit's gone shy. Buy what you need and mind the awning on your way out; it bites people it doesn't like."
- **???:** *(The shop stays open. The warmth does not. You can still arm up — but the one being who might have liked you in this whole gilded rot now watches you like a debt. Fear works. It always costs.)*

> **[FEAS #9]** The biting awning is **dialogue flavor only**. Optional wink: one-frame sprite-shake + sound on a cruel-lean exit. **Do not build an awning hazard entity.**

---

# SCENE 4 — THE PETITION & THE KNOTTED RIBBONS (PUZZLE + BUILD-UP)
**id:** `rescue_buildup` · **Title:** *The Petition & the Knotted Ribbons*

**Purpose:** Heist-turned-rescue build-up. Solve the **RIGGED DECREE** by exploiting exact wording (the "ask for nothing" loophole). Win → legitimate stage access. Reconnect with Rook (lock the plan). One quiet beat with Yew. Trigger the festival start. **Mr. Ankam reappears officially** (branches off Act One — see ANKAM RETURN block). Ends by pushing the player onto the stage for the boss.

> **NOTE ON TWO PUZZLE STAGINGS:** The bible ships **two** puzzle framings — (A) the **Petition / "ask for nothing"** dialogue puzzle here, and (B) the fuller **"Weigh-In of Gratitude" scale puzzle** detailed below as the *physical* puzzle that immediately gates the boss arena. Build BOTH as a continuous sequence: **Petition (narrative win → stage access)** flows into the **Weigh-In (physical, mechanical break)**. Ankam presides over the Weigh-In; that is where his disposition variant fires. The Weigh-In's three branches map 1:1 to the boss's three resolutions.

**Present:** Player, Festival Clerk, the crowd (implied), Rook, Yew, Mr. Ankam (enters during/after the puzzle).

### MAP — Decree Board approach (within hub; then transitions to Weigh-In hall)
```
##########################################
#  ...........▮ DECREE BOARD .............#
#         [Clerk]    crowd ring           #
#   service-gap (Rook) ↘                   #
#        ........[stage stairs]→ K (Yew)   #
#   →→→ TO WEIGH-IN HALL / THRONE-APPROACH #
##########################################
```

### BEATS
1. Return to the decree board; submit a Petition the Court cannot refuse without exposing the trap.
2. The clerk panics; the "win" grants **legitimate stage access** (festival sash + stage pass) instead of a literal boon.
3. Rook meets the player in a service corridor; lock the rescue to the festival's loudest moment.
4. **Mr. Ankam appears officially** in his Act-One-determined mood (see ANKAM RETURN).
5. Quiet beat with Yew at the cage; **CHOICE** on how to steady her.
6. Third bell tolls; the Herald's voice booms; the player is swept toward the stage and the boss.

### DIALOGUE — THE PETITION
1. **Festival Clerk:** "Back again? Bold. Or stupid. Bold-stupid, my favorite flavor of petitioner. Go on then — state your Boon, loudly, for the crowd, and remember the wording: you may have whatsoever you ask for, provided you ask for nothing the Court does not WISH to give. Ha! Twist away, sky-thing. Twist away."
2. **You:** "Then I petition for this: I ask the Court to grant me NOTHING — and to let me stand upon the festival stage to receive it."
3. **Festival Clerk:** "You ask for... nothing. ...You ask for NOTHING. The Court most certainly WISHES to give nothing, it's the Court's favorite thing to give — so it cannot refuse you, the wording forbids refusal of a wish it already holds — but then it must seat you on the STAGE to receive the nothing, in full view, as a WINNER, which it has never, ever, ever had to—"
4. **Festival Clerk:** "—oh. Oh no. You found the edge. You found the actual edge in it. Nobody finds the edge. I have to — protocol says — a WINNER is granted festival standing and stage access, it's WRITTEN, I can't unwrite it in front of the crowd, they're watching, they SAW you win—"
5. **???:** *(The crowd, starved for anyone to ever beat the Court at anything, lets out a real sound — not rehearsed. A gasp with teeth in it. The clerk thrusts a festival sash and a stage pass at you like they're on fire.)*
6. **Festival Clerk:** "Festival standing. Stage access. By the WORDING. Take it, take it, stop SMILING like that, you're frightening the throne. ...How did you— nobody asks for nothing. Everybody wants SOMETHING. That's the whole— that's how the trap— oh, I have to go lie down inside my coat."

> **ENGINE:** On petition win → grant key items `festival_sash` + `stage_pass`; set flag `stage_access`. (If the player bought the **Counterfeit Festival Token**, an alternate one-line shortcut to fair-footing is also accepted — same flag.)

### DIALOGUE — ROOK LOCKS THE PLAN
7. **Rook:** *(yanking you into a service gap, grinning despite himself)* "I watched the clerk's soul leave his body. You asked the trap for nothing and it had to hand you the STAGE. That's — okay, that's the best thing I've seen all year, and I once saw a warden fall in a fountain."
8. **Rook:** "Here's the plan, and it's thin: the pass gets you up by the cage during the ceremony — legitimately, in the open, which is INSANE and perfect. The festival peaks when the Herald announces the 'award.' That's the loudest, blindest second in the whole kingdom. Everyone watching the stage. THAT'S when the ribbons come off and Yew walks. I'll have a cart in the under-stage tunnel. You just have to survive being on stage with the Herald until the window opens."
9. **Rook:** "And he won't fight you straight — he doesn't fight, he CONDUCTS. Pikemen, spotlights, those confetti cannons. He'll throw a whole show at you and never lift a finger. So you do what the shopkeeper said — you go at the SHOW. The script, the rigging, or his pride. Pick your knife. Just get her out before the last bell, or she's Sufflok's, and we don't get her back from THAT."

### DIALOGUE — QUIET BEAT WITH YEW
10. **Yew:** *(quiet, through the gilded bars, not looking at you, watching the wardens)* "You're the one who asked for nothing. The whole yard's whispering it. ...Don't look so pleased. They put ribbons on a cage and a girl in it and called it an honor. Pleased is what they want from people up here."
11. **Yew:** "I'm not going to scream when it starts. I decided. If I scream they got what they wanted, and they don't get anything from me. So whatever you're planning — I'll be ready, and I'll be quiet, and I will NOT perform being saved either. Understand? I walk out. I don't get carried."

### CHOICE — "Yew is holding herself together by refusing to break. The third bell is close. What do you give her?"
| label | tag | effect |
|---|---|---|
| *"You won't be carried. You'll walk. I'll just hold the door."* | **mercy** | `steady_yew` |
| *"Stay sharp, stay quiet, move the second I move. No heroics."* | **survival** | `brief_yew` |
| *"When it goes loud up there, that fear's a weapon. Don't waste it."* | **cruelty** | `harden_yew` |

**MERCY result (`steady_yew`):**
- **You:** "Then walk. When the ribbons come off, you walk out on your own feet and I'll just be the one holding the door open. No scream. No performance. Just you, leaving, like it was always going to happen."
- **Yew:** "...Okay. Okay. The door, and I do the walking. I can do walking. I've been doing sitting-still-and-furious for two days; walking sounds like heaven. ...Don't die up there, door-holder. I'd hate to walk out and find the door's a corpse."

**SURVIVAL result (`brief_yew`):**
- **You:** "Don't watch me — watch the under-stage stairs. When I move, you move, no slower, no faster. No heroics, no goodbyes, no last looks. We live by being boring at the exact right second."
- **Yew:** "Boring. At the right second. ...You sound like my father. He's the one they hauled me off in front of. Fine. Sharp and quiet and boring. I'll be the most boring rescue you've ever run. Just make it happen before the last bell."

**CRUELTY result (`harden_yew`):**
- **You:** "When I go up there, the whole crowd's about to feel something they've never felt at one of these. Fear. Of me. Of the thing that beat their Court. You ride that wave out the gap while every warden's bowels turn to water. Their fear is our cover. Use it."
- **Yew:** "...I came in here a prisoner. I'm not walking out somebody's weapon, sky-thing. I'll take your gap. But you scare me a little, and I've spent two days NOT being scared on principle, so. Get me out. Then we have a long talk about that look in your eye."

---

## 4B — THE WEIGH-IN OF GRATITUDE (PHYSICAL PUZZLE — gates the boss arena)
**id:** `puzzle_weigh_in` · presided over by **Mr. ANKAM** · captive here = **BELL** (frightened old farmer; the bible's puzzle uses Bell at the Weigh-In and Yew at the festival cage — treat as the *same rescue thread*, two staging beats; if shipping a single captive, use **Yew** throughout and rename Bell's lines).

> **[FEAS #6]** **EXPLOIT B (living subject stands on a pan / physics) is CUT.** It is vestigial (appears in `solution`, never in `steps`). Ship only **EXPLOIT A** (sling cinch-rope → Crown pan drops → Article Three satisfied = SURVIVAL) and **EXPLOIT C** (reveal SERVANT fine-print → Ankam becomes subject = MERCY). CRUELTY uses the confetti-cannon-at-the-eye action.
> **[FEAS #7]** Push/rotate cannon = **single interact** (snap-aim + fire). No drag-rotate minigame.

### MAP — Throne-Approach Weigh-Station
```
##########################################
#  [▮ banner-frag 1]      [▮ banner-frag 2]#  ← Articles I & II (S spotlight sweeps near frag2)
#        ╔═════ KING'S SCALE ═════╗        #
#   @    ║  [subject pan]  [CROWN pan]║    #   CROWN pan = chained GIFT OF ORDER (unliftable)
#        ╚══ fulcrum cinch-rope ═════╝     #   ← SLING target (Exploit A / SURVIVAL)
#   [A Ankam podium]  (painted SUFFLOK-eye)#   ← surveillance "castle-eye" on backdrop
#   [confetti cannon]        [confetti cannon]# ← push+fire (CRUELTY)
#   [Rook behind portcullis] $wing-stall    #
#        [▮ banner-frag 3 + soot 4th line] K#   K = Bell's cage (rear dais); frag3 = Article III
#                  COURT CLOCK ▭▭▭░░ (idle→Pikemen)#
##########################################
```
**Props:** giant gilded balance (2 cart-bed pans), CROWN pan pre-loaded with the chained `GIFT OF ORDER` (lead block, unliftable, **protected** by Article II), painted SUFFLOK-eye backdrop (surveillance device), Ankam's podium, two **CONFETTI CANNONS** (single-interact push+fire), one **SWEEPING SPOTLIGHT** rig, three **DECREE BANNER-FRAGMENTS** (`▮`), Bell's cage on rear dais, **COURT CLOCK** bar (reused Act One detection-bar widget: idle too long → 2-Pikeman patrol spawns). Rook stuck behind a side portcullis (shouts advice, can toss one item). Weird Shopkeeper has a wing stall.

### THE ASSEMBLED DECREE (read by combining 3 fragments)
> **DECREE OF THE FESTIVAL OF GRATITUDE — BY THE HAND OF SUFFLOK, READ ALOUD BY HIS SERVANT ANKAM.**
> **ARTICLE ONE.** Let every subject prove their love. Each shall place their GRATITUDE upon the King's Scale. The subject's pan must outweigh the Crown's pan, that all may see the subject is GLAD.
> **ARTICLE TWO.** Upon the Crown's pan rests the GIFT OF ORDER, which weighs as much as the King's mercy is great. It may not be touched, questioned, lightened, nor removed, on pain of the King's displeasure.
> **ARTICLE THREE.** The subject shall load their pan with TRIBUTE until the scale tips in their favor, or stand condemned as UNGRATEFUL. Tribute, once placed, may not be retrieved. The contest ends when one pan touches the floor. The losing party bows.
> *— so it is written, so it is performed.*
>
> **(charred 4th line, base of fragment 3, revealed by sling-knocking soot off):**
> **"(In the absence of a named subject, the SERVANT reading the decree stands as subject before the Crown.)"**

### WHY IT'S RIGGED (intended to fail)
The stated method is unwinnable: Article Three says "load TRIBUTE until the scale tips," but the CROWN pan holds the GIFT OF ORDER, heavier than any tribute in the square, and Article Two forbids touching/lightening/removing it. Tribute once placed can't be retrieved (sunk cost). The COURT CLOCK punishes hesitation (spawns Pikemen). Designed outcome: exhaust every crate, never tip, get condemned UNGRATEFUL, forced to BOW, ceremony proceeds to "award" the captive. **The player must BREAK the contest, not survive it.**

### SOLUTION (wording exploits)
The decree never says tribute must be an OBJECT, never says the win must come from ADDING weight, and never names WHO the subject is.
- **EXPLOIT A (→ SURVIVAL):** "The contest ends when one pan touches the floor" doesn't say which pan. Sling-snap the fulcrum **cinch-rope** → the heavy CROWN pan crashes to the floor → Article Three satisfied **without touching the protected Gift** (Article II intact).
- **EXPLOIT C (→ MERCY):** The charred 4th line: the SERVANT who read the decree stands as subject "in the absence of a named subject." Ankam read it and named no one → **Ankam** must out-weigh the Crown, and he cannot. The rigged rule devours its own operator.
- **CRUELTY action:** push a CONFETTI CANNON to face the painted Sufflok-eye + the pinned Ankam and fire — out-perform the crown, turn the crowd's forced gratitude into laughter at the KING, then cheering for the PLAYER.

### PUZZLE STEPS (numbered, build order)
1. **READ FRAGMENT 1** — walk to left-wing banner, press **Z**. Ankam's amplified voice reads Article One; decree UI panel gains line 1.
2. **READ FRAGMENT 2** — cross to the right-wing banner (the SWEEPING SPOTLIGHT passes here; time the crossing or duck a curtain-wing alcove to break the cone — reuses depot stealth). Press **Z** → Article Two added.
3. **READ FRAGMENT 3** — third banner on the rear dais near Bell's cage. Press **Z** → Article Three added. **COURT CLOCK starts ticking;** idling too long spawns a 2-Pikeman patrol (projectile combat / dash-dodge).
4. **(OPTIONAL DOOMED PATH, teaches the rig)** — PICK UP a TRIBUTE TOKEN crate (press Z, carry slowly, movement-slowed), walk it to the SUBJECT'S pan, press Z to drop. Pan barely twitches. Repeat → pan never tips. Rook shouts *"Stop carrying boxes!"* This is the failure to reject.
5. **REVEAL THE FINE PRINT** — aim + **SLING** a pebble at the soot-blackened base of fragment 3 (small targetable prop). Soot clatters off → charred 4th line revealed. Chime + zoom highlight. Set flag `decree_loophole_seen`.
6. **PRESENT THE EXPLOIT** — a CHOICE prompt opens. The branch sets the moral path AND the physical resolving action.
7. **PHYSICAL RESOLUTION by branch:**
   - **MERCY** → walk to Ankam's podium, press Z to read the line back to him as a way out; he cuts his own fulcrum rope and drops the curtain over the eye.
   - **SURVIVAL** → SLING-snap the gold CINCH-ROPE at the fulcrum; the CROWN's loaded pan CLANGS to the floor → contest ends by Article Three; Ankam stamps a forged castle pass.
   - **CRUELTY** → PUSH (single interact) a CONFETTI CANNON to face the painted Sufflok-eye + crowd, press Z to fire, drowning Ankam's script in spectacle that turns the crowd to you.
8. **FREE BELL/YEW** — ceremony broken before "resolving correctly" → cage-lock releases (flag `bell_freed`). Walk to cage, press Z; captive joins to the wing exit. **Transitions into the Court Herald boss arena**, the Herald furious that his weigh-in was "not in the script."

### PUZZLE DIALOGUE
1. **Ankam:** "Welcome, welcome, to the FESTIVAL OF GRATITUDE! Where every loyal heart is... weighed. Publicly. By me. Against my will, but PUBLICLY."
2. **Ankam:** "The rules are FAIR. Look how fair they are. Two pans. One scale. You simply... out-love the Crown. Easy! Everyone manages it! ...No one has ever managed it."
3. **Rook:** "Hey. HEY. That block on the other pan is bolted to the floor. This whole thing's a con. Don't play it straight — read the stupid law. ALL of it."
4. **Bell:** "Don't bother for me, child. They've already written down that I'm a 'gift.' A gift can't say no. That's... that's the clever part."
5. **Ankam:** "Article Two! The Gift of Order may not be touched, questioned, lightened, NOR removed! On pain of— of His displeasure. Please don't make me describe His displeasure."
6. **You:** *(The Crown's pan is heavier than anything here. The rule wants me to lose. So I should stop reading it like a subject — and start reading it like a lawyer.)*
7. **Rook:** "There — the bottom of that last banner, under the soot. Knock it off. Sufflok's people NEVER read the small print. They're too busy performing the big print."
8. **You:** *(I sling a pebble. The soot scatters. A fourth line, charred and hidden:)* "...the SERVANT reading the decree stands as subject before the Crown."
9. **Ankam:** "...What. What did you just— that line is— that's a SCRIBE'S error, that's not— I read it. I read the decree. Oh. Oh no. I named no one. I read it. That makes ME the—"
10. **You:** "The subject. Article One. You have to out-weigh the Crown now, Ankam. Go on. Prove your love. Publicly. By you. Against your will."

### CHOICE — "The rigged rule has turned on its operator. How do you break the scale?"
| label | tag | effect |
|---|---|---|
| *"This was never about gratitude. It's a trap with your name in the fine print — and now it's the King's trap, around you. I won't spring it. Drop the curtain. End the show yourself."* | **mercy** | `expose_decree` |
| *"Keep your guilt. The rope at the fulcrum is the only thing this contest forgot to protect. One pan on the floor and it's over — and it's faster than arguing with you."* | **survival** | `disable_rigging` |
| *"No. Let them WATCH it eat you. Crank the cannon at the King's painted face — give the crowd a better show than the one He wrote. Let them cheer for the scale breaking, not for you."* | **cruelty** | `upstage_crown` |

**MERCY result (`expose_decree`; +MERCY, flags `ankam_turned`, `decree_exposed`):**
- **Ankam:** "You... you could have let it crush me. The eye is RIGHT THERE. It would have loved watching me weighed and found wanting."
- **Ankam:** "He scripts every word, you know. Every 'spontaneous' cheer. I memorize gratitude I don't feel and I have done it so long I forgot it was a script. ...You let me see it was a script."
- **Ankam:** "The cinch-rope. The contest ends 'when one pan touches the floor' — it never said WHICH. Here. Let an old coward cut his own stage down for once."
- **Ankam:** *(He saws the fulcrum rope. The Crown's pan CLANGS to the floor. The painted Sufflok-eye goes dark as Ankam yanks the master curtain across it.)* "Contest concluded. The Crown's pan is on the floor. By Article Three, the Crown... bows. Let the record show it."
- **Rook:** "Did the scary hat-man just... help us? Out of GUILT? I'm putting that in the song."
> **PAYOFF:** Ankam becomes an intermittent **INFORMANT** for the rest of the act → opens *Ankam-informant gaps* in the upcoming Herald fight + a village-trust nudge. **Stronger if Act One flag `ankam_mercy`** (he recognizes "the one who asked why I was afraid" and breaks faster).

**SURVIVAL result (`disable_rigging`; +SURVIVAL, flags `castle_pass`, `rigging_disabled`):**
- **You:** *(I sling the gold cinch-rope at the fulcrum. The beam jolts. The Crown's loaded pan — too heavy to ever lose — slams to the floor under its own weight.)*
- **Ankam:** "You— you can't— the contest ends when one pan touches the— ...the floor. It touched the floor. Its OWN pan. By its OWN rule. The contest is concluded and I am NOT permitted to say who won, oh, this is bad, this is so procedurally bad—"
- **You:** "Mark me 'cleared,' Ankam. On the record. The law's satisfied. You're the one who has to live with the eye, not me."
- **Ankam:** *(Shaking, he stamps a parchment and shoves it at you: a forged CASTLE PASS.)* "Cleared. CLEARED. Take it and GO before someone makes me explain physics to Sufflok."
- **Rook:** "Efficient. Cold, but efficient. The old man's gonna have nightmares about ropes now."
> **PAYOFF:** key item **forged CASTLE PASS** (opens the Prison Zone gate later without a fight). No Ankam ally. **Faster stamp if Act One `ankam_survival`** ("you out-maneuver everything, don't you").

**CRUELTY result (`upstage_crown`; +CRUELTY, flags `crowd_weaponized`, `castle_heat_up`):**
- **You:** *(I shove the confetti cannon around until it aims at the leering painted Sufflok-eye, and at Ankam pinned under his own fine print. I fire.)*
- **Ankam:** "NOT THE FACE— not the— they're LAUGHING. They're laughing at the EYE. They've never— you can't make them laugh at HIM, do you know what He DOES to things that get laughed at—"
- **Bell:** *(quietly)* "...They're cheering for you, child. Not for the King. For you. I have lived here sixty years and I have never heard that sound. It frightens me more than the cage did."
- **You:** "The contest's over, Ankam. The crowd decided. They always do — Sufflok just never let them. Now they know they can."
- **Ankam:** *(He bows. To you. Reflexively. In front of the eye. And his face when he realizes is the most afraid I have ever seen a man.)* "...Take the prisoner. Take anything. Just— just don't smile at me like that. That's HIS smile."
- **Rook:** "Okay. That was incredible and I want to never see you do it again. The whole court's looking at you the way they look at HIM. ...Is that what we want? Is it?"
> **COST (legible, immediate):** raises `castle_heat` → **more Pikemen + harder Herald fight**; no Ankam ally; no clean pass; **Sufflok takes personal notice of a rival.** **If Act One `ankam_cruel`,** the bow is instant and pathetic (deepens the "the other one like him" thread).

### POST-RESOLUTION (all branches)
- **Bell:** *(as the cage opens)* "You broke a rule that was built so no one could break it. That's... that's a thing people here had stopped believing was possible. Word of that travels faster than guards do."
- **Court Herald:** *(amplified, from the boss arena beyond)* "UN-SCHEDULED! This is UN-SCHEDULED! The weigh-in does NOT end this way, it is not in my SCRIPT — places, PLACES, we go again from the top and this time the outsider LOSES—!"

> **EXIT:** Third bell. Player swept onto the **Grand Dais / festival stage** → Boss (Scene 6 stage / Scene 6 boss).

---

# SCENE 5 — MR. ANKAM RETURNS (BRANCH INSERT)
**id:** `ankamReturn` · plays during the festival-stage approach (Scene 6), after the Herald is broken / during the rescue window. Branches on Act One disposition. **Insert the matching variant where the boss block calls `ankamReturn`.**

> **WHICH VARIANT FIRES:**
> - `ankam_mercy` (Act One: spared-with-pity) → **tippedOff**
> - `ankam_survival` (Act One: out-maneuvered) → **obstructive**
> - `ankam_cruel` (Act One: terrified-of-player) → **terrified**

### VARIANT A — `tippedOff` (Act One = ankam_mercy)
1. **Mr. Ankam:** *(stepping from the wings, smoothing a coat that does not need smoothing, voice pitched low so no warden hears)* "You. The sky one. The one I — that didn't happen, the village, we AGREED it didn't happen. And now you're up here making the Court LAUGH on the night Sufflok comes for his gift. Do you have ANY idea what that does to my paperwork?"
2. **Mr. Ankam:** "Listen. LISTEN. I out-maneuvered, I — no, YOU out-maneuvered me, fine, I conceded that, I'm a CONCEDER, it's a survival trait. And I've been... thinking, since the village. About ledgers. About marks by names. About how the Herald is about to be a very large mark by a very large name, and how I do NOT want to be standing next to that man when Sufflok arrives."
3. **Mr. Ankam:** "So here is a thing that also won't have happened: the under-stage tunnel's service gate. The booth's unmanned. I reassigned the boothkeeper an hour ago to — and I want you to appreciate this — 'urgent confetti logistics.' There is no such thing. That was the point. If your rebel's cart happens to roll through an unlocked gate, that is a COINCIDENCE and I will deny it under any quantity of oath." `[VOICE-FIX #4]`
4. **Mr. Ankam:** "...You made me think, last time. With the ledger thing. It was very rude. I haven't stopped. Now GO, before I remember I'm an instrument of state terror and start behaving like one. ...And — for what it's not worth, since none of this happened — good. With the laughing. Someone should laugh at us. It's been a very long time since anyone could."
> **EFFECT:** Ankam unlocks the under-stage service gate → smoother rescue window; informant flavor in the boss fight.

### VARIANT B — `obstructive` (Act One = ankam_survival)
1. **Mr. Ankam:** *(striding out, hat first, the way a man leads with the only part of himself he trusts)* "STOP. Stop right there, sky-thing. Oh, I KNOW you. The village. You stood in front of me with your CLEVER mouth and your impossible paperwork and you made me look — you made the THEFT my fault, you wordsmithing little — and now you're HERE. Of course you're here. You ruin scheduled events. It's apparently your entire personality."
2. **Mr. Ankam:** "Well, NOT this one. This one is MINE to deliver clean to Sufflok, and I have been very good, and very early, and very BLAMELESS for an entire week, and I am not — NOT — letting an off-list sky-creature un-blameless me twice. Wardens! No — I'll do it MYSELF, that's how serious — I have a WHISTLE, I'll use the WHISTLE—"
3. **Mr. Ankam:** *(but his hand shakes on the whistle, and his eyes keep darting to the high tower)* "...He's coming. He's actually coming tonight. And if I blow this whistle and there's a SCENE, then the scene is on my watch, and a scene on my watch is — is a mark — oh, you've done it AGAIN, you've made even stopping you DANGEROUS, how do you DO that—"
4. **Mr. Ankam:** "I am going to stand RIGHT HERE and watch you, and disapprove ENORMOUSLY, and not actually intervene, because intervening is how I end up in the ledger. Consider yourself OBSTRUCTED. Spiritually. Loudly. From a safe distance. ...Get your villager and get OUT before he arrives and turns this into the kind of evening nobody walks away from, you absolute — paperwork-shaped — CATASTROPHE."
> **EFFECT:** No help, no real hindrance — comic stalemate; rescue window proceeds on its own timing.

### VARIANT C — `terrified` (Act One = ankam_cruel)
1. **Mr. Ankam:** *(he does not stride. He edges out, half-behind a confetti cannon, and the moment he sees your face the colour leaves his)* "...It's you. It's YOU. The hat doesn't — the hat means NOTHING to you, does it. I've worn this hat for nine years and it has never once meant nothing until you. Oh, I had hoped you'd died in the sky. I hoped it quite hard."
2. **Mr. Ankam:** "I'm not going to— I won't blow a single whistle, I won't raise a single hand, I will not so much as INHALE in a threatening manner, do you understand, I have learned, I have LEARNED, the lesson took beautifully, ask anyone, I flinch at the actual sky now. The sky. As a concept." `[VOICE-FIX #5]`
3. **Mr. Ankam:** "The girl. The guest. You want the guest. Take the guest. Take the cage, take the ribbons, take the whole stage, I'll have the boothkeeper UNLOCK things, I'll unlock things I don't even know the locks to, just — please don't do the thing. The looking. The looking you did in the village. Sufflok looks at me like I'm a mistake he's deciding when to correct, and you look at me like — like the same — and I cannot do BOTH of you, I am ONE assistant—"
4. **Mr. Ankam:** *(and as you turn to go, something small and bitter and almost brave flickers in him)* "...You know the worst of it? I taught a recruit to be scared this morning. Same way he teaches me. Same way you taught ME. It goes DOWNHILL, the fear, it always rolls downhill onto someone smaller, and I am SO tired of being a hill. ...Go. Take her. And know that the one thing I'm afraid of more than Sufflok now is YOU, and I don't think you should be proud of that. I don't think either of us should."
> **EFFECT:** Ankam capitulates fully (unlocks everything) but the beat lands as cost, not victory. **Do not cut lines 2–4 — emotional peak of his arc;** thematically rhymes with the Scene-2 `scare_recruit` beat.

---

# SCENE 6 — THE COURT HERALD & THE FESTIVAL OF GRATITUDE (BOSS + CLIMAX)
**id:** `festival_stage` · **Title:** *The Court Herald & the Festival of Gratitude*

**Purpose:** Act Two boss + climax. The Court Herald CONDUCTS escalating waves; the player **out-thinks**, never out-DPSes. Three honest resolutions, each rescuing the captive at different cost. Ends pointing toward the Prison Zones; Sufflok now personally notices the player.

**Present:** Player, Court Herald (boss, on podium), Court Pikemen / Confetti Troopers / Gilded Ushers (conducted waves), Spotlight Rigs (hazards), the crowd (live reaction meter), Yew/Bell (cage, rescue objective), Rook (under-stage tunnel), Mr. Ankam (wings — fires `ankamReturn`), Herald's Apprentice (MERCY-only ally).

---

## 6A — COMBAT BESTIARY (reused across all Act Two arenas)
> All projectiles **straight-line, honestly telegraphed, dash-through-able**. No DPS races — Herald is `hp:0` (won via meter); pikemen/troopers are `hp:1` (one Sling = KO). All KOs **non-lethal**.

### `court_pikeman` — charger (hp 1, speed 1.7)
- **Behavior:** bored conscript; holds a loose patrol line, then telegraphs a single straight **LUNGE** at the player's last position: winds up in place, dashes ~4 tiles in a fixed line, over-shoots, leaving a ~0.9s **recovery** window (stunnable). Never tracks mid-lunge → a sideways dash always clears him. Two pikemen never lunge on the same frame (the conductor staggers them). Touch contact = 1 heart + knockback; the lunge adds no extra damage beyond contact, so dodging the line is enough.
- **Telegraph:** boots scrape; a white chevron arrow paints the full lunge lane on the floor for 0.55s; pike-tip flashes gold before commit. Lane is honest — travels exactly its length, no curve.
- **Projectile:** `melee_lunge_line` · speed 4.6 · count 1 · cooldown 2.6
- **KO reward:** Sling to back/side during recovery = instant KO (flops, armor clatters, stays down for the wave). **Restraint payoff:** clean KO with no extra hits → 1–2 chits + sometimes a pebble; mutters thanks if spared rather than swarmed.

### `confetti_trooper` — shooter (hp 1, speed 1)
- **Behavior:** cranks a confetti cannon at range; strafes slowly to keep distance; fires a 3-pellet **fan**; gaps wider than the player hitbox at mid-range → weave the gap or dash the volley on i-frames. Reloads visibly (cannot fire) ~1.1s after each volley = KO window. Aims at where you ARE (no lead) → strafing sideways already shifts the fan.
- **Telegraph:** barrel glows warm; 3 thin aim-lines fan from the muzzle for 0.5s; rising "fwip" pitch. Reload = barrel vents smoke, goes dark (clearly safe to approach).
- **Projectile:** `fan_spread_3` · speed 3.6 · count 3 · cooldown 2.2
- **KO reward:** Sling during reload vent = KO (cannon backfires harmlessly, he sits down covered in his own confetti). **Restraint payoff:** KO without taking a hit → chits + a confetti pickup that briefly slows nearby troopers' aim.

### `spotlight_turret` — turret/hazard (hp 0 — **not killable**, speed 0)
- **Behavior:** wall/rafter-mounted stage spotlight; sweeps a circular kill-light disc across the floor on a fixed, readable loop. Standing in the bright disc >0.4s = 1 heart ("caught in the act" burn), no knockback → walk/dash out. Constant looping path — a moving hazard to TIME, never a tracker. Dashing across the beam edge is safe (i-frames cover the crossing).
- **Telegraph:** a dim ring pre-traces the spot's next position 0.6s ahead; the beam itself is a hard-edged bright disc; a low hum tracks sweep direction.
- **Projectile:** `sweeping_beam_disc` · speed 1.3 · count 1
- **KO reward:** not KO-able. **SURVIVAL:** sling/interact the rigging panel or yank the lever to kill the beam for the rest of the fight.
> **[FEAS #1]** Implement as a moving **circle** (center on a parametric path, radius R). Damage = timer while player-center inside radius >0.4s. "Blackening wood" is a **VFX decal under the disc** — **no tile-state simulation.**

### `usher_support` — support (hp 1, speed 2)
- **Behavior:** nervous, weaponless stagehand; scuttles to a downed Pikeman or broken rigging point and tries to **REVIVE/reset** over ~2.5s (visible progress bar). If it finishes, one KO'd enemy stands back up or a disabled spotlight re-lights. Flees the instant the player dashes at it or slings it. Soft time pressure; rewards aggression-with-restraint.
- **Telegraph:** glances over its shoulder; a revive-meter fills above its target; it **freezes** while reviving (vulnerable). **No projectile** — its "attack" is purely the interruptible meter.
- **Projectile:** `none`
- **KO reward:** one Sling KO or a dash-bump drops it (non-lethal: trips over its own coattails, surrenders). **Restraint payoff:** KO before it revives anyone → freezes the wave's progress; the crowd "oohs."
> **[FEAS #2]** No A*: spawn from a wing, **move straight-line to the target's position, ignore cover collision**, freeze to channel 2.5s, flee on dash-approach/sling. Never give ushers aim/projectiles.

### `court_herald` — conductor (hp 0 — **not damageable**, speed 0.7) — BOSS
- **Behavior:** pompous amplified announcer on a raised podium; **NEVER attacks directly**; slinging him only knocks his hat askew + makes the crowd laugh (a meter, not damage). He **CONDUCTS**: between speech lines he points his baton to trigger Pikemen/Trooper waves, fire confetti spreads, aim spotlight sweeps. **Out-THOUGHT, not out-DPS'd.** Three escalating phases. He reads from a SCRIPT in his free hand and cannot stop reading it.
- **Telegraph:** always honest + theatrical — ANNOUNCES each hazard one beat before it happens ("PIKEMEN — to your MARKS!", "and now... a SHOWER of GRATITUDE!"); baton raised = spread incoming; baton swept low = spotlight turn. Amplifier makes every cue audible; an overhead banner flashes the cue word. **Phase 3:** announcements stutter and arrive a half-beat EARLY → paradoxically *easier* to read (deliberate tell that he's losing control).
- **Win condition = a CONDUCT meter** filled via the chosen resolution. Player damage is irrelevant.

> **[FEAS #4] CANONICAL VULN TARGETS — collapse to 3.** The richer `boss.phases` prop list (horn, rig-rope, pulley, feed-belt) are **flavor names for these same three mechanical targets.** Build:
> - **MERCY** → the **script-stand** (one interact/sling target, same prop all 3 phases; 3 successful "page knocks" fill the meter).
> - **SURVIVAL** → **3 wing panels** (NE / NW / center feed) — reuse the *same* panel sprite/interaction ×3.
> - **CRUELTY** → **no prop**; meter filled by KO-pace + standing in the follow-spot disc (a position check you already have from spotlight code).
> **[FEAS #5] / AMMO FIX:** make the **SURVIVAL panels** and the **CRUELTY pose** *interact / hold-button, NOT Sling* (mirrors the puzzle's press-Z solves). This removes any chance of softlocking your own resolution by being out of pebbles. Keep Sling scarcity meaningful for *enemies only*.
> **AMMO REFILL:** refill pebbles to full on entry to `grand_finale_court` (and at each boss phase start), so enemy-KO play never starves a resolution.

---

## 6B — BOSS ARENA: THE GRAND DAIS / GRAND FINALE COURT (32×20)
```
################################################
# P (outer processional — CROWD implied in dark) #
#  ┌NW panel┐                      ┌NE panel┐   #  ← SURVIVAL interact targets (wing alcoves)
#  S          C cover      C cover          S    #  S = spotlight rig
#       ╔══════════════════════════════╗         #
#  C    ║   f  f  f  INNER FLOOR f  f   ║    C    #  f = open kill/conduct floor
#       ║  f   [H Herald podium]   f    ║         #  H = podium: script-stand + rig lever + stage-front
#  S    ║   f  f  f  f  f  f  f  f  f   ║    S    #
#       ╚══════════════════════════════╝         #
#  C cover        [center feed panel]      C cover#  ← 3rd SURVIVAL target
#        ===========  g  ===========             #  = velvet rope, g = entry gap (south apron)
#                  [ K award-cage ]              #  K = captive (rescue objective, front-center)
#   @  (entry from south apron)   ↓under-stage tunnel→ Rook #
################################################
```
**Layout:** central `C`-ringed podium holds the Herald (un-damageable) with **script-stand + rigging lever + stage-front** clustered there (the three resolution levers). Concentric rings: inner open `f` floor (conduct/kill zone) → mid ring of four `C` cover wedges at the diagonals → outer `P` walkway (crowd implied). Two wing alcoves (NE/NW) hold confetti feeds + rigging panels (SURVIVAL). Captive cage front-and-center `K` on the stage lip (rescue objective, always lit by a pity-white follow-spot). Entry from the south apron. **Ambient:** falling gold glitter (recolored mote field), hot footlight glare, low velvet hum, `FESTIVAL OF GRATITUDE` scrim banner overhead flaking gold leaf.

**Cover/fairness notes:** cover wedges block confetti spreads + allow repositioning between announced cues; the open inner `f` floor is where conduct/poses/spotlights happen (high-risk). Herald announces every hazard a beat early → out-think the rhythm, don't out-shoot it. Ammo scarce by design — you cannot brute-force Phase 3, which pushes each resolution. **All telegraphs honest; all patterns dash-dodgeable.**

---

## 6C — STAGE-ENTRY DIALOGUE (third bell → Herald takes the stage)
1. **???:** *(The third bell drops like a dropped anvil. Every torch flares gold. A man explodes onto the stage — enormous coat, enormouser voice, a brass cone strapped to his throat that makes every word a weather event.)*
2. **Court Herald:** "GRATITUDE! GRATITUDE, my radiant, my RAVENOUS, my RELENTLESSLY thankful people! WELCOME to the Festival of Gratitude, where we GIVE — and GIVE — and are GRATEFUL to have been ALLOWED to give! I am your HERALD, and tonight, on this very stage, we present our humble GIFT to the magnificent Lord Sufflok!"
3. **Court Herald:** "And what's THIS? A WINNER? On MY stage? How — how FESTIVE. How completely accounted-for and not at all a problem. Wardens — PIKEMEN — let us WELCOME our winner the way the Court welcomes ALL who win. With a CELEBRATION they will never. forget. PIKEMEN — a volley of JOY!"
4. **???:** *(Court Pikemen line the stage edge. Each shoulders a launcher; each barrel blooms a clear warning glow before it fires. The Herald doesn't lift a weapon. He lifts his HANDS, like a conductor, and the stage obeys.)*
5. **Court Herald:** "Observe! I do not FIGHT — fighting is for the GRACELESS. I CONDUCT. The stage is my orchestra and you, little winner, are the percussion! Dance! DANCE for the magnificent Lord Sufflok! It's in the SCRIPT that you dance, so DANCE!"
6. **Rook:** *(in your ear, from the tunnel grate)* "He reads from the script in his free hand the whole time — watch it. He can call a hundred pikemen and still can't put the book down. That's the seam. Drop the pikemen, make him call more, watch the hand." `[VOICE-FIX #2]`

> **OPTIONAL alt intro (`boss.introDialogue`, if staging the cage-banter version):**
> - **Court Herald:** "AND NOW — direct from the gutters of the outer dark, by no invitation whatsoever — the STRAY!"
> - **Court Herald:** "Applause, applause, you're too kind, you're not kind at all, it doesn't matter, the SIGN says applause."
> - **Rook:** "He's wired the whole stage. Spotlights, cannons, the works. He doesn't fight — he RUNS the fight."
> - **Rook:** "Don't go for him. Go for the rig. And — hey. The villager. In the cage. We are NOT leaving without them."
> - **Court Herald:** "The CAGE? Oh, the prize, yes — to be GIFTED to Lord Sufflok himself, live, tonight, between Act Two and the fireworks."
> - **Court Herald:** "It's all on the program. The program is PERFECT. I wrote it myself. Mostly. The important bits."
> - **You:** *(He keeps touching that script like it might run away.)*
> - **Court Herald:** "Pikemen! PLACES! Let's give them a show they'll be too frightened to forget!"

### HERALD TAUNTS (random barks during waves)
- "Eyes UP, little stray! The cheap seats can't see you cower!"
- "A WAVE of my finest! Try not to bleed on the good floorboards."
- "You DODGE? In MY theater? How dreadfully... athletic."
- "He's only sleeping! We don't do MESSY on the good floorboards, darling — blood is so hard to gild over." `[VOICE-FIX #10]`
- "SPOTLIGHT! Let them see exactly how small you are."
- "You cannot hide in the dark forever — the dark isn't on the PROGRAM."
- "Smile! You're on the festival's main stage! Everyone is so... GRATEFUL."
- "CONFETTI! Because nothing says mercy like a parade, hm?"
- "Why won't you just LOSE on cue? It's all written down, see, it's RIGHT HERE—"
- "Stop improvising! Improvising is for AMATEURS and— and— where's my next line—"
- "The crowd loves me. The crowd LOVES me. They— they're meant to be clapping by now."

---

## 6D — BOSS PHASES (spawn / telegraph / counter)

### PHASE 1 — "PLACES, EVERYONE!" (Conducting the Pikeman Waves) — hp 100%
**Spawn / attacks:**
- **CONDUCTED PIKEMAN WAVES:** Herald raises baton, "introduces" 2–3 Court Pikemen marching on from the wings; they open telegraphed straight-line volleys down the pillar lanes.
- **BATON CUES:** on a clear downbeat (baton snaps + brass "sting"), every standing Pikeman fires at once down their lane — a readable synchronized volley you dash THROUGH.
- **CURTAIN-CALL ENTRANCE:** between waves a single Pikeman is "announced" from a wing with a spotlight flourish; one free aimed shot before the volley resumes (punishes center-camping).
- **+ one slow single SPOTLIGHT** sweep introduced.
- **Herald is behind the velvet rope; takes no damage.** Phase progresses by clearing waves + reading that he is the conductor, not a target (first out-think beat). **This phase teaches the announce-then-act rhythm and lets the player locate the 3 resolution levers** (script-stand / rigging lever / stage-front).

**Telegraph:** baton RAISES + glows warn-gold ~0.6s before any wave fires (honest downbeat); each Pikeman muzzle pre-glows; bolt lane shows a thin filling line on the pillar grid; curtain-call = spotlight snap + brass sting one beat before the free shot. Brass "sting" audio always = a committed volley.

**Player counter:** use cover wedges (`C`) to break each lane's sightline; **dash on the downbeat** through the synchronized volley (i-frames); weave to a flank and Sling-KO Pikemen between volleys; Whipcord charge one-shots a Pikeman's stagger. The real counter: recognize the Herald is untouchable here; clearing his cast advances the fight.

**Resolution meters open:** poke the **script-stand** → begins MERCY. Sling/interact a **wing panel** → begins SURVIVAL. Fast clean KOs → begins CRUELTY. The crowd reacts to *how* you play (restraint legible).

**Wave spec:** `[court_herald, court_pikeman, court_pikeman, spotlight_turret]` (low density).

---

### PHASE 2 — "THE FOLLOWING SPOT!" / "A SHOWER OF GRATITUDE" (Sweeping Spotlights + Confetti) — hp 66%
**Spawn / attacks:**
- **SWEEPING SPOTLIGHT CONES/DISCS:** the rigs drop hot kill-zones that sweep on fixed arcs; standing fully lit fills a SPOTLIGHT bar → on fill, iris-in chunk damage + knockback. Dodge by timing gaps + ducking the **curtain wings** (full-dark cover breaks the cone — depot stealth logic).
- **FOLLOW-SPOT:** one rig tracks the player with ~0.4s lag — can't be out-run straight, beaten by hard cuts behind pillars / into wings.
- **PINCH SWEEPS:** two cones sweep toward each other to close center, forcing you to a wing/pillar exactly as a thinned Pikeman remnant fires.
- **CONFETTI SPREADS from BOTH wings** now fire in time with his lines; baton tempo speeds up.
- **GILDED USHER** tries to revive downed enemies / re-light panels (soft time pressure; rewards interrupting it).
- **VULN / OPENING:** when two cones cross, the rigs over-tax and the Herald's amplifying HORN sparks/over-heats — a brief window. (Canonically: this is when SURVIVAL's wing-panel interact or MERCY's page-knock lands a phase beat; CRUELTY banks a follow-spot pose.)

**Telegraph:** each rig FLICKS on with a click + a bright pre-glow ring showing the cone's start before it sweeps; swept floor brightens a beat ahead of the lethal cone; SPOTLIGHT bar fills only while fully lit; follow-spot tell = a small warn reticle on the floor that lags you; cross-over VULN = horn shoots GOLD sparks + a feedback "whine" (honest "hit me NOW").

**Player counter:** read the floor pre-glow + walk the gaps; never stand still in light; duck the follow-spot behind a pillar or into a wing (the dark eats the cone); don't tank the iris-in — dash clear before the bar fills. When the horn sparks GOLD, that's the opening for your chosen resolution beat. **Out-think:** his own stagecraft (the light) overloads his rig.

**Active contest of paths:** the usher will **undo SURVIVAL panel-kills if ignored**; CRUELTY must **out-pace the revives**; MERCY banks its second leaked page.

**Wave spec:** `[court_herald, court_pikeman, confetti_trooper, confetti_trooper, spotlight_turret, spotlight_turret, usher_support]`.

---

### PHASE 3 — "THE GRAND FINALE!" (Confetti-Cannon Bullet Spreads; script glitches) — hp 33%
**Spawn / attacks:**
- **CONFETTI-CANNON SPREADS:** both proscenium cannons fire wide festive bullet-spreads (radial fans + sweeping arcs of slow-to-medium projectiles); gaps always present and reachable with one dash.
- **ALTERNATING SALVOS:** left then right fan-burst, then a combined **CRESCENDO double-fan** leaving exactly one survivable lane (the lane glows safe). Mid-crescendo, a last **2-Pikeman "encore"** pressures the lane.
- **STREAMER STREAKS:** between fans, ribbon-streamers whip in straight lines cannon-to-cannon across the front — a low fence you dash over on i-frames (stops footlight-camping).
- **TWO SPOTLIGHTS sweep opposite directions; TWO USHERS** scramble to revive.
- **THE SCRIPT FALTERS:** spreads get FASTER but SLOPPIER — fans mis-fire / double-fire and leave bigger gaps (visual language of a man losing the plot). Cannons over-pressurize; the feed-belt / script-stand becomes the final VULN target.

**Telegraph:** each cannon barrel glows warn + "huffs" (glitter puff + party-popper pop) ~0.5s before its fan; the fan's spread arc is pre-drawn as faint warn dotted lines (pre-spot the gap); CRESCENDO dims the stage except the one EERIE-safe lane; streamer streaks flash a thin line before whipping; over-pressurized cannons / script-stand spark GOLD when hittable; "encore" Pikemen get the Phase-1 spotlight-snap + brass sting. **Cues arrive a half-beat EARLY → easier to read (the honest tell that he's losing control).**

**Player counter:** pre-spot the gap from the dotted arc and dash to it before the fan lands (each fan = a single-dash puzzle, not a wall); on CRESCENDO run to the EERIE-safe lane and ignore everything else; dash the streamer-fence on i-frames; when the cannon feed / script-stand sparks GOLD, that's your KO/resolution shot (Whipcord for reliability where applicable). **Out-think, don't out-DPS** — you win by reading the faltering script + landing the single decisive resolution beat.

**Wave spec:** `[court_herald, court_pikeman, court_pikeman, confetti_trooper, confetti_trooper, spotlight_turret, spotlight_turret, usher_support, usher_support]`.

> **FAIRNESS GUARANTEE (build requirement):** Phase-3 resolution meters **must be able to close MID-phase** (reaching ~66–100% of the chosen meter ends the fight immediately). **No resolution may require surviving a full Phase-3 loop first.** This is what keeps the 5-heart ceiling fair.

---

## 6E — THE RESOLUTION FORK (3 honest endings; each frees the captive, at different cost)

> **CHOICE PROMPT (fires when the Herald's rhythm cracks in Phase 3):** *"The Herald is unravelling and the rescue window is open. How do you break him?"*

| label | tag | effect |
|---|---|---|
| Snatch the script and read his next lines aloud — to the whole crowd. | **mercy** | `expose_script` |
| Ignore him entirely — dash to the rigging junction and cut the whole stage dead. | **survival** | `disable_rigging` |
| Take his stage. Out-perform him until the crowd turns on HIM. | **cruelty** | `outperform_herald` |

> **CONSISTENCY FIX `[VOICE-FIX #9]`:** the leaked-line button is unified to the panic-note **"DO NOT CRY"** across both this scene and the boss resolution block (it's the line that humanizes him).

### MERCY — `expose_script` (EXPOSE HIS SCRIPT LIVE)
**How (mechanical):** throughout the fight, knock pages loose at the **script-stand** (interact, restraint-rewarded). Expose 3 leaked lines (canned "spontaneous" crowd reactions, the pre-written "heroic" Sufflok intro, his panic-note). On the Phase-3 VULN window, instead of striking the rig, **sling/raise his own script into the follow-spot** for the whole crowd to read. The crowd realizes the gratitude was scripted → they LAUGH. His amplified voice cracks; he flees. The spotlight swings to the cage; free the captive in the confusion. **No one is hurt.**

**Result dialogue:**
- **You:** "You want the next page? Let me help. *(You catch the script as a spotlight forces his hand wide, and you read it to the crowd, loud and flat.)* 'Here the Herald shall pause for ADORING APPLAUSE. If applause is insufficient, the Herald shall ORDER it. See appendix: APPROVED LAUGHTER, three types.'"
- **???:** *(A beat. Then the crowd LAUGHS — a real, ragged, astonished laugh, the first un-ordered sound this kingdom has made in months. They're laughing at the man behind the curtain because you showed them there was a curtain.)*
- **Court Herald:** "No — NO — don't read the APPENDIX, that's — those are PRIVATE stage directions, you can't just — they're LAUGHING, they're not supposed to — a Herald without a script is just a — is just a loud — I have to — I'M LEAVING, this is a SCHEDULED intermission, I MEANT to do this—"
- **Court Herald:** *(very small, off-mic)* "...I just wanted a good show. I just wanted them to—" *(he runs, clutching his ruined pages, chased by laughter, not fear.)*

> **[VOICE-FIX checklist / boss leaked-line variant]** Optionally surface the unified panic-note button:
> - **Court Herald:** "'...if stray wins... improvise... smile... do NOT cry...' ...who's reading that. WHO is reading that aloud."

- **???:** *(He flees into the wings. The spotlights die. In the noise, the captive slips her ribbons and walks — walks, head up — down the under-stage stairs into Rook's tunnel. You didn't beat the Herald. You let the crowd stop being afraid of him. Mercy is active: you handed a thousand scared people a laugh, and a laugh is a crack in a wall.)*

> **ALLY PAYOFF (make it ON-SCREEN — design-contract gap fix):** the lightboard **Apprentice** defects, moved by you sparing his terrified boss, and slips you the cage key. **Stage this in the result so the reward is visible at the moment of choice, like the puzzle's `expose_decree` does with Ankam.**
> - **Herald's Apprentice:** "Hey. Stray. You didn't hurt him. You could've, and you didn't. ...Here. The cage key. I never saw you. Go."
> - **You:** *(The villager blinks at the light, free. The crowd is still laughing — at the show, not at you.)*
> - **PAYOFF:** Apprentice becomes a future ally → **reappears in the Prison Zone.** Set flag `apprentice_defected`.

- **Rook:** *(half-laughing, half-stunned)* "She's IN, she's in the cart, she's GOOD — and you just made an entire kingdom laugh at the Court out loud. They'll be telling that one in whispers for a year. Move, move, before they remember they're allowed to be scared again!"

---

### SURVIVAL — `disable_rigging` (DISABLE THE STAGE RIGGING)
**How (mechanical):** treat the theater as the boss; **interact** the infrastructure during each phase's VULN window — Phase 1: the **wing pulley** (wave supply dries up); Phase 2: the **spotlight rig-rope** (dead rigs drop); Phase 3: the **confetti-cannon feed-belt** (both cannons jam). With the rigging dead, the Herald has nothing to conduct. He surrenders to keep his own skin. Cut the cage open with the slack rigging-rope; leave fast + clean. *No crowd-turn, no humiliation, no killing — most efficient exit; keeps the shopkeeper's best prices + cleanest castle reputation.* **Cost: the apprentice doesn't defect (you never engaged the Herald as a person) — that ally is missed.**

**Result dialogue:**
- **You:** "You're not the threat. The STAGE is the threat. *(You stop fighting the show and run the show's spine instead — dashing the spotlight gaps to the rigging junction under the throne-prop, and you haul the master lever.)* Lights. Cannons. Pikemen's cues. All of it runs through here. So all of it stops. Here."
- **???:** *(Every spotlight gutters out at once. The confetti cannons choke. The pikemen, suddenly un-conducted, stand blinking in the dark with no cue to follow. The Herald keeps gesturing at an orchestra that has simply stopped existing.)*
- **Court Herald:** "Lights? LIGHTS! Where are my — the cues, give me the CUES — pikemen, why aren't you — someone CONDUCT something, I cannot conduct silence, silence isn't in the — oh, this is a disaster, this is an unscheduled DARKNESS—"
- **???:** *(In the dark, nobody's watching the cage. You didn't beat him; you unplugged him. The captive's ribbons slither off and she's down the stairs and gone before the Herald finds a working torch. Survival is messy and quiet and it WORKS: no crowd revelation, no fear, no laughter — just a girl, free, and a confused man yelling at a dead stage. Some nights, that's the whole victory.)*
- **Rook:** *(from the dark tunnel)* "Got her, got her, lights-out was PERFECT, nobody saw a thing — which means nobody saw YOU either, which is the smartest kind of rescue there is. Out. Now. Before the Herald finds the spare torches."

---

### CRUELTY — `outperform_herald` (OUT-PERFORM HIM — TURN THE CROWD ON HIM)
**How (mechanical):** UPSTAGE — every dodge a flourish, every Pikeman KO a "finishing move" played to the dark house. Each phase, hit the VULN window not to disable but to **STEAL the spotlight** (stand in his follow-spot, hold the pose) → feeds a CROWD meter your way. Fill it and the crowd's fear re-aims onto the Herald — booing → surging the footlights; Pikemen drag him off. Take the cage by force; walk through a court that now FLEES on sight; **unlock 'intimidate'** (weak shooters surrender). **Fastest route — and the cost is explicit + immediate.** Rook goes quiet; the captive flinches from you; the crowd that cheers you is the same crowd that would have cheered the gifting to Sufflok, and it will cheer the next thing too.

**Result dialogue:**
- **You:** "You want a show? *(You step into his light, into the smoke and the brass spread, and you don't dodge — you DEFY it, and you turn to the crowd.)* Look at him. Your Herald. He needed pikemen, lights, cannons, a SCRIPT, and an entire castle — to lose to one scared stranger who fell out of the sky. THIS is what's been deciding your gratitude?"
- **???:** *(The crowd's fear pivots like a weathervane in a gale — off the Herald, onto YOU. And then, because fear always needs a smaller target, back onto him. They start to JEER. Not laughing. Jeering. The sound has a mob's edge to it. You did that. You aimed a thousand people's terror like a weapon.)*
- **Court Herald:** "Stop — stop LOOKING at me like that, all of you, I am your HERALD, I — you can't — they're TURNING, why are they — I gave you a FESTIVAL, I gave you GRATITUDE, you ungrateful — somebody, anybody, GUARDS, get them OFF me—"
- **???:** *(He doesn't flee laughing. He flees HUNTED, the crowd surging after the man they were terrified of an hour ago. The captive uses the chaos — slips her ribbons, takes the stairs — but she's watching you, not the exit, and what's on her face isn't gratitude. Cruelty works. It worked fast. It always works fast. That's the trap of it: you turned fear into a tool, and a whole crowd just learned the lesson from YOU.)*
- **Rook:** *(quiet now, no laugh in it)* "She's in. We're clear. ...That crowd would've followed you anywhere just then. That's the thing nobody tells you about scaring people, friend. It works. It just costs you the part of yourself that knew it was wrong. ...Get down here. We'll talk later. Or we won't." `[VOICE-FIX #3 — keep verbatim; thesis line]`
> **COST (legible):** set flag `crowd_weaponized` + raise world-fear into the Prison Zones; **no apprentice ally.**

---

## 6F — AFTERMATH CHOICE (where do you go next? → Prison Zones)
> **PROMPT:** *"The Herald is gone and the captive is in the tunnel — but a familiar figure was watching the whole thing from the wings. (Mr. Ankam steps forward; his reaction depends on Act One. See ankamReturn — fire the matching variant here.) As the stage empties and the castle bells ring alarm, where do you go next?"*

> **ENGINE:** Play the correct **`ankamReturn`** variant (Scene 5) immediately before this choice resolves.

| label | tag | effect |
|---|---|---|
| Down into Rook's tunnel with the captive — get her home first, everything else second. | **mercy** | `to_prison_zones` |
| Slip out clean and quiet through the under-stage dark — no witnesses, no trail. | **survival** | `to_prison_zones` |
| Walk out the front, slow, and let every warden see exactly who did this. | **cruelty** | `to_prison_zones` |

**MERCY result:**
- **Rook:** "Both of you, in the cart, heads down. Yew — you walked out of there. On your own feet, like you said. Nobody carried you. Remember that part."
- **Yew:** "I'll remember all of it. The cage. The ribbons. You reading that pompous fool's own words back at him. ...My father's not the only one in the valley they 'awarded' to somebody. There are more. They keep them somewhere past here. The prison zones. ...I'm not asking you to go. But I'm telling you they're there."
- **???:** *(Far off, past the gilded rot, a darker road. And rising under the alarm bells, a new sound: a single horn from the highest tower, slow and deliberate. Not a garrison call. An INTEREST. Somewhere in that castle, for the first time, Sufflok has stopped reading his ledger to ask about the one name nobody can file. Yours.)*

**SURVIVAL result:**
- **You:** "We don't celebrate. We don't linger. We were never here. Down, quiet, gone — and we leave them nothing to chase but a confused Herald and an empty cage."
- **Rook:** "That's the way. A rescue nobody can describe is a rescue nobody can punish. ...But heads up — past the festival road, the ground gets worse. The PRISON ZONES. Where they keep the people too valuable to award and too dangerous to free. If we're going forward, that's forward."
- **???:** *(You move like smoke through the under-stage dark. Behind you the kingdom is already rewriting tonight into something it can survive remembering. But a single horn calls from the high tower, slow and curious — and you understand, cold in your gut, that being unfileable just stopped being safe. The unfiled thing is the thing the tyrant comes to read himself.)*

**CRUELTY result:**
- **You:** "No. We don't sneak. Let them watch me leave. Let every warden on that wall carry my face home tonight and tell the next one. Fear travels faster than any horn."
- **Rook:** "...Yeah. It does. It's already traveling. You can see it on them — they're not even raising their launchers. ...That's the part that worries me. A scared enemy fights you. A TERRIFIED enemy fetches someone bigger. And there's only one thing bigger here."
- **???:** *(You walk out through a gauntlet of wardens who do not dare to flash a single warning light. It feels like power. It IS power. And from the highest tower a horn answers it — slow, patient, almost pleased. You wanted the castle to fear you. It does. And the thing that rules by fear has just recognized a rival, and is, at last, personally interested. The road past the gold leads down. To the prison zones. To him.)*

> **ACT TWO END.** Transition → PRISON ZONES (Act Three hook). Set flag `act_two_complete`; Sufflok-notice flag `sufflok_interested` (always set; intensity scales with cruelty).

---

# COMBAT ARENAS (pre-boss training waves)

> These three arenas teach the pillar verbs **before** the boss. Reuse the bestiary above. Ammo scarce by design (zone refill ~6–8 pebbles; pouch is the valve). All projectiles dash-through, all telegraphs honest.

## ARENA A — `festival_forecourt` (30×18 — TEACH LUNGE / COVER / CROSSFIRE)
```
##############################
# b b  @  P............P....g#  g = locked stage-gate (east)
#   C       cart        C    #
#  r   (open f dance-floor)  r#  central f = exposed kill-box (no cover)
#   C       cart        C    #
# b b  P............P........#
##############################
```
Cover is the verb: `#`/`r`/`C`/`cart` block sight + confetti pellets (pellets pop on them). Four cover islands in a loose diamond. Central `f` floor open on purpose (fast cross, fully exposed). Bushes soften aggro only (don't stop pellets). Map bigger than the Act One depot so projectiles have room to be dodged.

| wave | enemies | teaching note |
|---|---|---|
| 1 | `court_pikeman`, `court_pikeman` | **TEACH THE LUNGE.** Two lone Pikemen, lunges staggered → only one telegraph at a time. Read the chevron lane, side-dash it, Sling the recovery. No ranged pressure. **Restraint reward:** clean double-KO, zero hits → chits + pebbles (first "mercy pays" beat). |
| 2 | `confetti_trooper`, `court_pikeman` | **TEACH COVER.** One Trooper firing 3-fans + one Pikeman to pressure you off cover. Use a cover island to eat the fan, then close on the Pikeman OR wait the Trooper reload vent. Introduces "weave the gap vs dash the volley." Winnable by dodging even with zero KOs; KOs make it calmer. |
| 3 | `confetti_trooper`, `confetti_trooper`, `court_pikeman` | **CROSSFIRE.** Two Troopers on opposite islands → overlapping fans across the center; the open `f` box now punished hard. The Pikeman flushes you out of single safe spots. Survivable purely by movement; rewards KO'ing one Trooper to break the crossfire. |

## ARENA B — `rigged_decree_stage` (26×16 — TEACH BEAM / staged DURING the decree)
```
##########################
# NW panel        NE panel#  ← optional SURVIVAL rigging targets (interact)
#  S   f f f f f f f   S   #  S = spotlight rig
#   C prop   [cart podium] #  sparse center cover only
#  f f f f K(cage) f f f f #  K = captive holding cart-cage
# ====== g ============    #  = velvet rope, g = only way up
#  P (south apron, safe-ish audience lane)#
##########################
```
SPOTLIGHT RIG is the headline hazard: two sweeping beam-discs trace honest pre-rings across the open `f` stage. Hard cover sparse + center-clustered → you must TIME beams as much as hide. Velvet rope + single `g` gap tighten the dodge read. SURVIVAL players eye the two wing panels (NE/NW interact targets) to kill beams. Pellet cover still works vs Trooper support. Pebbles double as the SURVIVAL tool, so spending them on enemies vs hazards is a real choice.

| wave | enemies | teaching note |
|---|---|---|
| 1 | `spotlight_turret`, `court_pikeman`, `court_pikeman` | **TEACH THE BEAM.** One sweeping spotlight + two Pikemen whose lunge lanes are angled to shove you toward the bright disc. Time the pre-ring; don't dash INTO the light. Rigging panel present but optional (foreshadows SURVIVAL boss route). |
| 2 | `spotlight_turret`, `spotlight_turret`, `confetti_trooper`, `court_pikeman` | **BEAM CROSSFIRE + PUZZLE PRESSURE.** Two spotlights sweeping opposite directions carve shifting safe-gaps; a Trooper fan + a Pikeman keep you moving. Staged DURING the decree — narrative solution is the WORDING exploit, but mechanically survive the overlapping sweeps via the brief shared-clear windows. Strong SURVIVAL incentive to sling the two rigging panels (delete a beam each). |

> **FAIRNESS GUARANTEE (build requirement):** in B-wave 2, **hard-code the two spotlight phase-offsets so a shared safe tile ALWAYS exists** (the bible promises "brief windows where both pre-rings clear the same tile" — enforce it, don't leave it emergent, or the overlap can lock unsurvivable). This is the hardest non-boss moment in the act; for a 5-heart player it's doable only with the guaranteed gap.

## ARENA C — `grand_finale_court` = the BOSS arena (see Scene 6B). Refill pebbles to full on entry.

---

# SCENE FLOW DIAGRAM

```
[ACT ONE flags: ankam_mercy / ankam_survival / ankam_cruel] ─────────────┐
                                                                          │
SCENE 1  kingdom_gate ── tutorial: dash THROUGH courtesy volley           │
   │   CHOICE goal: set_goal_rescue / set_goal_survive / set_goal_fear    │
   ▼                                                                      │
SCENE 2  court_town_hub (HUB, free-roam)                                  │
   │   • Decree Board seen (puzzle planted)                               │
   │   • Yew sighted in cage                                              │
   │   • CHOICE recruit: calm / give_chits / scare  → chits (+intel)      │
   ├──► SCENE 3  shopkeeper_stall (SHOP, repeatable)                      │
   │       • buy gear / Whipcord / pouch                                  │
   │       • lore (lean-gated) + portal sliver                            │
   │       • CHOICE: shop_discount / shop_open / shop_guarded             │
   │       (pricing: MERCY -25% +loaf / SURVIVAL fair / CRUELTY spike)    │
   │   (recommended: Shop → then Puzzle)                                  │
   ▼                                                                      │
   [ARENA A festival_forecourt: waves 1-3  TEACH lunge/cover/crossfire]   │
   ▼                                                                      │
SCENE 4  rescue_buildup                                                   │
   │   • PETITION puzzle: "ask for NOTHING" → stage_access (sash+pass)    │
   │   • Rook locks plan                                                  │
   │   • Yew CHOICE: steady / brief / harden                              │
   ▼                                                                      │
   [ARENA B rigged_decree_stage: waves 1-2  TEACH beam + decree pressure] │
   ▼                                                                      │
SCENE 4B  puzzle_weigh_in (Ankam presides; captive Bell/Yew)              │
   │   steps: read 3 frags → reveal soot 4th line → CHOICE:              │
   │     expose_decree (M, +ally Ankam-informant)                        │
   │     disable_rigging (S, +forged CASTLE PASS)                        │
   │     upstage_crown (C, +castle_heat, no pass)                        │
   │   → captive freed → push to stage                                    │
   ▼                                                                      │
SCENE 6  festival_stage (BOSS: Court Herald, hp 0, CONDUCT meter)         │
   │   PHASE 1 pikemen+1 spotlight  (locate 3 levers)                    │
   │   PHASE 2 +spotlights+confetti+usher (VULN windows)                 │
   │   PHASE 3 confetti barrage, script glitches (meter CLOSES mid-phase)│
   │   ── RESOLUTION FORK ──                                             │
   │     expose_script (M): crowd laughs → +apprentice ally + cage key   │
   │     disable_rigging (S): stage dies → clean exit, no ally           │
   │     outperform_herald (C): crowd turns → fast, crowd_weaponized     │
   │   ◄── SCENE 5 ankamReturn variant fires here ──────────────────────┘
   │       (tippedOff / obstructive / terrified per Act One flag)
   ▼
SCENE 6F  aftermath CHOICE → to_prison_zones (M/S/C flavor)
   ▼
[ACT TWO END] flags: act_two_complete, sufflok_interested(+),
   (+apprentice_defected / +castle_pass / +crowd_weaponized per path)
   ──► PRISON ZONES (Act Three)
```

---

# NEW ENGINE PIECES REQUIRED (build checklist)

### Combat / projectiles
- [ ] **`melee_lunge_line`** pikeman behavior: wind-up → fixed-lane dash (~4 tiles) → overshoot → ~0.9s stunnable recovery; chevron-lane telegraph (0.55s) + gold pike-tip flash; never tracks mid-lunge; conductor staggers paired lunges.
- [ ] **`fan_spread_3`** trooper behavior: 3-pellet fan aimed at current position (no lead); gaps > player hitbox at mid-range; warm-barrel + 3 aim-line telegraph (0.5s) + rising "fwip"; ~1.1s reload-vent KO window.
- [ ] **`sweeping_beam_disc`** spotlight: moving circle on a parametric loop, radius R; **timer-based damage (in-disc >0.4s = 1 heart, no knockback)**; 0.6s dim pre-ring telegraph; **VFX decal under disc, NO tile-state**. Disable hook (panel/lever).
- [ ] **`follow_spot`** variant: spotlight that lag-tracks the player (~0.4s) with a floor warn-reticle; defeated by hard cuts behind cover / into curtain-wing dark.
- [ ] **`usher_support`** AI: straight-line move to target (ignore cover collision, no navmesh), freeze + 2.5s revive progress bar, interruptible, flees on dash/sling; **never armed**.
- [ ] **Whipcord charge-shot** (HOLD to charge harder KO) — same input reused for the CRUELTY "pose" hold and the puzzle interacts.
- [ ] **Confetti-cannon stage hazard:** radial fans + sweeping arcs, alternating salvos, **CRESCENDO double-fan with one EERIE-safe glowing lane**, streamer-streak fences.

### Boss systems
- [ ] **Conductor boss controller** (`court_herald`, hp 0): announce-then-act rhythm; baton cues (raised=spread, swept-low=spotlight) + overhead cue-word banner + brass-sting audio; **Phase-3 half-beat-early glitch** tell; 3 escalating phase configs.
- [ ] **CONDUCT meter** (not an HP bar): three fill-paths (MERCY page-knocks ×3 / SURVIVAL panel-interacts ×3 / CRUELTY KO-pace + follow-spot poses); **must be able to close mid-Phase-3**.
- [ ] **3 canonical VULN targets only** `[FEAS #4]`: **script-stand** (interact), **3 wing panels** (interact, reused sprite), **follow-spot pose-zone** (position+hold check). Horn/rig-rope/pulley/feed-belt are flavor names mapped onto these.
- [ ] **SURVIVAL panels + CRUELTY pose = interact / hold-button (NOT Sling)** `[FEAS #5]`; **pebble refill-to-full on boss-arena entry + each phase start** (ammo softlock guard).
- [ ] **Crowd reaction meter** (laughter / silence / dread) driving the resolution + flavor.

### Puzzle systems
- [ ] **Petition dialogue puzzle** (Scene 4): accept the "ask for NOTHING" solution (or `decree_loophole` item) → grant `stage_access` + sash/pass.
- [ ] **Decree-assembly UI panel:** read 3 banner-fragments (press Z) → build Articles I–III; **sling-soot-reveal** of the charred 4th line (`decree_loophole_seen`).
- [ ] **King's Scale rig:** 2-pan balance; CROWN pan pre-loaded + Article-II-protected; **cinch-rope sling target** (Exploit A); fulcrum-drop animation; **carriable tribute crates** (doomed path, movement-slowed).
- [ ] **COURT CLOCK** = reuse Act One detection-bar widget; idle → 2-Pikeman patrol spawn.
- [ ] **Single-interact confetti-cannon "push+fire"** `[FEAS #7]` (no drag-rotate).
- [ ] Puzzle branch resolver (`expose_decree` / `disable_rigging` / `upstage_crown`) wiring item grants + flags.

### Shop / economy
- [ ] **Shop overlay menu** `[FEAS #3]` (no spatial interior); 6-item stock; one-time-purchase locks for pouch/whipcord/token.
- [ ] **CHITS currency** + pickups (enemy drops, stashes, recruit/Ankam gifts).
- [ ] **Inventory + consumables:** bandage (`heal` 2), grateful loaf (`heal_small` 1), smokebead (`smoke_escape` ~3s invis), pebble pouch (`ammo_capacity_up`), whipcord (`upgrade_sling`), counterfeit token (`decree_loophole`).
- [ ] **Lean-gated pricing engine** (`discountForMercy`): MERCY −25% + free loaf + 2 lore; SURVIVAL fair + 2 lore + first restock; CRUELTY −10% consumables / +30% whipcord+token / no loaf / 1 lore.

### Flags / state
- [ ] **Goal flag** (`set_goal_rescue`/`survive`/`fear`).
- [ ] **Moral counters** (MERCY/SURVIVAL/CRUELTY) + per-zone KO-not-killed tracking (feeds shop discount + crowd meter).
- [ ] **Carry-in** Act One Ankam flags → `ankamReturn` variant selector.
- [ ] **Act Two outcome flags:** `stage_access`, `decree_loophole_seen`, branch flags (`ankam_turned`/`decree_exposed`, `castle_pass`/`rigging_disabled`, `crowd_weaponized`/`castle_heat_up`), boss-branch flags (`apprentice_defected`), `bell_freed`, `act_two_complete`, `sufflok_interested`.
- [ ] **`castle_heat`** scalar → scales Pikemen density + Herald difficulty (raised by CRUELTY).

### Content / set-dressing (procedural, no external assets)
- [ ] Gold-and-rot palette + flaking gold-leaf banner sprites; recolored **falling-glitter mote field**; hot footlight glare + curtain-wing **full-dark cover** (reuse depot stealth/vision-cone tech for spotlights).
- [ ] Loudspeaker-cart prop (looping warped audio line); amplified-Herald voice processing (brass-cone "weather event" filter).
- [ ] Cage/gift-box sprite (ribbons = knotted-not-locked per `ribbon_intel`); painted **Sufflok-eye** backdrop (surveillance device that goes dark on MERCY curtain).

---

*End of Act Two shooting script — "The Theatrical Crown." Non-lethal contract intact. Telegraphs honest. Restraint pays immediately (shop discount, clean-KO drops, apprentice ally). Boss out-thought via CONDUCT meter, never an HP race. Feasibility cuts applied: EXPLOIT B removed, VULN targets collapsed to 3, panels/poses are interact-not-sling with ammo refills, shared-safe-tile guaranteed, biting awning is flavor only.*