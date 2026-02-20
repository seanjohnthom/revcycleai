# Axlow LinkedIn Autopilot — Setup & Deployment Guide

## 🎯 Overview

This system automates LinkedIn content creation for Axlow using:
- **Claude AI** (Anthropic) for content generation
- **Canva** (optional) for image creation
- **Buffer/Hootsuite** (optional) for scheduling
- **Python** for orchestration

**Time commitment:**
- Initial setup: 2-3 hours
- Monthly maintenance: 30 minutes (review calendar)
- Weekly engagement: 15 minutes (monitor comments)

---

## 📋 Prerequisites

### Required
- ✅ Python 3.8+ installed
- ✅ Anthropic API key (Claude)
- ✅ LinkedIn company page or personal profile
- ✅ Canva Pro account (for branded templates)

### Optional (for full automation)
- Buffer or Hootsuite account (for scheduling)
- Canva API access (for programmatic image generation)

---

## 🚀 Step-by-Step Setup

### Step 1: Install Python Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv axlow-env
source axlow-env/bin/activate  # On Windows: axlow-env\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

**What's in `requirements.txt`:**
```
anthropic>=0.18.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

### Step 2: Set Up API Keys

Create a `.env` file in the project directory:

```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
CANVA_API_KEY=your-canva-api-key  # Optional
BUFFER_API_KEY=your-buffer-api-key  # Optional
LINKEDIN_PROFILE_ID=axlow  # Your LinkedIn page/profile ID
```

**Where to get API keys:**

1. **Anthropic API Key:**
   - Sign up at console.anthropic.com
   - Create a new API key
   - Cost: ~$0.50-$2 per month for content generation

2. **Canva API Key (Optional):**
   - Requires Canva Enterprise plan
   - Apply at canva.com/developers

3. **Buffer API Key (Optional):**
   - Sign up at buffer.com
   - Go to Apps → Create New App
   - Generate access token

---

### Step 3: Create Canva Templates

Follow the instructions in `CANVA_TEMPLATES.md`:

1. Log in to Canva Pro
2. Create Brand Kit with Axlow colors + logo
3. Create these 5 templates:
   - Stat Card (1200x1200px)
   - Before/After Split (1200x1200px)
   - Quote Card (1200x1200px)
   - Data Visualization (1200x1200px)
   - Tip Card/Listicle (1200x1200px)
4. Save each as a template in your Canva account

**Pro tip:** You can hire a designer on Fiverr to create these templates for ~$50-100 if you're not familiar with Canva.

---

### Step 4: Test the System

Run the script to verify setup:

```bash
python axlow_autopilot.py
```

You should see the CLI menu:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 AXLOW LINKEDIN AUTOPILOT v2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AVAILABLE COMMANDS:

1. Generate monthly calendar
2. Generate single post
3. Monitor engagement
4. Generate engagement report
5. Exit
```

**Test with a single post:**
1. Select option `2` (Generate single post)
2. Choose a pillar and format
3. Verify the output file is created in `generated_content/`

---

### Step 5: Generate Your First Monthly Calendar

```bash
# From the CLI menu, select option 1
# Enter month: March
# Enter year: 2026
```

This will:
- Call Claude API to generate 16 posts
- Save raw content to `generated_content/March_2026_raw_content.txt`
- Save structured calendar to `calendars/March_2026_calendar.json`

**Review the output:**
- Open the raw content file
- Check that posts follow brand guidelines
- Flag any posts that need human review (compliance)

---

### Step 6: Create Images

For each post that requires an image:

1. Open the `generated_content/March_2026_raw_content.txt` file
2. Find the "IMAGE BRIEF" section for that post
3. Go to Canva and duplicate the appropriate template
4. Populate the template with text from the image brief
5. Export as PNG (1200x1200 or 1080x1350 depending on format)
6. Save to `generated_content/images/` folder

**Example workflow:**

```
IMAGE BRIEF:
Template: Stat Card
Stat: 30 min → 20 sec
Supporting text: Average payor policy search time before/after Axlow
Background: Deep Teal
```

→ Duplicate "Stat Card" Canva template  
→ Replace `[STAT]` with "30 min → 20 sec"  
→ Replace `[SUPPORTING_TEXT]` with "Average payor policy..."  
→ Export as `post_1_stat_card.png`

---

### Step 7: Schedule Posts

#### Option A: Manual Scheduling (Recommended to start)

1. Go to Buffer.com or Hootsuite
2. Create a new post for LinkedIn
3. Copy/paste the post copy from the generated content
4. Attach the image (if applicable)
5. Set publish date/time from the calendar
6. Repeat for all 16 posts

**Pro tip:** Block 30 minutes to load all posts at once at the start of the month.

---

#### Option B: Automated Scheduling (Advanced)

If you have Buffer API access:

```python
# This requires implementing the schedule_post() function
# Currently a placeholder in the script

from axlow_autopilot import AxlowAutopilot

autopilot = AxlowAutopilot()
calendar = autopilot.generate_monthly_calendar("March", 2026)

# Automatically schedule all posts
for post in calendar.posts:
    autopilot.schedule_post(post)
```

---

### Step 8: Monitor & Engage

**Daily (5 minutes):**
- Check LinkedIn notifications for comments
- Reply to questions using suggested reply templates from the calendar

**Weekly (15 minutes):**
- Review engagement metrics in LinkedIn analytics
- Note top/bottom performing posts
- Reply to any flagged comments

