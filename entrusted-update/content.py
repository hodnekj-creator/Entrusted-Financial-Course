# Content for the Entrusted course site. Scripture is referenced and paraphrased, never quoted at length;
# build.py links every reference to the NIV on Bible Gateway.

# Dave Ramsey's Baby Steps (Ramsey Solutions), minus his college-fund step, which this course leaves out on purpose.
# The second item in each row is his wording.
# Each row: short name, the step, scripture, why, how you know you are done.
STEPS = [
    ("Starter emergency fund", "Save $1,000 for your starter emergency fund.", "Proverbs 21:20",
     "The wise keep something in store. $1,000 is small on purpose: it is quick to save, and it keeps the next flat tire or copay from going on a card while you get out of debt.",
     "$1,000 sits in a separate savings account, kept for emergencies only."),
    ("Debt snowball", "Pay off all debt (except the house) using the debt snowball.", "Proverbs 22:7; Psalm 37:21",
     "The borrower serves the lender, and what you borrow you repay. List every debt except the mortgage from smallest balance to largest. Pay the minimum on all of them and attack the smallest with every extra dollar. When it is gone, roll its payment into the next one. The quick wins are what keep you going.",
     "No car loans, student loans, medical bills, personal loans or card balances. Only the house is left."),
    ("Full emergency fund", "Save 3–6 months of expenses in a fully funded emergency fund.", "Proverbs 6:6-8; Genesis 41",
     "The ant stores in summer and Joseph stored in the good years. A full emergency fund covers a job loss, not just a repair.",
     "Three months of expenses saved if your income is steady, six if it is irregular or you are the only earner."),
    ("Invest 15%", "Invest 15% of your household income in retirement.", "Ecclesiastes 11:2; Proverbs 21:5; Proverbs 14:15",
     "Diligent plans lead to profit, and spreading investments guards against what you cannot foresee. Time does most of the work, so starting early matters more than starting big. Never do something with your money that you do not understand. If you want help, look for an adviser with the heart of a teacher: someone who explains what you are buying and why, and is glad when you ask questions.",
     "15% of gross household income goes into retirement accounts every month, automatically."),
    ("Pay off the home", "Pay off your home early.", "Romans 13:8",
     "Let no debt remain outstanding. Extra payments on the mortgage, made while step 4 keeps going, turn a 30-year obligation into a paid-for home and free up the largest payment most people have.",
     "You own your home outright."),
    ("Build wealth and give", "Build wealth and give.", "Proverbs 13:22; 1 Timothy 6:17-19",
     "A good person leaves an inheritance for their children's children, and those who have much are told to be rich in good deeds and ready to share. Wealth at this step is a larger thing to manage, not a finish line.",
     "No debt of any kind, a current will, and giving that grows faster than your lifestyle."),
]

STEPS_NAME = "The Baby Steps"
STEPS_CREDIT = "The Baby Steps are Dave Ramsey's plan, taught in his books and in Financial Peace University. This course follows them, without his college-fund step, and adds scripture to each step. Because of that, our step 5 and step 6 are his step 6 and step 7."
STEPS_URL = "https://www.ramseysolutions.com/dave-ramsey-7-baby-steps"
STEPS_ORDER = "Baby Steps 1 to 3 are done one at a time, in order. Baby Steps 4 and 5 are worked at the same time."

# Where this course adds to the Baby Steps. Notes, not steps.
STEP_NOTES = [
    ("Take the employer match",
     "If your employer matches retirement contributions, put in enough to get the full match at every step, even while you work on Baby Steps 1 to 3. Dave Ramsey teaches pausing all investing until step 4; this course treats the match as part of your pay."),
    ("Credit cards",
     "Dave Ramsey teaches cutting up credit cards, and people do spend more with cards, so skipping them is wise. If you keep one, pay the full statement balance every month. The first month you cannot, it goes in a drawer."),
]

# Short paraphrases for step references that no session lists word for word.
STEP_PARAS = {
    "Genesis 41": "Joseph stores grain in seven good years to carry Egypt through seven lean ones.",
    "2 Corinthians 12:14": "Children should not have to save up for their parents, but parents for their children.",
    "Proverbs 14:15": "The gullible believe anything; the prudent think about where their steps lead.",
    "Luke 14:28": "Count the cost before you build.",
    "Proverbs 27:23": "Know the condition of your flocks.",
}

EVERY_STEP = ("At every step", "Give first and keep a written budget.", "Proverbs 3:9-10; Proverbs 27:23",
              "Giving first is how a manager acknowledges the owner. A budget is how a manager knows the condition of what he has been handed.")

# Articles linked from the money basics and from session slides.
LINKS = {
    "cfpb_compound": ("How does compound interest work?", "Consumer Financial Protection Bureau",
                      "https://www.consumerfinance.gov/ask-cfpb/what-is-compound-interest-en-1683/"),
    "sec_calc": ("Compound interest calculator", "Investor.gov, U.S. Securities and Exchange Commission",
                 "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator"),
    "cfpb_apr": ("What is a credit card interest rate? What does APR mean?", "Consumer Financial Protection Bureau",
                 "https://www.consumerfinance.gov/ask-cfpb/what-is-apr-en-44/"),
    "sec_401k": ("401(k) plans", "Investor.gov, U.S. Securities and Exchange Commission",
                 "https://www.investor.gov/additional-resources/retirement-toolkit/employer-sponsored-plans/traditional-and-roth-401k-plans"),
    "sec_stocks": ("How stock markets work", "Investor.gov, U.S. Securities and Exchange Commission",
                   "https://www.investor.gov/introduction-markets/how-markets-work"),
    "irs_brackets": ("Federal income tax rates and brackets", "Internal Revenue Service",
                     "https://www.irs.gov/filing/federal-income-tax-rates-and-brackets"),
    "ramsey": ("The Baby Steps", "Ramsey Solutions", STEPS_URL),
}


def ws(title, cols, rows, note=""):
    """A blank worksheet table."""
    head = "".join(f"<th>{c}</th>" for c in cols)
    body = ""
    for r in rows:
        if isinstance(r, str):
            cells = f"<td>{r}</td>" + "<td></td>" * (len(cols) - 1)
        else:
            cells = "".join(f"<td>{c}</td>" for c in r)
        body += f"<tr>{cells}</tr>"
    n = f"<p class='wsnote'>{note}</p>" if note else ""
    return f"<div class='worksheet'><h3>{title}</h3>{n}<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


INVENTORY = ws("What I manage", ["What I have been entrusted with", "Amount"], [
    "Checking and savings", "Retirement or investment accounts", "Vehicle and other things I could sell",
    "<b>Total I hold</b>", "Student loans", "Car loan", "Credit card balance not paid off", "Other debt",
    "<b>Total I owe</b>", "<b>Hold minus owe</b>", "Monthly income after tax", "Skills and abilities I can earn with"],
    "For your eyes only. A negative total is common, especially with student loans.")

INCOME = ws("Income and skills", ["Question", "My answer"], [
    "What I am paid for today", "Skills I have that I am not paid for yet", "One skill that would raise my income in 2 years",
    "What it would cost in time and money to get it", "Side work I could do 5 hours a week", "Where I am working for people's approval instead of the Lord",
    "My plan for one day of rest each week"])

BUDGET = ws("Monthly budget", ["Category", "Planned", "Actual"], [
    "<b>Income after tax</b>", "Giving", "Saving and investing", "Housing and utilities", "Food", "Transport",
    "Insurance and medical", "Debt payments", "Phone and subscriptions", "Fun and eating out", "Everything else",
    "<b>Income minus all lines (should be zero)</b>"],
    "Give every dollar a job before the month starts. Giving and saving go first, not last.")

