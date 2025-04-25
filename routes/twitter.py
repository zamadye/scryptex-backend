from fastapi import APIRouter, HTTPException, Path, Query, Depends, status
from typing import List, Optional
from datetime import datetime, timedelta

from models.twitter import TwitterPost, TwitterThread, TwitterAccount
from models.user import User
from utils.helper import generate_response, generate_id
from utils.jwt import get_current_user
from core.database import get_collection
from utils.logger import setup_logger, log_request

router = APIRouter(prefix="/twitter")
logger = setup_logger("twitter")

@router.post("/post", response_model=dict)
async def create_twitter_post(
    project_id: str = Query(..., description="Project ID to create content about"),
    topic: str = Query(..., description="Topic focus (tokenomics, team, roadmap, etc)"),
    tone: str = Query("informative", description="Tone of the post (informative, enthusiastic, critical)"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and queue a Twitter post based on project analysis
    """
    # Log request
    log_request(logger, {
        "project_id": project_id,
        "topic": topic,
        "tone": tone
    }, current_user.id)
    
    # Check if project exists
    projects_collection = get_collection("projects")
    project = await projects_collection.find_one({"id": project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Check if user has enough credits
    credit_collection = get_collection("credit_balances")
    credit_balance = await credit_collection.find_one({"user_id": current_user.id})
    
    if not credit_balance or credit_balance["balance"] < 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits to create Twitter post"
        )
    
    # Deduct credits (1 credit for Twitter post)
    await credit_collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "balance": credit_balance["balance"] - 1,
            "lifetime_spent": credit_balance["lifetime_spent"] + 1,
            "last_updated": datetime.utcnow()
        }}
    )
    
    # Log credit usage
    logs_collection = get_collection("credit_logs")
    credit_log = {
        "user_id": current_user.id,
        "action": "use",
        "amount": 1.0,
        "description": f"Twitter post about {project['name']} ({topic})",
        "related_entity": project_id,
        "created_at": datetime.utcnow()
    }
    await logs_collection.insert_one(credit_log)
    
    # Generate tweet content based on project and topic
    # In a real implementation, this would use AI to generate content based on project analysis
    
    # Sample hashtags based on topic and project
    hashtags = []
    if "token" in topic.lower() or "tokenomics" in topic.lower():
        hashtags = ["#Tokenomics", "#Crypto", f"#{project['name'].replace(' ', '')}", "#Investment"]
    elif "team" in topic.lower():
        hashtags = ["#Team", "#Founders", f"#{project['name'].replace(' ', '')}", "#Blockchain"]
    elif "roadmap" in topic.lower():
        hashtags = ["#Roadmap", "#Development", f"#{project['name'].replace(' ', '')}", "#Future"]
    else:
        hashtags = [f"#{project['name'].replace(' ', '')}", "#Crypto", "#Blockchain", "#Web3"]
    
    # Sample content based on topic
    content_templates = {
        "tokenomics": [
            "Just analyzed {project}'s tokenomics. The distribution looks {sentiment} with {details}.",
            "Looking at {project}'s token model - {details}. What do you think about this approach?",
            "{project}'s tokenomics breakdown: {details}. This could be {sentiment} for early adopters."
        ],
        "team": [
            "Checked out the team behind {project}. {details} - looks {sentiment}!",
            "{project}'s founding team has {details}. This background is {sentiment} for the project's future.",
            "Team analysis of {project}: {details}. Their experience is {sentiment}."
        ],
        "roadmap": [
            "{project}'s roadmap reveals {details}. The timeline seems {sentiment}.",
            "Just reviewed {project}'s development plan. {details} - {sentiment} outlook overall.",
            "The roadmap for {project} shows {details}. I'm {sentiment} about their execution so far."
        ],
        "general": [
            "Analyzing {project} with AI tools. Initial findings: {details}. Looking {sentiment} overall!",
            "Deep dive into {project}: {details}. The project seems {sentiment} compared to competitors.",
            "Using Scryptex to analyze {project}. {details} - {sentiment} signals for potential growth."
        ]
    }
    
    # Determine which template set to use
    template_key = "general"
    for key in content_templates.keys():
        if key in topic.lower():
            template_key = key
            break
    
    # Select a random template
    import random
    template = random.choice(content_templates[template_key])
    
    # Fill in template with project info
    # In a real implementation, these would be actual insights from the analysis
    project_name = project["name"]
    
    # Sentiment based on tone
    sentiment_options = {
        "informative": ["interesting", "noteworthy", "significant"],
        "enthusiastic": ["promising", "exciting", "impressive"],
        "critical": ["concerning", "questionable", "risky"]
    }
    sentiment = random.choice(sentiment_options.get(tone, sentiment_options["informative"]))
    
    # Details based on topic
    details_options = {
        "tokenomics": [
            "25% allocated to the team with 2-year vesting",
            "10% community rewards and 15% ecosystem development",
            "unique burn mechanism that reduces supply over time"
        ],
        "team": [
            "founders from top tech companies",
            "strong technical background but limited blockchain experience",
            "impressive advisory board including industry veterans"
        ],
        "roadmap": [
            "mainnet launch in Q3 and partnership announcements",
            "ambitious timeline but clear milestones",
            "focus on scaling solutions before marketing"
        ],
        "general": [
            "solid fundamentals and clear use case",
            "innovative approach to solving scalability",
            "growing community engagement metrics"
        ]
    }
    
    details = random.choice(details_options.get(template_key, details_options["general"]))
    
    # Generate content
    content = template.format(
        project=project_name,
        sentiment=sentiment,
        details=details
    )
    
    # Add hashtags
    hashtag_string = " ".join(hashtags)
    content = f"{content}\n\n{hashtag_string}"
    
    # Create Twitter post
    posts_collection = get_collection("twitter_posts")
    post_id = generate_id("tweet_")
    
    post = {
        "id": post_id,
        "user_id": current_user.id,
        "project_id": project_id,
        "content": content,
        "hashtags": hashtags,
        "mentions": [],
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await posts_collection.insert_one(post)
    
    # Log to general logs
    logs_general = get_collection("logs")
    await logs_general.insert_one({
        "user_id": current_user.id,
        "action": "twitter_post_create",
        "metadata": {
            "post_id": post_id,
            "project_id": project_id,
            "topic": topic
        },
        "timestamp": datetime.utcnow()
    })
    
    return generate_response(
        data={
            "post_id": post_id,
            "content": content,
            "status": "draft"
        },
        message="Twitter post generated successfully"
    )

@router.post("/thread", response_model=dict)
async def create_twitter_thread(
    project_id: str = Query(..., description="Project ID to create content about"),
    topics: List[str] = Query(..., description="List of topics to cover in thread"),
    current_user: User = Depends(get_current_user)
):
    """
    Generate and queue a Twitter thread based on project analysis
    """
    # Log request
    log_request(logger, {
        "project_id": project_id,
        "topics": topics
    }, current_user.id)
    
    # Check if project exists
    projects_collection = get_collection("projects")
    project = await projects_collection.find_one({"id": project_id})
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Check if user has enough credits (2 credits for a thread)
    credit_collection = get_collection("credit_balances")
    credit_balance = await credit_collection.find_one({"user_id": current_user.id})
    
    if not credit_balance or credit_balance["balance"] < 2:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits to create Twitter thread (requires 2 credits)"
        )
    
    # Deduct credits
    await credit_collection.update_one(
        {"user_id": current_user.id},
        {"$set": {
            "balance": credit_balance["balance"] - 2,
            "lifetime_spent": credit_balance["lifetime_spent"] + 2,
            "last_updated": datetime.utcnow()
        }}
    )
    
    # Log credit usage
    logs_collection = get_collection("credit_logs")
    credit_log = {
        "user_id": current_user.id,
        "action": "use",
        "amount": 2.0,
        "description": f"Twitter thread about {project['name']}",
        "related_entity": project_id,
        "created_at": datetime.utcnow()
    }
    await logs_collection.insert_one(credit_log)
    
    # Create thread and initial post
    thread_id = generate_id("thread_")
    
    # Generate initial post and thread posts
    # In a real implementation, this would use AI to generate relevant content
    
    # Create intro post
    intro_post = {
        "id": generate_id("tweet_"),
        "user_id": current_user.id,
        "project_id": project_id,
        "content": f"🧵 THREAD: Deep dive on {project['name']} - what I found after analyzing this project with @ScryptexAI\n\nKey insights in this thread 👇",
        "hashtags": [f"#{project['name'].replace(' ', '')}", "#Crypto", "#Analysis"],
        "mentions": ["@ScryptexAI"],
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Create posts for each topic
    topic_posts = []
    topic_templates = {
        "tokenomics": "1/ TOKENOMICS:\n\n{project}'s token distribution: 40% public sale, 20% team (2yr vesting), 25% ecosystem, 15% reserves.\n\nThis allocation is balanced compared to other projects. Team vesting is a good sign. 📊",
        "team": "2/ TEAM:\n\n{project} was founded by experienced devs from {companies}. The CTO previously built {previous}.\n\nKey advisors include veterans from the blockchain space, bringing credibility. 👥",
        "roadmap": "3/ ROADMAP:\n\n{project} plans to launch mainnet in Q3, followed by ecosystem expansion.\n\nCompared to competitors, their timeline is aggressive but achievable based on their development pace. 🗓️",
        "investors": "4/ INVESTORS:\n\n{project} is backed by notable VCs including {investors}.\n\nThis level of institutional backing provides runway and connections for growth. 💰",
        "technology": "5/ TECHNOLOGY:\n\n{project} is built on {tech} with {innovations}.\n\nTheir approach to solving {problem} is novel and could lead to significant adoption if executed well. ⚙️"
    }
    
    import random
    
    # Sample companies, previous projects, and investors for template filling
    companies_list = ["Google", "Meta", "ConsenSys", "Solana Labs", "Binance", "Coinbase"]
    previous_list = ["a DeFi protocol with $500M TVL", "a popular NFT marketplace", "scaling solutions for Ethereum", "a top 50 blockchain"]
    investors_list = ["Andreessen Horowitz", "Sequoia Capital", "Paradigm", "Polychain Capital", "Dragonfly Capital", "Binance Labs"]
    tech_list = ["Ethereum", "Solana", "Polkadot", "Cosmos", "zkSync"]
    innovations_list = ["zero-knowledge proofs", "a novel consensus mechanism", "optimistic rollups", "sharding technology"]
    problem_list = ["scalability", "security", "interoperability", "user experience"]
    
    for i, topic in enumerate(topics):
        template_key = next((k for k in topic_templates.keys() if k in topic.lower()), "general")
        
        if template_key in topic_templates:
            content = topic_templates[template_key].format(
                project=project['name'],
                companies=", ".join(random.sample(companies_list, 2)),
                previous=random.choice(previous_list),
                investors=", ".join(random.sample(investors_list, 2)),
                tech=random.choice(tech_list),
                innovations=random.choice(innovations_list),
                problem=random.choice(problem_list)
            )
        else:
            # Default template for topics not in the predefined list
            content = f"{i+1}/ {topic.upper()}:\n\n{project['name']} shows promising signs in this area. Further analysis suggests positive momentum compared to other projects in the space."
        
        topic_posts.append({
            "id": generate_id("tweet_"),
            "user_id": current_user.id,
            "project_id": project_id,
            "content": content,
            "hashtags": [f"#{project['name'].replace(' ', '')}", "#Analysis"],
            "mentions": [],
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
    
    # Create concluding post
    conclusion_post = {
        "id": generate_id("tweet_"),
        "user_id": current_user.id,
        "project_id": project_id,
        "content": f"CONCLUSION:\n\n{project['name']} shows potential based on my analysis. The strongest areas are {random.choice(topics)} and {random.choice(topics)}.\n\nWill continue monitoring this project. What do you think?\n\n#DYOR #NotFinancialAdvice",
        "hashtags": [f"#{project['name'].replace(' ', '')}", "#DYOR", "#NotFinancialAdvice"],
        "mentions": [],
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Combine all posts
    all_posts = [intro_post] + topic_posts + [conclusion_post]
    
    # Save all posts to database
    posts_collection = get_collection("twitter_posts")
    await posts_collection.insert_many(all_posts)
    
    # Create thread
    threads_collection = get_collection("twitter_threads")
    thread = {
        "id": thread_id,
        "user_id": current_user.id,
        "project_id": project_id,
        "posts": all_posts,
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await threads_collection.insert_one(thread)
    
    # Log to general logs
    logs_general = get_collection("logs")
    await logs_general.insert_one({
        "user_id": current_user.id,
        "action": "twitter_thread_create",
        "metadata": {
            "thread_id": thread_id,
            "project_id": project_id,
            "topics": topics
        },
        "timestamp": datetime.utcnow()
    })
    
    return generate_response(
        data={
            "thread_id": thread_id,
            "post_count": len(all_posts),
            "topics": topics,
            "status": "draft"
        },
        message="Twitter thread generated successfully"
    )

@router.get("/posts", response_model=dict)
async def get_user_twitter_posts(
    current_user: User = Depends(get_current_user)
):
    """
    Get all Twitter posts for the current user
    """
    posts_collection = get_collection("twitter_posts")
    
    posts_cursor = posts_collection.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1)
    
    posts = []
    async for post in posts_cursor:
        posts.append({
            "id": post["id"],
            "content": post["content"],
            "hashtags": post["hashtags"],
            "mentions": post["mentions"],
            "status": post["status"],
            "created_at": post["created_at"].isoformat(),
            "tweet_id": post.get("tweet_id")
        })
    
    return generate_response(
        data=posts,
        message="Twitter posts retrieved successfully"
    )

@router.get("/threads", response_model=dict)
async def get_user_twitter_threads(
    current_user: User = Depends(get_current_user)
):
    """
    Get all Twitter threads for the current user
    """
    threads_collection = get_collection("twitter_threads")
    
    threads_cursor = threads_collection.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1)
    
    threads = []
    async for thread in threads_cursor:
        # Get first post content as preview
        preview = thread["posts"][0]["content"] if thread["posts"] else "Empty thread"
        
        threads.append({
            "id": thread["id"],
            "post_count": len(thread["posts"]),
            "preview": preview,
            "status": thread["status"],
            "created_at": thread["created_at"].isoformat()
        })
    
    return generate_response(
        data=threads,
        message="Twitter threads retrieved successfully"
    )

@router.post("/connect", response_model=dict)
async def connect_twitter_account(
    twitter_handle: str = Query(..., description="Twitter handle to connect"),
    current_user: User = Depends(get_current_user)
):
    """
    Connect a Twitter account to the user's profile
    """
    # In a real implementation, this would use OAuth to authenticate with Twitter
    
    # Log request
    log_request(logger, {"twitter_handle": twitter_handle}, current_user.id)
    
    # Check if account already exists
    accounts_collection = get_collection("twitter_accounts")
    existing_account = await accounts_collection.find_one({"user_id": current_user.id})
    
    if existing_account:
        # Update existing account
        await accounts_collection.update_one(
            {"user_id": current_user.id},
            {"$set": {
                "twitter_handle": twitter_handle,
                "is_connected": True,
                "connected_at": datetime.utcnow(),
                "last_used": datetime.utcnow()
            }}
        )
    else:
        # Create new account
        account = {
            "user_id": current_user.id,
            "twitter_handle": twitter_handle,
            "is_connected": True,
            "connected_at": datetime.utcnow(),
            "last_used": datetime.utcnow()
        }
        
        await accounts_collection.insert_one(account)
    
    return generate_response(
        data={
            "twitter_handle": twitter_handle,
            "is_connected": True
        },
        message="Twitter account connected successfully"
    )
