"""
Scam prompt library for Scam School game.
Organized by category and difficulty level.
"""

import random
from dataclasses import dataclass
from typing import List

@dataclass
class ScamPrompt:
    """A scam prompt for players to read."""
    category: str
    difficulty: str  # "easy", "medium", "hard"
    title: str
    script: str
    tips: str  # Acting tips for the player


# =============================================================================
# EASY PROMPTS - Over-the-top, classic scam scripts
# =============================================================================

EASY_PROMPTS = [
    ScamPrompt(
        category="Tech Support",
        difficulty="easy",
        title="The Virus Alert",
        script="""Hello! This is John from Microsoft Windows Technical Support Department! 
We have detected a VERY DANGEROUS virus on your computer! Your computer is sending 
error messages to our server! Do NOT turn off your computer! I need you to give me 
remote access RIGHT NOW or you will lose ALL your files! This is an emergency!""",
        tips="Sound panicked and urgent. Emphasize words like DANGEROUS and RIGHT NOW!"
    ),
    ScamPrompt(
        category="Prize Winner",
        difficulty="easy",
        title="The Lucky Winner",
        script="""CONGRATULATIONS! You have been selected as our GRAND PRIZE WINNER! 
You have won a FREE luxury cruise to the Bahamas worth ten thousand dollars! 
But you must act NOW! This offer expires in the next 15 minutes! All I need is 
your credit card number to pay the small processing fee of just $99!""",
        tips="Be extremely excited and enthusiastic! Rush through to create urgency!"
    ),
    ScamPrompt(
        category="IRS/Government",
        difficulty="easy",
        title="The Tax Collector",
        script="""This is Officer Williams from the Internal Revenue Service. We are calling 
because you owe $5,847 in back taxes! If you do not pay immediately, a warrant 
will be issued for your arrest TODAY! The police are already on their way! 
You must pay now using gift cards to avoid going to JAIL!""",
        tips="Sound stern and authoritative. Threaten consequences dramatically!"
    ),
    ScamPrompt(
        category="Bank Fraud",
        difficulty="easy",
        title="The Suspicious Activity",
        script="""URGENT ALERT from your bank's fraud department! We have detected 
suspicious activity on your account! Someone in Nigeria is trying to steal 
$50,000 from your savings! I need your account number, PIN, and social security 
number RIGHT NOW to stop this transaction before it's too late!""",
        tips="Sound alarmed and worried for the victim. Create panic!"
    ),
    ScamPrompt(
        category="Romance Scam",
        difficulty="easy",
        title="The Stranded Millionaire",
        script="""My darling! It is me, your beloved Prince Abdullah! I am stuck at the 
airport in Dubai! My wallet was stolen and I cannot fly home to be with you! 
Please wire me $2,000 immediately! Once I return, I will give you access to 
my $50 million fortune! I love you so much my sweetheart!""",
        tips="Be dramatic and emotional! Sound desperate but loving!"
    ),
]


# =============================================================================
# MEDIUM PROMPTS - Standard scammer scripts
# =============================================================================

MEDIUM_PROMPTS = [
    ScamPrompt(
        category="Tech Support",
        difficulty="medium",
        title="The Subscription Renewal",
        script="""Hi, this is calling from Norton Antivirus subscription services. 
I'm reaching out because your annual subscription of $399.99 is about to renew 
automatically. If you did not authorize this charge, please press 1 to speak 
with a representative who can help cancel this and process your refund.""",
        tips="Sound professional and helpful. Act like you're doing them a favor."
    ),
    ScamPrompt(
        category="Prize Winner",
        difficulty="medium",
        title="The Survey Reward",
        script="""Hi there! I'm calling from Consumer Research Group. You recently 
completed our online survey and you've qualified for a $500 Walmart gift card! 
We just need to verify your shipping address and collect a small $4.95 shipping 
fee. Can I get your card information to process that for you?""",
        tips="Be friendly and conversational. Make it sound routine and normal."
    ),
    ScamPrompt(
        category="IRS/Government",
        difficulty="medium",
        title="The Social Security Issue",
        script="""This is an automated message from the Social Security Administration. 
We have detected fraudulent activity linked to your social security number. 
Your benefits will be suspended unless you verify your identity. Please provide 
your full social security number and date of birth to our agent.""",
        tips="Sound robotic at first, then switch to a concerned human agent."
    ),
    ScamPrompt(
        category="Bank Fraud",
        difficulty="medium",
        title="The Verification Call",
        script="""Good afternoon, this is Sarah from Chase Bank's security team. We've 
noticed some unusual login attempts on your online banking account from an 
unrecognized device. For your protection, I need to verify your identity. 
Can you confirm the last four digits of your social and your account PIN?""",
        tips="Sound professional and genuinely concerned. Use proper phone etiquette."
    ),
    ScamPrompt(
        category="Delivery Scam",
        difficulty="medium",
        title="The Missed Package",
        script="""Hello, this is FedEx delivery services. We attempted to deliver your 
package today but no one was available to sign. Your package contains valuable 
items and will be returned to sender in 24 hours. To reschedule delivery, 
please provide your credit card for the $3.99 redelivery fee.""",
        tips="Sound slightly inconvenienced but professional. Create mild urgency."
    ),
]