FIRST_PAY = ws("First-paycheck budget", ["Category", "In college now", "On my first salary"], [
    "<b>Income after tax</b>", "Giving", "Saving and investing", "Housing and utilities", "Food", "Transport",
    "Loan payments", "Phone and subscriptions", "Fun and eating out", "<b>Left over</b>"],
    "The goal: the second and third columns look as alike as possible, and the gap goes to giving, saving and debt.")

GIVING = ws("Giving plan", ["Question", "My answer"], [
    "My monthly income", "What I gave last month", "What I have decided in my heart to give", "As a share of my income",
    "Where it will go", "The day of the month it leaves my account", "Has giving ever stretched me? When?",
    "What I am praying over"])

EFUND = ws("Emergency fund", ["Line", "Amount"], [
    "<b>Baby Step 1: starter emergency fund</b>", "What I have saved today", "What I can add each month",
    "Months until $1,000 is saved",
    "Housing and utilities (monthly)", "Food", "Transport", "Insurance and medical", "Minimum debt payments",
    "<b>One month of essentials</b>", "<b>Baby Step 3, low end: times 3</b>", "<b>Baby Step 3, high end: times 6</b>"],
    "The starter fund is $1,000. Keep it in a separate savings account so it is easy to reach and hard to spend by accident.")

DEBT = ws("Debt snowball", ["Debt (all but the house)", "Balance", "APR", "Minimum payment", "Snowball order", "Paid off on"], [
    ["", "", "", "", "", ""]] * 6 + [["<b>Totals</b>", "", "", "", "", ""]],
    "Number your debts from the smallest balance to the largest. Pay the minimum on all of them and put every extra dollar on number 1. When it is gone, add its payment to number 2, and keep rolling.")

APR = """<div class='worksheet'><h3>Loans and rates cheat sheet</h3><table><thead><tr><th>Term</th><th>What it means</th></tr></thead><tbody>
<tr><td>Principal</td><td>The amount you borrowed and still owe.</td></tr>
<tr><td>Interest</td><td>What the lender charges for the use of the money.</td></tr>
<tr><td>APR</td><td>Annual percentage rate: the yearly rate on a loan, before compounding. This is the number you <b>pay</b>.</td></tr>
<tr><td>APY</td><td>Annual percentage yield: the yearly rate including compounding. This is the number you <b>earn</b> on savings.</td></tr>
<tr><td>Why both exist</td><td>A card at 24% APR that compounds daily really costs about 27% a year. Lenders show the smaller number, banks advertise the bigger one.</td></tr>
<tr><td>Term</td><td>How long the loan lasts. A longer term means a lower payment and more total interest.</td></tr>
<tr><td>Minimum payment</td><td>The least you can pay without a penalty. On a card it is set so the balance lasts for years.</td></tr>
<tr><td>Co-signing</td><td>You owe the whole debt if the other person stops paying. See Proverbs 22:26-27.</td></tr>
</tbody></table></div>"""

INVEST = ws("Match and the cost of waiting", ["Question", "My answer"], [
    "Does my employer match? Up to what percent?", "What percent am I contributing now?", "Am I getting the full match?",
    "Accounts I have (401(k), Roth IRA, other)", "Monthly amount I could invest today",
    "Value at 65 if I start now (use the calculator)", "Value at 65 if I wait ten years", "The difference"],
    "Use a conservative return such as 7% a year. Past returns do not guarantee future ones.")

ACCOUNTS = """<div class='worksheet'><h3>Retirement accounts cheat sheet</h3><table><thead><tr><th>Account</th><th>How it works</th></tr></thead><tbody>
<tr><td>401(k) or 403(b)</td><td>Offered through an employer. Money comes out of your paycheck automatically. Often comes with a match.</td></tr>
<tr><td>Traditional</td><td>You skip the tax now and pay it when you take the money out in retirement.</td></tr>
<tr><td>Roth</td><td>You pay the tax now, and qualified withdrawals in retirement are tax-free. Often a good fit when your income is low, as in a first job.</td></tr>
<tr><td>IRA</td><td>A retirement account you open yourself, separate from any employer. Comes in traditional and Roth versions.</td></tr>
<tr><td>Index fund</td><td>One fund that owns a small piece of hundreds of companies. Built-in diversification at low cost.</td></tr>
<tr><td>Contribution limits</td><td>Set by the IRS and changed most years. Look up the current numbers before you plan.</td></tr>
</tbody></table></div>"""

LEGACY = """<div class='worksheet'><h3>Legacy checklist</h3><ul class='checks'>
<li>I have a will, and it is current</li><li>Every account has a named beneficiary</li>
<li>Someone I trust knows where my documents and passwords are</li><li>I have enough life insurance for the people who depend on me</li>
<li>My children (or the young people I influence) have seen me give</li><li>I have taught someone younger how to budget</li>
<li>I have decided what I will give while I am alive, not only after</li><li>I can name my \"enough\" number</li></ul></div>"""

STEP_MARK = ws("Which Baby Step am I on?", ["Baby Step", "Done", "Working on it", "Not yet"], [
    [f"{i+1}. {s[0]}", "", "", ""] for i, s in enumerate(STEPS)])


C1 = dict(
    title="Whose money is it?",
    big="God owns everything you will ever earn. Your job is to manage it faithfully, starting with what you have now.",
    scripture=["Psalm 24:1|Everything on earth belongs to the Lord.",
               "1 Chronicles 29:14|David admits that what he gives to God came from God first.",
               "Matthew 25:14-30|The parable of the talents: a master entrusts his wealth to three servants and returns to settle accounts."],
    opener="If someone handed you $10,000 tomorrow with no strings attached, what would you do with it?",
    teach=[("God owns it. You manage it.",
            "Psalm 24:1 leaves nothing out. A manager makes real decisions and has real freedom, but he never forgets whose name is on the account. Picture house-sitting: you live there and make choices every day, and you still do not repaint the kitchen. The $10,000 always has strings attached."),
           ("The manager's job is faithfulness, not size.",
            "The servant with two bags hears the same words as the servant with five. Two people on very different incomes are measured the same way: what did you do with what you were handed? The parable does not promise that faithful people get rich. It promises that the master notices."),
           ("A wrong view of the owner produces fear.",
            "The third servant buried the money because he saw the master as harsh. How you picture God shapes how you handle money: fear hides and hoards, trust puts it to work."),
           ("Giving shows who you think the owner is.",
            "The tithe is Old Testament law and a good practice to learn from. The New Testament instruction in 2 Corinthians 9:7 is to give what you have decided in your heart, cheerfully. Decide on purpose and pray over the number. If giving has never stretched you, and you have never given a tenth, pray over it more.")],
    skill=("Take inventory", "A manager cannot be faithful with what he has not counted. Fill in the inventory: what you hold, what you owe, what comes in. Then read the step card once from top to bottom. The rest of the course walks through it."),
    discuss=["Where do you most naturally think \"this is mine\": your paycheck, your time, your stuff?",
             "The third servant acted out of fear. Where does fear drive your money decisions?",
             "What would change this week if you were managing your money for someone you had to report to?",
             "What is one thing you are already managing well?"],
    action=["Fill in the \"What I manage\" inventory.", "Decide what you will give from your next paycheck, and pray over the number before you settle it."],
    worksheet=INVENTORY,
    guard="The parable is about faithfulness while the master is away. Do not teach it as a promise of wealth, and do not skip the third servant: his problem starts with his view of the master.",
    objections=[("I earned it, so it is mine.", "Go to Deuteronomy 8:17-18. Effort is real, and the ability behind it was given."),
                ("I am broke, so this does not apply yet.", "Go to Luke 16:10. Habits form at small numbers, and someone with $500 is already a manager."),
                ("Does God want me to be rich?", "The parable makes no such promise. Read Proverbs 30:8-9 together.")],
    prep=["Read Matthew 25:14-30 twice and note what surprises you.", "Fill in the inventory yourself first.", "Print one step card and one handout per person.",
          "Warn people before they write that a negative inventory total is normal."],
)

