
from typing import Dict, List, Any, Optional
import random
from datetime import datetime
import logging
import re
import asyncio

from core.database import get_collection
from utils.helper import generate_id

logger = logging.getLogger("twitter_agent")

class TwitterAgent:
    """
    Service for automating Twitter posts and engagement
    """
    
    @staticmethod
    async def generate_post_content(project_id: str, topic: str, tone: str = "informative") -> Dict[str, Any]:
        """
        Generate Twitter post content based on project analysis
        
        Args:
            project_id: ID of the analyzed project
            topic: Topic to focus on (tokenomics, team, roadmap, etc)
            tone: Tone of the post (informative, enthusiastic, critical)
            
        Returns:
            Dict with generated content
        """
        # In a real implementation, this would:
        # 1. Retrieve project analysis from the database
        # 2. Use AI to generate content based on the analysis and topic
        # 3. Format the content for Twitter with hashtags, etc.
        
        # Get project data
        projects_collection = get_collection("projects")
        project = await projects_collection.find_one({"id": project_id})
        
        if not project:
            return {"success": False, "message": "Project not found"}
        
        project_name = project["name"]
        
        # Sample hashtags based on topic and project
        hashtags = []
        if "token" in topic.lower() or "tokenomics" in topic.lower():
            hashtags = ["#Tokenomics", "#Crypto", f"#{project_name.replace(' ', '')}", "#Investment"]
        elif "team" in topic.lower():
            hashtags = ["#Team", "#Founders", f"#{project_name.replace(' ', '')}", "#Blockchain"]
        elif "roadmap" in topic.lower():
            hashtags = ["#Roadmap", "#Development", f"#{project_name.replace(' ', '')}", "#Future"]
        else:
            hashtags = [f"#{project_name.replace(' ', '')}", "#Crypto", "#Blockchain", "#Web3"]
        
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
        template = random.choice(content_templates[template_key])
        
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
        
        return {
            "success": True,
            "content": content,
            "hashtags": hashtags,
            "topic": topic,
            "tone": tone
        }
    
    @staticmethod
    async def create_post(user_id: str, content: str, project_id: Optional[str] = None, hashtags: Optional[List[str]] = None, mentions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a Twitter post in the database
        
        Args:
            user_id: User ID creating the post
            content: Post content
            project_id: Optional project ID the post relates to
            hashtags: Optional list of hashtags
            mentions: Optional list of mentions
            
        Returns:
            Dict with created post info
        """
        post_id = generate_id("tweet_")
        
        posts_collection = get_collection("twitter_posts")
        post = {
            "id": post_id,
            "user_id": user_id,
            "project_id": project_id,
            "content": content,
            "hashtags": hashtags or [],
            "mentions": mentions or [],
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await posts_collection.insert_one(post)
        
        return {
            "success": True,
            "post_id": post_id,
            "content": content,
            "status": "draft"
        }
    
    @staticmethod
    async def create_thread(user_id: str, project_id: str, topics: List[str]) -> Dict[str, Any]:
        """
        Create a Twitter thread based on multiple topics
        
        Args:
            user_id: User ID creating the thread
            project_id: Project ID the thread relates to
            topics: List of topics to cover in the thread
            
        Returns:
            Dict with created thread info
        """
        # Get project data
        projects_collection = get_collection("projects")
        project = await projects_collection.find_one({"id": project_id})
        
        if not project:
            return {"success": False, "message": "Project not found"}
        
        project_name = project["name"]
        thread_id = generate_id("thread_")
        
        # Create intro post
        intro_post = {
            "id": generate_id("tweet_"),
            "user_id": user_id,
            "project_id": project_id,
            "content": f"🧵 THREAD: Deep dive on {project_name} - what I found after analyzing this project with @ScryptexAI\n\nKey insights in this thread 👇",
            "hashtags": [f"#{project_name.replace(' ', '')}", "#Crypto", "#Analysis"],
            "mentions": ["@ScryptexAI"],
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Generate a post for each topic
        topic_posts = []
        
        for i, topic in enumerate(topics):
            # Generate content for this topic
            content_result = await TwitterAgent.generate_post_content(project_id, topic)
            
            # Format it as part of a thread
            content = f"{i+1}/ {topic.upper()}:\n\n" + content_result["content"].split("\n\n")[0]
            
            topic_posts.append({
                "id": generate_id("tweet_"),
                "user_id": user_id,
                "project_id": project_id,
                "content": content,
                "hashtags": content_result["hashtags"],
                "mentions": [],
                "status": "draft",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
        
        # Create conclusion post
        conclusion_post = {
            "id": generate_id("tweet_"),
            "user_id": user_id,
            "project_id": project_id,
            "content": f"CONCLUSION:\n\n{project_name} shows potential based on my analysis. The strongest areas are {topics[0] if topics else 'fundamentals'} and {topics[1] if len(topics) > 1 else 'community'}.\n\nWill continue monitoring this project. What do you think?\n\n#DYOR #NotFinancialAdvice",
            "hashtags": [f"#{project_name.replace(' ', '')}", "#DYOR", "#NotFinancialAdvice"],
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
            "user_id": user_id,
            "project_id": project_id,
            "posts": all_posts,
            "status": "draft",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await threads_collection.insert_one(thread)
        
        return {
            "success": True,
            "thread_id": thread_id,
            "post_count": len(all_posts),
            "topics": topics,
            "status": "draft"
        }
    
    @staticmethod
    async def post_to_twitter(post_id: str) -> Dict[str, Any]:
        """
        Post to Twitter (simulated)
        
        Args:
            post_id: ID of the post to publish
            
        Returns:
            Dict with post result
        """
        # In a real implementation, this would:
        # 1. Get the post content from the database
        # 2. Connect to Twitter API using the user's credentials
        # 3. Post the content and handle responses/errors
        
        # Simulate posting to Twitter
        await asyncio.sleep(random.uniform(1.0, 2.0))
        
        # Get post
        posts_collection = get_collection("twitter_posts")
        post = await posts_collection.find_one({"id": post_id})
        
        if not post:
            return {"success": False, "message": "Post not found"}
        
        # Generate fake tweet ID
        tweet_id = "".join(random.choice("0123456789") for _ in range(19))
        
        # Update post status
        await posts_collection.update_one(
            {"id": post_id},
            {"$set": {
                "status": "posted",
                "tweet_id": tweet_id,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Posted to Twitter successfully",
            "tweet_id": tweet_id
        }
    
    @staticmethod
    async def post_thread_to_twitter(thread_id: str) -> Dict[str, Any]:
        """
        Post a thread to Twitter (simulated)
        
        Args:
            thread_id: ID of the thread to publish
            
        Returns:
            Dict with thread posting result
        """
        # Get thread
        threads_collection = get_collection("twitter_threads")
        thread = await threads_collection.find_one({"id": thread_id})
        
        if not thread:
            return {"success": False, "message": "Thread not found"}
        
        # Post each tweet in the thread
        posts_collection = get_collection("twitter_posts")
        previous_tweet_id = None
        
        for post in thread["posts"]:
            # Simulate posting to Twitter with a delay between posts
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Generate fake tweet ID
            tweet_id = "".join(random.choice("0123456789") for _ in range(19))
            
            # Update post status
            await posts_collection.update_one(
                {"id": post["id"]},
                {"$set": {
                    "status": "posted",
                    "tweet_id": tweet_id,
                    "in_reply_to": previous_tweet_id,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            # Set this tweet as the parent for the next one
            previous_tweet_id = tweet_id
        
        # Update thread status
        await threads_collection.update_one(
            {"id": thread_id},
            {"$set": {
                "status": "posted",
                "updated_at": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "Thread posted to Twitter successfully",
            "post_count": len(thread["posts"])
        }
    
    @staticmethod
    async def analyze_engagement(user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Analyze Twitter engagement statistics (simulated)
        
        Args:
            user_id: User ID to analyze
            days: Number of days to analyze
            
        Returns:
            Dict with engagement statistics
        """
        # In a real implementation, this would:
        # 1. Fetch the user's Twitter posts from the database
        # 2. Call Twitter API to get engagement metrics
        # 3. Aggregate and analyze the data
        
        # Get user's Twitter posts
        posts_collection = get_collection("twitter_posts")
        
        # Calculate date threshold
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        posts_cursor = posts_collection.find({
            "user_id": user_id,
            "status": "posted",
            "created_at": {"$gte": cutoff_date}
        })
        
        # Simulate engagement metrics
        posts_count = 0
        total_likes = 0
        total_retweets = 0
        total_comments = 0
        
        async for post in posts_cursor:
            posts_count += 1
            
            # Generate random engagement numbers
            likes = random.randint(5, 50)
            retweets = random.randint(1, 15)
            comments = random.randint(0, 10)
            
            total_likes += likes
            total_retweets += retweets
            total_comments += comments
        
        # Calculate averages
        avg_likes = total_likes / posts_count if posts_count > 0 else 0
        avg_retweets = total_retweets / posts_count if posts_count > 0 else 0
        avg_comments = total_comments / posts_count if posts_count > 0 else 0
        
        return {
            "success": True,
            "period_days": days,
            "posts_count": posts_count,
            "total_engagement": {
                "likes": total_likes,
                "retweets": total_retweets,
                "comments": total_comments
            },
            "average_engagement": {
                "likes": avg_likes,
                "retweets": avg_retweets,
                "comments": avg_comments
            }
        }