# =============================================================================
# HARD PROMPTS - Sophisticated social engineering
# =============================================================================

HARD_PROMPTS = [
    ScamPrompt(
        category="Business Email",
        difficulty="hard",
        title="The CEO Request",
        script="""Hey, this is Mark from accounting. The CEO just pulled me into an urgent 
meeting - we need to process a wire transfer for the acquisition deal before 
end of business today. The regular approval chain is too slow. Can you help 
me push through this $45,000 transfer? I'll get the paperwork sorted after.""",
        tips="Sound stressed but casual. Act like you're a trusted colleague."
    ),
    ScamPrompt(
        category="Tech Support",
        difficulty="hard",
        title="The IT Department",
        script="""Hi, this is Kevin from the IT help desk. We're doing a security audit 
and noticed your workstation hasn't received the latest patch. I can push 
the update remotely, but I'll need you to confirm your network credentials 
so I can verify your machine in our system. Should only take a minute.""",
        tips="Be casual and helpful. Use technical-sounding language naturally."
    ),
    ScamPrompt(
        category="Investment",
        difficulty="hard",
        title="The Exclusive Opportunity",
        script="""Good morning! I'm a licensed broker with Preston Securities. One of our 
institutional clients is divesting shares before their quarterly report. 
We have a small allocation available for select retail investors. This isn't 
public information, but I wanted to give you first access. Interested?""",
        tips="Sound sophisticated and exclusive. Make them feel special."
    ),
    ScamPrompt(
        category="Family Emergency",
        difficulty="hard",
        title="The Grandchild in Trouble",
        script="""Grandma? It's me... I'm in trouble. I was in a car accident and I got 
arrested. Please don't tell mom and dad, they'll be so disappointed. My lawyer 
says I need $3,000 for bail. Can you wire it to me? I promise I'll pay you 
back. Please, I really need your help right now...""",
        tips="Sound emotional and slightly panicked. Use a younger, vulnerable voice."
    ),
    ScamPrompt(
        category="Utility Scam",
        difficulty="hard",
        title="The Power Company",
        script="""Good afternoon, I'm calling from the electric company's billing department. 
Our system shows your account is 60 days past due. To avoid service interruption 
this evening, we can process a same-day payment over the phone. We accept 
most payment methods including prepaid cards for your convenience.""",
        tips="Sound matter-of-fact and business-like. Be polite but firm."
    ),
]


def get_all_prompts() -> List[ScamPrompt]:
    """Get all available prompts."""
    return EASY_PROMPTS + MEDIUM_PROMPTS + HARD_PROMPTS


def get_prompts_by_difficulty(difficulty: str) -> List[ScamPrompt]:
    """Get prompts filtered by difficulty level."""
    difficulty = difficulty.lower()
    if difficulty == "easy":
        return EASY_PROMPTS
    elif difficulty == "medium":
        return MEDIUM_PROMPTS
    elif difficulty == "hard":
        return HARD_PROMPTS
    else:
        return get_all_prompts()


def get_random_prompt(difficulty: str = None) -> ScamPrompt:
    """Get a random prompt, optionally filtered by difficulty."""
    if difficulty:
        prompts = get_prompts_by_difficulty(difficulty)
    else:
        prompts = get_all_prompts()
    return random.choice(prompts)


def get_categories() -> List[str]:
    """Get list of all unique categories."""
    all_prompts = get_all_prompts()
    return list(set(p.category for p in all_prompts))


def get_prompt_by_category(category: str, difficulty: str = None) -> ScamPrompt:
    """Get a random prompt from a specific category."""
    if difficulty:
        prompts = get_prompts_by_difficulty(difficulty)
    else:
        prompts = get_all_prompts()
    
    category_prompts = [p for p in prompts if p.category == category]
    if not category_prompts:
        return get_random_prompt(difficulty)
    return random.choice(category_prompts)