C2 = dict(
    title="Work as worship",
    big="Work is the first thing you manage. You do it for the Lord, and the ability to do it is a gift.",
    scripture=["Colossians 3:23-24|Whatever you do, work at it with all your heart, as working for the Lord.",
               "Proverbs 10:4|Lazy hands bring poverty; diligent hands bring wealth.",
               "Deuteronomy 8:17-18|Do not say your own strength produced your wealth; God gives the ability to produce it.",
               "Psalm 127:2|Rising early and staying up late in anxious toil is in vain; He gives His loved ones sleep."],
    opener="What is the hardest you have ever worked for something, and who were you doing it for?",
    teach=[("Your income is your largest financial tool.",
            "Cutting expenses has a floor. Growing what you earn through skill and diligence does not. Proverbs ties diligence to gain over and over, and a person skilled in their work stands out (Proverbs 22:29)."),
           ("Who you work for changes how you work.",
            "Paul wrote Colossians 3:23 to bondservants with no say over their jobs. The point is the audience: you work for the Lord whether or not your boss is watching, fair, or grateful."),
           ("The ability to earn is a gift, not a trophy.",
            "Deuteronomy 8 warns against the moment success arrives and you credit yourself. Diligence is commanded and pride about the results is forbidden, both at once."),
           ("Rest is part of faithful work.",
            "The same God who commands diligence commands Sabbath. Working every waking hour is not obedience to Colossians 3:23; it usually means the work has become the master.")],
    skill=("Raise your earning ability", "List what you are paid for today, what skills you have that you are not yet paid for, and one skill that would raise your income in two years. Decide what it costs to get it. Then name one day a week you will rest."),
    discuss=["Would your work look different this week if the Lord were your direct supervisor?",
             "Where are you tempted to coast? Where are you tempted to overwork?",
             "Who has God used to give you the abilities you earn with?",
             "What is one skill you could build this year?"],
    action=["Fill in the income and skills worksheet.", "Pick one day this week to rest, and keep it."],
    worksheet=INCOME,
    guard="This verse was written inside instructions to bondservants. It is about who you serve, not about hustle. Always pair it with rest (Exodus 20:8-10; Psalm 127:2).",
    objections=[("My job is meaningless.", "Paul's first readers had less choice than anyone in the room. The meaning comes from who the work is for."),
                ("So I should work more hours?", "Not necessarily. Diligent hours, growing skill and real rest. Psalm 127:2 calls anxious overwork vain."),
                ("Is wanting a raise greedy?", "Growing what you manage is faithful. 1 Timothy 6:9-10 warns about wanting to get rich, which is a different aim.")],
    prep=["Think of one story from your own work where the audience mattered.", "Fill in the worksheet yourself.", "Print handouts."],
)

C3 = dict(
    title="Know your flocks",
    big="A faithful manager knows exactly what he has and decides ahead of time where it goes. That is a budget.",
    scripture=["Proverbs 27:23-24|Know the condition of your flocks and give careful attention to your herds, because riches do not last forever.",
               "Luke 14:28-30|No one builds a tower without first sitting down to estimate the cost.",
               "Proverbs 21:5|The plans of the diligent lead to profit; haste leads to poverty."],
    opener="Without looking it up, how much did you spend on food last month? How confident are you?",
    teach=[("A budget is knowing your flocks.",
            "A shepherd who never counted would lose sheep without noticing. Most people lose money the same way. Counting is not a lack of faith; Proverbs calls it wisdom."),
           ("Decide before the month starts.",
            "Jesus assumes a sensible builder counts the cost first. A budget written in advance is a plan. A list of what you already spent is only a report."),
           ("Every dollar gets a job.",
            "Income minus every line should equal zero. Giving and saving are the first lines, because whatever is left to the end usually is not there.",
            "budget"),
           ("The budget serves you.",
            "The first three months will be wrong, and that is normal. Adjust the plan, not the honesty. Couples should write it together; a budget only one spouse knows about is not a shared plan.")],
    skill=("Write next month's budget", "Start with income after tax. Write giving first, then saving, then needs, then wants, until the remainder is zero. Track actual spending for one month in whatever tool you will really use: an app, a spreadsheet or an envelope of cash."),
    discuss=["What comes to mind when you hear the word budget: freedom or restriction? Why?",
             "Which category do you least want to look at?",
             "If you are married, who knows the numbers? Is that working?",
             "What would you do with money you found by tracking?"],
    action=["Write a budget for next month before it starts.", "Track every dollar for 30 days."],
    worksheet=BUDGET,
    guard="Keep the tone practical. Shame makes people stop looking at their numbers, which is the opposite of the goal.",
    objections=[("I do not make enough to budget.", "The less there is, the more each dollar needs a job. Tight margins are where counting pays most."),
                ("Budgets never work for me.", "Usually the first one was abandoned after one bad month. Expect three months of adjusting."),
                ("Is planning this much a lack of trust in God?", "Proverbs praises the planner. Trust shows in how you hold the plan, not in refusing to make one.")],
    prep=["Bring your own budget, or last month's actuals, as a real example.", "Print two budget sheets per person.", "Decide which tracking tools you will mention."],
)

C4 = dict(
    title="Give first",
    big="Giving is the first line in the budget because it is the clearest way a manager acknowledges the owner.",
    scripture=["Proverbs 3:9-10|Honor the Lord with your wealth and with the first of what you produce.",
               "2 Corinthians 9:6-7|Each should give what they have decided in their heart, not reluctantly or under pressure, for God loves a cheerful giver.",
               "Malachi 3:10|Israel is told to bring the whole tithe into the storehouse.",
               "Mark 12:41-44|A widow's two small coins are counted as more than the large gifts of the rich."],
    opener="What is the most generous thing anyone has ever done for you?",
    teach=[("First, not leftover.",
            "Proverbs 3:9 speaks of the first of the harvest. Giving from what is left at the end of the month says the owner gets whatever the manager did not want."),
           ("The tithe is a starting point to learn from, not a law over you.",
            "A tenth was Old Testament law for Israel, and Malachi 3 speaks into that covenant. It is a good and tested practice. The New Testament instruction is to give what you have decided in your heart."),
           ("Decide it, and pray over it.",
            "Decided means on purpose, not by impulse or guilt. If giving has never stretched you, and you have never given a tenth, that is a reason to pray over it more, not a reason to feel safe."),
           ("God measures the heart and the proportion.",
            "The widow gave almost nothing in amount and everything in proportion. The Macedonians gave out of poverty (2 Corinthians 8:1-5). Generosity is not reserved for step 6.")],
    skill=("Make a giving plan", "Write what you gave last month and what share of income it was. Decide a number for next month, where it goes, and the date it leaves your account. Automate it if you can, and review it whenever your income changes."),
    discuss=["Has giving ever cost you something you felt? What happened?",
             "Is your giving decided, or does it depend on how the month went?",
             "What makes giving feel reluctant for you?",
             "How do you hold together giving first and getting out of debt?"],
    action=["Fill in the giving plan.", "Pray over the number every day this week before you settle it."],
    worksheet=GIVING,
    guard="Do not teach Malachi 3:10 as a formula where giving guarantees financial return. Do not use guilt. The position here: Old Testament law, good biblical practice, give what you have decided in your heart, and pray, especially if you have never been stretched.",
    objections=[("Should I give while I am in debt?", "Yes, in this course giving comes first at every step. The amount is between you and God; the habit should not wait."),
                ("Gross or net?", "Scripture does not say. Decide in your heart and be consistent. Do not let the question delay starting."),
                ("Does it all have to go to the church?", "Talk with your pastor. Supporting your local church first and giving beyond it is a common pattern.")],
    prep=["Talk with your pastor about how your church teaches giving.", "Be ready to share, humbly, a time giving stretched you.", "Print handouts."],
)