**Monthly (30 minutes):**
- Generate engagement report
- Review next month's calendar before scheduling
- Update strategy based on performance

---

## 📊 Ongoing Workflow

### Monthly Cycle

**Week 1 of the month:**
1. Run `python axlow_autopilot.py`
2. Select "Generate monthly calendar"
3. Review generated posts (30 min)
4. Flag posts needing compliance review
5. Create images in Canva (60 min)
6. Load into Buffer/Hootsuite (30 min)

**Weeks 2-4:**
- Monitor engagement (15 min/week)
- Reply to comments (10 min/day)
- Watch for crisis/breaking news (requires reactive content)

**End of month:**
- Generate engagement report
- Analyze top/bottom posts
- Update content strategy if needed

---

## 🔧 Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"

**Fix:** Create a `.env` file with your API key (see Step 2)

---

### Generated content doesn't match brand voice

**Fix:**
- Open `SYSTEM_PROMPT_V2.md`
- Review the brand voice section
- Ensure the system prompt file is in the same directory as the script
- Re-run generation

---

### Images don't look professional

**Fix:**
- Review `CANVA_TEMPLATES.md` specs
- Ensure you're using Axlow brand colors exactly (#1D4740, #E8F4F0, etc.)
- Keep whitespace generous (content ≤40% of canvas)
- Use Inter or Helvetica Neue fonts only
- Simplify — less is more

---

### Posts aren't getting engagement

**Fix:**
- Review the A/B testing framework in `SYSTEM_PROMPT_V2.md`
- Try different hook styles
- Test shorter vs. longer posts
- Increase pain point / relatable content
- Respond to every comment to boost algorithm

---

## 🚨 Emergency Protocols

### If Axlow has a service outage or major bug:

1. **IMMEDIATELY PAUSE** all scheduled content
   - Go to Buffer/Hootsuite and delete queued posts
2. Alert the team
3. Do NOT publish new content until issue is resolved
4. Draft a holding statement if needed

---

### If a post gets negative feedback:

1. Don't delete the post (looks defensive)
2. Respond professionally: "Thanks for the feedback. We're looking into this."
3. Flag for human escalation
4. Review accuracy of the claim
5. Post a correction if needed

---

## 💡 Pro Tips

1. **Start manual, automate gradually**
   - Month 1-2: Generate content, create images manually, load into Buffer manually
   - Month 3+: Add Canva API automation
   - Month 6+: Add scheduling automation

2. **Build a content library**
   - Save high-performing posts for recycling after 90 days
   - Keep a swipe file of great hooks
   - Track which topics get the most engagement

3. **Engage authentically**
   - Reply to EVERY comment (even just "Thanks! 🙏")
   - Ask follow-up questions to keep threads alive
   - Tag people who share your content

4. **Quality over quantity**
   - Better to publish 4 great posts per week than 10 mediocre ones
   - If a generated post feels off, rewrite it
   - Don't be afraid to scrap a post and generate a replacement

5. **Monitor competitors**
   - See what Availity, Change Healthcare, Waystar are posting
   - Learn from their wins (and avoid their mistakes)
   - Differentiate Axlow's voice

---

## 📈 Success Metrics

Track these monthly:

| Metric | Target |
|--------|--------|
| **Engagement Rate** | >3% (good), >5% (excellent) |
| **Click-Through Rate** | >0.5% (good), >1% (excellent) |
| **Follower Growth** | +2% per month |
| **Post Frequency** | 4 posts/week (16/month) |
| **Comment Response Time** | <4 hours |

**What "good" looks like after 3 months:**
- 500+ followers (if starting from scratch)
- 50-100 engagements per post
- 5-10 clicks to axlow.com per post
- 2-3 substantive comments per post (not just emoji reactions)

---

## 🎓 Learning Resources

**LinkedIn B2B Best Practices:**
- "LinkedIn for B2B: The Ultimate Guide" — HubSpot
- "How to Write LinkedIn Posts That Get 1M+ Views" — Justin Welsh
- Search "RCM LinkedIn" to see what top RCM influencers post

**Content Strategy:**
- "Everybody Writes" by Ann Handley
- "Building a StoryBrand" by Donald Miller
- "Obviously Awesome" by April Dunford (for positioning)

**Healthcare RCM:**
- Follow HFMA (Healthcare Financial Management Association)
- Subscribe to RCM newsletters (MGMA, Advisory Board)
- Monitor CMS.gov for policy updates

---

## 🆘 Need Help?

**Common questions:**

Q: How much does this cost to run per month?  
A: ~$2-5 for Claude API calls + $12/mo for Buffer (if used) = ~$15-20/mo total

Q: Can I use this for multiple brands?  
A: Yes! Just create a separate system prompt and calendar for each brand

Q: What if I don't have Canva Pro?  
A: You can create images in free tools (Figma, Photoshop, etc.) using the template specs

Q: How long does it take to generate a month's content?  
A: 5-10 minutes for AI generation + 60-90 minutes for image creation

Q: Can I customize the system prompt?  
A: Absolutely! Edit `SYSTEM_PROMPT_V2.md` to fit your exact brand voice

---

## 🚀 Next Steps

1. ✅ Complete setup (Steps 1-4)
2. ✅ Generate first monthly calendar
3. ✅ Review and approve posts
4. ✅ Create images
5. ✅ Schedule in Buffer
6. ✅ Monitor engagement
7. ✅ Iterate and improve

**Ready to go? Run:**

```bash
python axlow_autopilot.py
```

Good luck! 🎉