C5 = dict(
    title="Build margin",
    big="Wise people keep something in store. Margin turns an emergency into an inconvenience and frees you to be generous.",
    scripture=["Proverbs 21:20|The wise store up choice food and oil; fools consume all they have.",
               "Proverbs 6:6-8|The ant stores provisions in summer and gathers at harvest.",
               "Genesis 41:34-36|Joseph stores grain in seven good years to carry Egypt through seven lean ones.",
               "Matthew 6:25-34|Do not worry about tomorrow; your Father knows what you need."],
    opener="What was your last unexpected expense, and how did you pay for it?",
    teach=[("Emergencies are certain. Only the date is unknown.",
            "Cars break, jobs end, people get sick. Joseph did not know which year the famine would start, only that it would. Saving for it is prudence, not pessimism."),
           ("Baby Step 1: $1,000, fast.",
            "The starter emergency fund is small on purpose so you can finish it quickly, often in a month or two. It is the barrier that keeps the next repair or copay from going on a card while you attack your debt.",
            "efund"),
           ("Baby Step 3: three to six months.",
            "Once everything but the house is paid off, build the full emergency fund. Three months of expenses if income is steady and shared, six if it is irregular or you are the only earner."),
           ("Margin is not hoarding.",
            "Jesus tells us not to worry, and the rich fool in Luke 12 is condemned for storing up only for himself. The reserve has a limit and a purpose. Past that limit, money has other jobs.")],
    skill=("Size your emergency fund", "Work out how many months it will take you to save $1,000. Then add up one month of essentials and multiply by three and six: that is your Baby Step 3 target. Keep it in a separate savings account, and set an automatic transfer on payday."),
    discuss=["Would a $1,500 surprise this month go on a card, come from savings, or come from family?",
             "Where is the line between wise saving and hoarding?",
             "How does having margin change your ability to give when a need appears?",
             "What could you cut or sell to reach $1,000 faster?"],
    action=["Open a separate savings account and schedule the first transfer toward $1,000.", "Calculate your one-month number and your three-to-six-month target."],
    worksheet=EFUND,
    guard="Hold Proverbs 21:20 and Matthew 6 together. Saving that comes from wisdom is commended; saving that comes from fear, or has no limit, is what Jesus warns against.",
    objections=[("Isn't saving a lack of faith?", "Proverbs calls it wise and Joseph is praised for it. Faith shows in not trusting the savings."),
                ("Should I save while I have debt at high interest?", "Only the $1,000 starter fund, so the next emergency does not add more debt. The full emergency fund waits until the debt is gone."),
                ("Where should it be kept?", "Somewhere safe and easy to reach, such as a savings account. It is insurance, not an investment.")],
    prep=["Calculate your own one-month number.", "Look up a current savings account APY to mention.", "Print handouts."],
)

C6 = dict(
    title="Get out of debt",
    big="The borrower serves the lender. Baby Step 2 is to pay off everything except the house, smallest balance first.",
    scripture=["Proverbs 22:7|The rich rule over the poor, and the borrower is slave to the lender.",
               "Romans 13:8|Let no debt remain outstanding except the continuing debt to love one another.",
               "Proverbs 22:26-27|Do not put up security for debts; if you cannot pay, your bed will be taken from under you.",
               "Psalm 37:21|The wicked borrow and do not repay, but the righteous give generously."],
    opener="What is the first thing you ever borrowed money for? Would you do it again?",
    teach=[("Scripture warns about debt without forbidding it.",
            "Proverbs 22:7 describes what debt does: it puts someone else in charge of part of your future income. Lending and borrowing appear throughout the Bible, but never as the wise default."),
           ("Baby Step 2: all of it, except the house.",
            "Cards, car loans, student loans, medical bills, personal loans: all of it goes. Debt for something that lasts is different from debt for things already used up, but either way what you have borrowed you repay (Psalm 37:21), and the sooner it is gone the sooner your income is yours to direct."),
           ("Credit cards: paid in full, or not at all.",
            "Dave Ramsey teaches cutting them up, and people do spend more when they pay with a card, so skipping cards is wise. If you use one, the rule is simple: the full statement balance is paid every month. The first month it is not, the card goes in a drawer."),
           ("The debt snowball.",
            "List your debts from the smallest balance to the largest. Pay the minimum on all of them and attack the smallest with every spare dollar. When it is gone, roll its payment into the next one. Each payoff frees more money for the next, and the quick wins keep you going.",
            "snowball")],
    skill=("Build your debt snowball", "List every debt except the house with its balance, APR and minimum payment, smallest balance first. Pay minimums on everything and all extra on the smallest. When it is gone, roll its payment onto the next, and write the date each one is paid off."),
    discuss=["How does owing money affect your freedom to give, change jobs, or say yes to God?",
             "Which would keep you going: quick wins or the lowest total cost?",
             "If you use a credit card, do you spend differently than you would with cash?",
             "Has anyone asked you to co-sign? What does Proverbs 22:26-27 say to that?"],
    action=["Fill in your debt snowball, smallest balance first.", "Find one expense to cut and send that amount to the smallest debt this month."],
    worksheet=DEBT,
    guard="Do not teach that all debt is sin; the text does not say it. Do not shame people in debt. Do be plain that a card balance carried month to month is the line.",
    objections=[("Is a mortgage wrong?", "No. It is the one debt the Baby Steps leave for later, in step 5. Keep it small relative to income and aim to finish it early."),
                ("Isn't paying the highest rate first cheaper?", "On paper, a little. The snowball is what most people actually finish, because the early wins keep them going. The best plan is the one you complete."),
                ("I get rewards on my card.", "Rewards are real only if the balance is paid in full and you are not spending more to get them. Most people spend more.")],
    prep=["Work one snowball example with real-looking numbers.", "Print handouts.", "Have the debt payoff calculator ready on the Tools page."],
)

C7 = dict(
    title="Invest shrewdly",
    big="Think ahead like the shrewd manager, and aim it at what lasts. Small amounts, given time, become large ones.",
    scripture=["Luke 16:1-13|A manager about to lose his job uses his last days to secure his future, and the master commends his shrewdness.",
               "Proverbs 13:11|Dishonest money dwindles, but whoever gathers little by little makes it grow.",
               "Ecclesiastes 11:2|Invest in seven ventures, even eight; you do not know what disaster may come.",
               "Proverbs 28:20|A faithful person will be richly blessed, but one eager to get rich will not go unpunished."],
    opener="If you had started saving $100 a month at 18, what do you think it would be worth today?",
    teach=[("The master praises foresight, not dishonesty.",
            "The manager saw what was coming and acted while he still could. Jesus says people of the world are often sharper about their future than God's people are about theirs. His application (verses 9-13): use worldly wealth for eternal ends, be faithful with little, and do not serve money."),
           ("Little by little is how it grows.",
            "$200 a month from age 22 to 65 at an assumed 7% return grows to about $655,000 from $103,200 of contributions. Start at 32 and it is about $309,000. Ten years of waiting costs more than half.",
            "compound"),
           ("Baby Step 4: invest 15%, and take the match all along.",
            "Once all debt but the house is gone and the full emergency fund is in place, invest 15% of household income for retirement. One note from this course: if your employer matches, take the full match from the start, even during Baby Steps 1 to 3. It is part of your pay.",
            "match"),
           ("Diversify, and distrust anything fast.",
            "Ecclesiastes says to spread it across many ventures because you do not know what is coming. Proverbs 28:20 warns the person in a hurry to get rich. Broad, low-cost, boring and automatic beats clever.")],
    skill=("Check your match and run your numbers", "Find out whether your employer matches and up to what percent. Use the compound growth calculator with your own monthly amount, then run it again starting ten years later. Learn the difference between traditional and Roth accounts from the cheat sheet."),
    discuss=["What does the shrewd manager do that you are not doing?",
             "What are you investing in that will matter in 100 years?",
             "Why is get-rich-quick so attractive? Where have you seen it go wrong?",
             "What is stopping you from starting, or from increasing, this month?"],
    action=["Confirm you are getting the full employer match.", "Run your own numbers in the calculator and write down the cost of waiting."],
    worksheet=INVEST + ACCOUNTS,
    guard="This is the riskiest passage in the course. The parable is not approval of dishonesty and not a proof-text for any investment. Teach verses 9-13 as Jesus' own explanation. Give no specific investment recommendations; this is teaching, not professional advice.",
    objections=[("Is investing just gambling?", "Gambling is a wager on chance. Investing is owning a share of productive businesses over decades. Proverbs praises gathering little by little."),
                ("Should I invest before my debt is gone?", "Take the match, because it is part of your pay. Everything beyond the match waits until Baby Steps 2 and 3 are done: all debt but the house gone, and the full emergency fund in place."),
                ("What about returns? I heard 12%.", "Use a conservative number such as 7%. If the market does better, that is a bonus, not a plan.")],
    prep=["Open the Tools page and practice the calculator.", "Read Luke 16:1-13 in two translations.", "Print handouts with both cheat sheets."],
)

C8 = dict(
    title="Legacy and contentment",
    big="The account outlives you. Leave an inheritance, give generously while you live, and learn the word enough.",
    scripture=["Proverbs 13:22|A good person leaves an inheritance for their children's children.",
               "1 Timothy 6:6-10|Godliness with contentment is great gain; the love of money is a root of all kinds of evil.",
               "1 Timothy 6:17-19|The rich are told not to hope in wealth but to be rich in good deeds, generous and willing to share.",
               "Luke 12:13-21|The rich fool builds bigger barns for himself and is not rich toward God."],
    opener="What did you inherit from your parents or grandparents that was not money?",
    teach=[("Think in generations.",
            "Proverbs 13:22 looks two generations ahead. Most financial decisions look two weeks ahead. An inheritance includes money, and also faith, character and the know-how to handle what is passed on."),
           ("An inheritance can bless or harm.",
            "Proverbs 20:21 warns that an inheritance gained too soon is not blessed at the end. Preparing the heir matters as much as preparing the money. Teach children to work, give and save while they are watching you do it."),
           ("Contentment is the guardrail.",
            "Paul says he learned contentment (Philippians 4:11-13). Without a point called enough, step 6 becomes bigger barns. Decide your enough before you reach it."),
           ("Give while you live.",
            "1 Timothy 6 tells those with wealth to be rich in good deeds now. A will handles what is left; generosity during your life is something you get to see and your family gets to learn from.")],
    skill=("Put your legacy in order", "Work through the checklist: a current will, named beneficiaries on every account, someone who knows where things are, enough insurance for those who depend on you. Then mark which Baby Step you are on and name your next one."),
    discuss=["What do you want your grandchildren to say about how you handled money?",
             "What would be enough for you? Have you ever written the number down?",
             "How do you hold together leaving an inheritance and not building bigger barns?",
             "Which step are you on now, and what is the next one?"],
    action=["Complete the legacy checklist and fix one gap this month.", "Mark your step on the step card and tell one person what your next step is."],
    worksheet=LEGACY + STEP_MARK,
    guard="A proverb describes how life generally goes; it is not a guarantee or a command to die rich. Read Proverbs 13:22 beside Luke 12 and Proverbs 30:8-9 so the session does not drift toward a prosperity message.",
    objections=[("I have nothing to leave.", "Start with what is not money: faith, example, skills. Then a will and beneficiaries, which cost little."),
                ("Shouldn't I give it all away instead?", "Scripture commends both inheritance and radical generosity. Pray over the balance; the rich fool's error was keeping it all for himself."),
                ("Do I need a will if I am young?", "If anyone depends on you, or you own anything, yes. Beneficiary forms take ten minutes.")],
    prep=["Check your own beneficiaries before you teach this.", "Bring the step card for everyone to mark.", "Print handouts."],
)

K2 = dict(
    title="Keep living like a student",
    big="When the first real paycheck arrives, keep spending like you did in college. The gap is your one-time head start.",
    scripture=["Proverbs 21:20|The wise store up; fools consume all they have.",
               "Proverbs 21:5|The plans of the diligent lead to profit; haste leads to poverty.",
               "1 Timothy 6:6-8|Godliness with contentment is great gain; with food and clothing we will be content.",
               "Luke 12:15|Life does not consist in an abundance of possessions."],
    opener="What is the first thing you plan to buy when you get a full-time salary?",
    teach=[("You already know how to live on little.",
            "Right now you live on a fraction of what you will earn. The day you start a salary, your income might triple. If your spending stays near where it is, the difference can fund giving, an emergency fund and debt payoff within a couple of years.",
            "gap"),
           ("Lifestyle creep is the default.",
            "Nobody decides to spend everything. The apartment gets nicer, the car gets newer, the subscriptions stack up, and each one feels earned. Proverbs 21:20 calls consuming all you have foolish, however large the income."),
           ("Contentment is learned early or expensively.",
            "Paul says contentment is great gain. Learning it at 22 on a small budget is far cheaper than learning it at 40 with a mortgage and two car loans."),
           ("Write the budget before the paycheck.",
            "Know your flocks (Proverbs 27:23). Give first, save second, then live on what remains. Your first target is Baby Step 1: $1,000 in a starter emergency fund.")],
    skill=("Write your first-paycheck budget", "Fill in what you spend now in each category. Then fill in the salary column, keeping every spending line as close to today as you can. Whatever is left goes to giving, the $1,000 starter emergency fund and then your loans."),
    discuss=["What part of student life would you be glad to keep for two more years? What part would be hard?",
             "Whose lifestyle are you tempted to match after graduation?",
             "What does enough look like for you at 25?",
             "What would you do with an extra $1,000 a month for two years?"],
    action=["Fill in the first-paycheck budget.", "Open a separate savings account for your $1,000 starter emergency fund."],
    worksheet=FIRST_PAY + EFUND,
    guard="This is wisdom, not a rule that enjoying anything is wrong. The point is the order: give, save, then spend, and do not let the first salary set a lifestyle you then have to feed.",
    objections=[("I have waited four years to stop being broke.", "Two more years of living simply buys decades of margin. And you choose what to loosen first; just choose it on purpose."),
                ("My salary will not be that high.", "Then the gap is smaller and matters more. The habit is the same at any income."),
                ("Isn't saving this much a lack of faith?", "Proverbs calls storing up wise. Faith shows in giving first and not trusting the savings.")],
    prep=["Work out what you spent per month in college versus now, as an honest example.", "Print both worksheets.", "Look up typical rent in your area to make the numbers real."],
)

K3 = dict(
    title="Debt and the fine print",
    big="Borrowing puts someone else in charge of part of your future paychecks. Understand exactly what you are signing, and keep it small.",
    scripture=["Proverbs 22:7|The borrower is slave to the lender.",
               "Luke 14:28-30|Sit down and count the cost before you build.",
               "Romans 13:8|Let no debt remain outstanding.",
               "Proverbs 22:26-27|Do not put up security for another's debts."],
    opener="Do you know your student loan balance and interest rate right now, without checking?",
    teach=[("How a loan really works.",
            "You borrow the principal and pay interest on what you still owe. A longer term lowers the payment and raises the total you pay. The lender is counting on you to look only at the monthly payment, so look at the total."),
           ("APR is what you pay. APY is what you earn.",
            "APR is the yearly rate before compounding, which is how loans are advertised. APY includes compounding, which is how savings are advertised. A card at 24% APR compounding daily really costs about 27% a year.",
            "apr_apy"),
           ("Debt has a time and a place. Keep it minimal.",
            "A reasonable student loan for a degree that raises your income, or a modest mortgage, is different from a car you cannot afford or a vacation on a card. Either way the borrower serves the lender, so borrow little and finish early."),
           ("Credit cards: paid in full every month, or not at all.",
            "Hear the warning first: Dave Ramsey teaches cutting them up, and people spend more with a card than with cash, so the wise default is to skip them. If you use one, pay the full statement balance every month. The first month you cannot, stop using it.")],
    skill=("List what you owe as a debt snowball", "Write down every loan with its balance, APR and minimum payment, and number them from the smallest balance to the largest. That is the debt snowball from Baby Step 2. Use the cheat sheet to check any new loan before you sign."),
    discuss=["What surprised you when you added up what you owe?",
             "How would being debt-free at 27 change what you could say yes to?",
             "Do you spend differently with a card than with cash?",
             "What would you tell a freshman about borrowing?"],
    action=["Log in and write down every loan balance and rate.", "Fill in your debt snowball, smallest balance first."],
    worksheet=APR + DEBT,
    guard="The credit card point is the one most likely to be heard as permission. Say the warning first and louder than the allowance. Do not teach that all debt is sin, and do not shame anyone for loans they already have.",
    objections=[("Don't I need a credit card to build credit?", "A card paid in full every month does build credit. So do on-time rent and loan payments. Credit is a tool for borrowing, so do not go into debt to earn the right to more debt."),
                ("Should I pay loans off fast or invest?", "Take any employer match, because it is part of your pay. Beyond that, Baby Step 2 comes first: clear all debt but the house before investing more."),
                ("Everyone has a car payment.", "Everyone having one is why it feels normal, not why it is wise. Count the total cost, not the payment.")],
    prep=["Work the 24% APR example so you can explain it plainly.", "Print the cheat sheet and payoff plan.", "Open the debt payoff calculator on the Tools page."],
)

K4 = dict(
    title="Small things, long time",
    big="Little things now make a big difference later. Time is the one advantage you have that older people cannot buy.",
    scripture=["Proverbs 13:11|Whoever gathers money little by little makes it grow.",
               "Luke 16:10|Whoever can be trusted with very little can also be trusted with much.",
               "Luke 16:1-13|The shrewd manager acts today because he sees what is coming.",
               "Proverbs 13:22|A good person leaves an inheritance for their children's children."],
    opener="Would you rather have $1 million today, or a penny doubled every day for a month? Why?",
    teach=[("Compound interest is growth on growth.",
            "Your money earns a return, and then the return earns a return. For the first ten years it looks like nothing is happening. The last ten years do most of the work, which is why the early years matter most.",
            "early_late"),
           ("The cost of waiting.",
            "$200 a month from age 22 to 65 at an assumed 7% grows to about $655,000. The same $200 from age 32 grows to about $309,000. Waiting ten years saves you $24,000 in contributions and costs you about $346,000.",
            "compound"),
           ("Take the match, and know your accounts.",
            "If your employer matches contributions, take all of it from your first paycheck; it is part of your pay. Investing 15% is Baby Step 4, after debt and the full emergency fund. A 401(k) comes through your job. A Roth IRA you open yourself, pay tax on now, and withdraw tax-free in retirement, which often suits a first-job income.",
            "match"),
           ("Shrewd for the right reasons.",
            "The shrewd manager is praised for seeing ahead and acting, and Jesus points that foresight at eternity. Faithful with little comes before trusted with much. The goal is not a big number; it is a life that can give freely and leave something for the next generations.")],
    skill=("Run your own numbers", "Open the compound growth calculator. Enter an amount you could really invest each month from your first job. Write down the value at 65, then change the start age by ten years and write that down too. Mark which Baby Step you are on."),
    discuss=["What small habit now would your 60-year-old self thank you for?",
             "What makes it hard to care about something 40 years away?",
             "How could what you build serve other people, not only you?",
             "Which step are you on, and what is your next one?"],
    action=["On your first day at a job with a match, sign up for the full match.", "Write your cost-of-waiting number on the handout and keep it."],
    worksheet=INVEST + ACCOUNTS,
    guard="Do not turn the shrewd manager into an investing proof-text; teach Jesus' own application in verses 9-13. Use a conservative return, and say out loud that returns are not guaranteed. Give no specific investment recommendations.",
    objections=[("I cannot afford to invest yet.", "Start with the match. Then move through Baby Steps 1 to 3 as fast as you can; at 22 that can take months instead of years, and every year you start Baby Step 4 sooner is worth a great deal at 65."),
                ("Isn't it more spiritual not to think about retirement?", "Proverbs commends the ant and the planner. The danger is trusting the savings, not having them."),
                ("What should I invest in?", "This course does not recommend specific investments. Learn what an index fund is, and talk to a qualified advisor for your situation.")],
    prep=["Practice the calculator with three different monthly amounts.", "Check whether your own employer's match details make a good example.", "Print both cheat sheets and the step card."],
)

K1 = dict(C1)
K1.update(
    big="God owns everything you will ever earn. Your job is to manage it faithfully, starting with the small amounts you have now.",
    teach=[C1["teach"][0],
           ("The manager's job is faithfulness, not size.",
            "The servant with two bags hears the same words as the servant with five. A graduate on a $45,000 salary and one on $90,000 are measured the same way: what did you do with what you were handed? The parable does not promise that faithful people get rich. It promises that the master notices."),
           ("Work is the first way you manage.",
            "Colossians 3:23-24 says to work with your whole heart, as working for the Lord. Your skills, degree and health are part of what you were entrusted with, and Deuteronomy 8:17-18 says the ability to earn is itself a gift. The verse is about who you work for, not about working every waking hour."),
           ("Giving shows who you think the owner is.",
            "The tithe is Old Testament law and a good practice to learn from. The New Testament instruction in 2 Corinthians 9:7 is to give what you have decided in your heart, cheerfully. Decide on purpose and pray over the number. If giving has never stretched you, pray over it more. The habit is easiest to start on a small first paycheck, before a lifestyle fills in around it.")],
    scripture=C1["scripture"] + ["Colossians 3:23-24|Work with all your heart, as working for the Lord."],
)

NIGHT = dict(
    title="Entrusted in one night",
    big="God owns it all, we manage it, and He will ask for an account. Here is the whole course in 90 minutes.",
    scripture=["Psalm 24:1|Everything on earth belongs to the Lord.",
               "Matthew 25:14-30|The parable of the talents.",
               "Colossians 3:23-24|Work with all your heart, as working for the Lord.",
               "2 Corinthians 9:7|Give what you have decided in your heart, cheerfully.",
               "Proverbs 22:7|The borrower is slave to the lender.",
               "Luke 16:1-13|The shrewd manager.",
               "Proverbs 13:22|A good person leaves an inheritance for their children's children."],
    opener="What is the best and the worst money decision you have made?",
    teach=[("Owner and manager.",
            "God owns all of it, and a manager is measured on faithfulness, not on the size of what he was handed. The two-bag servant hears the same words as the five-bag servant. The third servant's failure began with a wrong view of the master."),
           ("Work and giving.",
            "Work is done for the Lord, and the ability to earn is a gift. The tithe is Old Testament law and a good practice; the New Testament instruction is to give what you have decided in your heart. If giving has never stretched you, pray over it more."),
           ("The Baby Steps.",
            "This course follows Dave Ramsey's Baby Steps. Read the step card once. Most people are stuck on the first two: $1,000 for a starter emergency fund, and paying off all debt except the house with the debt snowball. Spend the time there, and have each person privately mark the step they are on.",
            "staircase"),
           ("The long view.",
            "The master praises the shrewd manager's foresight, not his dishonesty, and Jesus applies it to using money for what lasts. $200 a month from age 22 reaches about $655,000 by 65 at an assumed 7% return, and about $309,000 if started at 32. Proverbs 13:22 looks two generations ahead; it is wisdom, not a guarantee.",
            "compound")],
    basics=["compound", "rule72", "debt", "apr", "taxes", "match", "stocks"],
    skill=("Find your step", "Mark the Baby Step you are on. Write down the one thing that is stopping the next one. Take the inventory home and fill it in this week."),
    discuss=["Which Baby Step are you on, and what is stopping the next one?",
             "Where do you most naturally think \"this is mine\"?",
             "For couples: do you agree with each other on which step you are on?",
             "What is one thing you will do in the next 30 days?"],
    action=["Fill in the \"What I manage\" inventory at home this week.",
            "Do the one thing you wrote down within 30 days, and tell someone you trust when it is done.",
            "Find out whether your employer matches retirement contributions, and make sure you get all of it."],
    worksheet=STEP_MARK + INVENTORY,
    guard="Do not try to teach all six steps in depth; the conversation is the point. The money basics are headlines, about three minutes each: explain the idea, show the picture, and move on. Give no specific investment recommendations. This version leaves out budgeting mechanics, loan detail and wills. Say so at the end and point people to the site or a longer track.",
    objections=[("That was a lot. Where do I start?", "With the inventory and one step. Nothing else this week."),
                ("We disagree as a couple.", "Normal. Fill in the inventory together before discussing any decision."),
                ("Which fund should I pick in my 401(k)?", "This course does not recommend specific investments. Learn what an index fund and a target-date fund are, compare the fees in your plan, and talk to a qualified advisor about your situation."),
                ("Can we go deeper?", "Yes: the four-week and eight-week tracks cover each piece with its own handout, and the Money Basics page has more on every topic from tonight.")],
    prep=["Read Matthew 25:14-30 and Luke 16:1-13 twice.", "Print a step card and handout for each person, and the scripture handout for anyone who wants to read ahead.",
          "Decide who will read each passage aloud.", "Practice the seven money-basics slides so each one takes about three minutes.",
          "Mark your own step first so you can go first in discussion."],
)

# Practical money basics. Used as slides in One Night and as the Money Basics page.
# Each: title, slide text, one-line takeaway for the handout, more paragraphs for the page, graphic, article links.
BASICS = {
    "compound": dict(
        short="Compound interest",
        title="Compound interest: growth on growth.",
        text="Your money earns a return, and then the return earns a return. Sam puts in $200 a month from 22 to 32, then stops: $24,000 in. Jordan puts in $200 a month from 32 to 65: $79,200 in. At an assumed 7%, Sam has about $346,000 at 65 and Jordan about $309,000. Ten early years beat thirty-three later ones.",
        glance="Growth on growth. Ten early years can beat thirty-three later ones.",
        more=["Nothing about Sam is special except the start date. For the first decade the balance looks like it is barely moving; the curve bends upward late, and it only bends for money that is already in.",
              "The same idea runs in reverse when you borrow, which is why the debt snowball comes before investing in the Baby Steps."],
        graphic="early_late", links=["cfpb_compound", "sec_calc"]),
    "rule72": dict(
        short="Rule of 72",
        title="The rule of 72.",
        text="Divide 72 by the yearly return to see about how many years it takes money to double. At 7%, that is roughly every 10 years. $10,000 at age 22 becomes about $20,000 at 32, $40,000 at 42, $81,000 at 52 and $163,000 at 62, without adding a dollar. The last doubling is worth more than all the ones before it.",
        glance="72 divided by the return is the years to double. At 7%, about 10.",
        more=["It works for debt too. A card at 24% doubles what you owe in about three years if you pay nothing.",
              "The rule is a shortcut, not exact math, and real returns move around from year to year."],
        graphic="doubling", links=["sec_calc"]),
    "debt": dict(
        short="Debt at 24%",
        title="It works against you too.",
        text="On a $5,000 card balance at 24% APR, the first month's interest is $100. Pay $100 a month and the balance never goes down. Pay $200 a month and it is gone in 36 months, after $2,001 in interest. Compound interest is a great servant and a hard master, which is why Baby Step 2 comes before investing.",
        glance="$5,000 at 24% with $100 a month is never paid off. At $200, 36 months.",
        more=["Minimum payments on a card are set so the balance lasts for years. Anything you add above the minimum goes straight to the balance.",
              "Try your own balance in the debt payoff calculator on the Tools page."],
        graphic="debt_trap", links=["cfpb_apr"]),
    "apr": dict(
        short="APR and APY",
        title="APR is what you pay. APY is what you earn.",
        text="APR is the yearly rate on a loan or card, before compounding. APY is the yearly rate on savings, including compounding. A card at 24% APR that compounds daily costs about 27.1% a year. Savings at 4% compounded daily earn a 4.08% APY. When you borrow, compare APRs. When you save, compare APYs.",
        glance="APR is the rate you pay on loans. APY is what you earn on savings.",
        more=["Lenders show you the smaller number and banks advertise the bigger one; both are telling the truth, they are just measuring differently.",
              "On a car loan or mortgage, the APR also includes some fees, so it can be a little higher than the interest rate. Compare APRs between lenders, not monthly payments."],
        graphic="apr_apy", links=["cfpb_apr"]),
    "taxes": dict(
        short="Taxes and brackets",
        title="How income tax brackets work.",
        text="Federal income tax is charged in layers called brackets, and each rate applies only to the slice of income inside its layer. Take a single filer with $60,000 of taxable income and round-number brackets: 10% on the first $12,000, 12% on the next $36,000 and 22% on the last $12,000. That is $8,160 in all, or 13.6% of the $60,000. The 22% is the marginal rate, what the next dollar costs. A raise never makes you take home less.",
        glance="Each rate applies only to its slice of income. A raise never lowers take-home.",
        more=["The numbers above are rounded for teaching. The real brackets, and the standard deduction, change most years, so look up the current ones before you plan.",
              "Taxable income is not your paycheck. Tax is figured on income after deductions. Everyone gets a standard deduction, and money you put into a traditional 401(k) comes off before the bracket math.",
              "Marginal and effective. Your marginal rate is the rate on your last dollar. Your effective rate is total tax divided by total income, and it is always lower. Use the marginal rate to judge a raise, a side job or a traditional-versus-Roth choice, and the effective rate to see what you really pay.",
              "Deduction or credit. A deduction lowers the income that is taxed. A credit lowers the tax itself, dollar for dollar, so a $1,000 credit is worth more than a $1,000 deduction.",
              "Payroll tax is separate. Social Security (6.2%, up to a yearly wage limit) and Medicare (1.45%) come out of each paycheck whatever your bracket, and your employer pays a matching share.",
              "Withholding and refunds. Your employer withholds tax from each paycheck using your Form W-4. A large refund means you lent the government money interest-free, and owing a lot means too little was withheld. Look at your W-4 after a raise, a marriage or a second job.",
              "Traditional or Roth. A traditional account saves tax now, at your marginal rate, and you pay it when you withdraw. A Roth is the other way around. A low rate now, as in a first job, often favors Roth; a high rate now can favor traditional.",
              "Scripture asks for honest taxes. Paul says to give taxes to whom taxes are owed (Romans 13:6-7), and Jesus tells his questioners to give to Caesar what is Caesar's (Matthew 22:21). Using the deductions and credits the law offers is good management. Hiding income is not.",
              "For your own return, use the IRS tools and a tax professional you trust. This course explains how the system works and does not give tax advice."],
        graphic="brackets", links=["irs_brackets"]),
    "match": dict(
        short="401(k) match",
        title="Your 401(k) and the match.",
        text="A 401(k) is a retirement account through your job. Money comes out of each paycheck before you see it and goes into funds you choose from the plan's list. Many employers add a match. For example, on a $50,000 salary you put in 6%, or $3,000 a year, and an employer that matches half of the first 6% adds $1,500. That is an instant 50% return. Ask HR what your match is.",
        glance="Get the full employer match. It is part of your pay.",
        more=["Traditional or Roth. With a traditional 401(k) you skip the income tax now and pay it when you take the money out. With a Roth 401(k) you pay the tax now and qualified withdrawals in retirement are tax-free. Many plans offer both.",
              "Vesting. Some matches become fully yours only after you have worked there a certain number of years. Your own contributions are always yours. Ask HR for the vesting schedule.",
              "IRA. An individual retirement account is one you open yourself, separate from any job. It also comes in traditional and Roth versions.",
              "Limits. The IRS sets yearly contribution limits and changes them most years. For most people they are well above 15% of pay, but look up the current numbers before you plan."],
        graphic="match", links=["sec_401k"]),
    "stocks": dict(
        short="Stocks and index funds",
        title="What the stock market is.",
        text="A share of stock is a small piece of ownership in a company. The stock market is where people buy and sell those pieces, and prices move every day with how the companies are doing and how people feel about them. An index fund owns a small piece of hundreds of companies at once, the kind of spreading out Ecclesiastes 11:2 describes. Any single year can drop sharply, so money you need in the next few years belongs in savings.",
        glance="A share is a piece of a company. An index fund owns pieces of hundreds.",
        more=["Over long stretches, owning productive businesses has grown wealth, with deep drops along the way. Past returns do not guarantee future ones, which is why this course uses a conservative 7% for its examples.",
              "Bonds are loans to a company or government that pay interest. They usually move less than stocks and usually earn less.",
              "Target-date funds are a common 401(k) choice: one fund holding a mix of stocks and bonds that gets more conservative as the year in its name gets closer.",
              "Every fund charges a yearly fee called the expense ratio. A difference of one percentage point a year sounds small and compounds into a large amount over decades, so it is worth comparing.",
              "Never do something with your money that you do not understand. If you cannot explain in a sentence what you own and how it makes money, wait. The prudent think about where their steps lead (Proverbs 14:15).",
              "If you want help, find someone with the heart of a teacher. A good adviser explains what you are buying, what it costs and what could go wrong, and welcomes the same question twice. Be wary of anyone who rushes you, gets vague about fees, or sells you something you cannot explain back."],
        graphic="shares", links=["sec_stocks"]),
}

NEXT_STEPS = [
    ("basics.html", "Money basics", "Everything from tonight's practical section, with a little more on each."),
    ("compound.html", "Compound interest calculator", "Your own numbers, a growth chart and the cost of a purchase."),
    ("scripture-handout.html", "Scripture handout", "Every passage in the course, each linked to the NIV."),
    ("campus.html", "4 Weeks", "For students near graduation and people in their first years of work."),
    ("church.html", "8 Weeks", "One session per skill, for a class or small group of any age."),
]

P45 = [("0-5", "Open", "Ask the opening question. Let three or four people answer."),
       ("5-15", "Read", "Read the passages aloud from people's own Bibles. Ask what stands out."),
       ("15-30", "Teach", "Walk through the four points."),
       ("30-35", "Practical step", "Introduce the worksheet and show one example."),
       ("35-45", "Discuss", "Group questions, then this week's action.")]

P90 = [("0-10", "Open", "Everyone answers the opening question."),
       ("10-25", "Owner and manager", "Read Psalm 24:1 and Matthew 25:14-30 aloud. Ask whose money it is at the start and the end, then teach point 1."),
       ("25-35", "Work and giving", "Colossians 3:23-24 and 2 Corinthians 9:7. Teach point 2."),
       ("35-50", "The Baby Steps", "Hand out the step card. Read it once, then focus on Baby Steps 1 and 2. Everyone marks their step privately."),
       ("50-55", "The long view", "Luke 16:1-13 and Proverbs 13:22. Show the age 22 versus age 32 chart."),
       ("55-78", "Money basics", "Seven short slides: compound interest, the rule of 72, debt, APR and APY, taxes and brackets, the 401(k) match, and the stock market. About three minutes each; take questions at the end."),
       ("78-90", "Discuss and commit", "Group questions, one written action each, prayer.")]

TRACKS = {
    "night": dict(name="One Night", page="one-night.html", length="One 90-minute session",
                  who="A church small group that wants the whole picture in a single evening.",
                  blurb="The whole picture in one evening: whose money it is, the Baby Steps, and a practical section on compound interest, APR and APY, how tax brackets work, the 401(k) match and the stock market. Points to the longer tracks for the how-to.",
                  extra="<b>If you only have 60 minutes:</b> open 5, owner and manager 10, work and giving 5, the Baby Steps 10, the long view and money basics 15, discussion 15.",
                  sessions=[("night", NIGHT, P90)]),
    "campus": dict(name="4 Weeks", page="campus.html", length="Four 45-minute sessions",
                   who="College students close to graduation and people in their first few years of work.",
                   blurb="Keep living like a student, understand loans and rates before you sign, and start investing while time is on your side.",
                   extra="",
                   sessions=[("campus-1", K1, P45), ("campus-2", K2, P45), ("campus-3", K3, P45), ("campus-4", K4, P45)]),
    "church": dict(name="8 Weeks", page="church.html", length="Eight 45-minute sessions",
                   who="A church class or small group semester, any age.",
                   blurb="Two sessions of foundation, five that walk the steps one skill at a time, and a closing session on legacy and contentment.",
                   extra="",
                   sessions=[("church-1", C1, P45), ("church-2", C2, P45), ("church-3", C3, P45), ("church-4", C4, P45),
                             ("church-5", C5, P45), ("church-6", C6, P45), ("church-7", C7, P45), ("church-8", C8, P45)]),
}
