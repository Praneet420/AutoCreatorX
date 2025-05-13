# -*- coding: utf-8 -*-
"""
AutoCreatorX: Automated Content Creation and Publishing System

This script defines the core components of AutoCreatorX, a sophisticated system
designed for automated generation, production, and distribution of video content
across various social media platforms. It leverages AI for trend analysis,
scriptwriting, media generation, and learns from performance feedback.

Key Features:
- Modular design for extensibility and maintainability.
- Centralized configuration management for easy customization.
- Comprehensive logging for monitoring and debugging.
- Robust error handling and retry mechanisms.
- Anti-detection measures for platform interactions.
- Monetization strategy integration.
- Feedback loop for continuous improvement.

USER NOTE:
This system is complex, but many aspects can be controlled through the
'AutoCreatorXConfig' class or a 'autocreatorx_config.yaml' file if you
create one. This configuration allows you to define things like:
- Which topics to focus on (niche_focus_keywords).
- Which topics to avoid (exclude_topics_containing).
- Which platforms to publish to (e.g., YouTube, TikTok).
- Whether certain features are enabled or disabled.

Look for 'USER NOTE:' comments within the code and especially in the
'AutoCreatorXConfig' class for guidance on what different settings do and
which ones are generally safe for you to modify to tailor the system's output.
For more advanced changes, developer assistance is recommended.

DEV NOTE:
The system is architected with distinct modules for different concerns:
- Configuration (AutoCreatorXConfig)
- Orchestration (AutoCreatorXOrchestrator)
- Intelligence (IntelligenceCore: trends, scripting, metadata)
- Media Production (MediaCore: TTS, visuals, video editing)
- Platform Interaction (PlatformOperations: uploading)
- Safety & Resilience (AntiDetection, ErrorHandling)
- Monetization (MonetizationManager)
- Performance Analysis & Adaptation (FeedbackLoop)

Most external API interactions are currently SIMULATED. These will need
to be replaced with actual SDK calls for a production environment.
Consider asynchronous operations (`asyncio`) for I/O-bound tasks to improve
performance in a production setting.
"""

import os
import json
import time
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
import re

# --- External Libraries (Illustrative - Install as needed) ---
# import yaml # For loading config from YAML. USER NOTE: If you want to use a .yaml config file, this line needs to be active and PyYAML installed.
# from some_llm_provider_sdk import LLMClient
# from some_tts_provider_sdk import TTSClient
# from some_video_editing_api_sdk import VideoEditingClient
# from some_platform_api_sdk import YouTubeAPI, TikTokAPI # etc.

# --- Logging Configuration ---
# USER NOTE: Logs are records of what the system is doing. They are useful for
#            troubleshooting if something goes wrong. Log files are saved in the './logs' directory.
LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)  # Create the logs directory if it doesn't exist
LOG_FILE = os.path.join(LOG_DIR, f"autocreatorx_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,  # Level of detail in logs. INFO is a good balance. DEBUG is more verbose.
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.FileHandler(LOG_FILE),  # Save logs to a file
        logging.StreamHandler()         # Also print logs to the console/terminal
    ]
)
logger = logging.getLogger("AutoCreatorX_System")  # Root logger for the system

# --- Centralized Configuration Management ---
class AutoCreatorXConfig:
    """
    Manages the comprehensive configuration for the AutoCreatorX system.

    This class holds all the settings that control how AutoCreatorX operates.
    It's designed to be potentially loaded from an external file (like YAML or JSON)
    in a production environment, or use built-in defaults.

    USER NOTE: This is the primary place where you can customize the system's
    behavior without changing the core code. Many settings here, like keywords,
    language choices, and enabling/disabling features, are intended for you
    to adjust. Each setting below has a comment explaining its purpose.
    If a setting is marked with "USER NOTE: Safe to modify", you can generally
    change its value. For others, it's best to consult with a developer or
    understand the implications fully.

    DEV NOTE: Consider using a library like Pydantic for more robust validation,
    type coercion, and generating JSON schemas for configuration if the complexity grows.
    """
    def __init__(self, config_data: Optional[Dict[str, Any]] = None):
        """
        Initializes the configuration.

        Args:
            config_data (Optional[Dict[str, Any]]):
                A dictionary containing configuration values, typically loaded
                from an external file (e.g., YAML). If None, default settings are used.
        """
        if config_data:
            self._load_from_dict(config_data)
        else:
            self._set_default_config()

        # This path is derived after all base paths are set.
        self.current_project_dir: str = os.path.join(self.project_base_dir, self.instance_id)

    def _set_default_config(self):
        """
        Sets the default configuration values if no external config is provided.
        USER NOTE: These are the fallback settings if you don't provide a custom
                   configuration file. You can see what the system does by default here.
        """
        logger.info("No external configuration provided, using default settings.")

        # --- Project and System Identification ---
        # USER NOTE: These settings identify the system and specific runs. Generally, no need to change.
        self.system_id: str = "AutoCreatorX_V2_BETA"
        self.instance_id: str = f"INSTANCE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(10000, 99999)}"
        self.project_base_dir: str = "./autocreatorx_projects/" # USER NOTE: Safe to modify. Base directory where all project files for each run are stored.

        # --- Global Settings ---
        # USER NOTE: These settings apply across the entire system.
        self.global_language: str = "en" # USER NOTE: Safe to modify. Default language for content (e.g., "en" for English, "es" for Spanish). Must be in supported_languages.
        self.supported_languages: List[str] = ["en", "es", "fr", "de", "pt"] # USER NOTE: List of languages the system can attempt to work with. Adding new ones might require new AI models or voice options.
        self.default_content_style: str = "viral_explainer_short" # USER NOTE: Safe to modify. Default style for generated content. Must be in available_content_styles.
        self.available_content_styles: List[str] = [ # USER NOTE: Styles the system knows how to generate. Modifying requires corresponding prompt templates.
            "viral_explainer_short", "deep_dive_analysis", "news_summary", "tutorial_screencast"
        ]

        # --- Workflow and Scheduling ---
        # USER NOTE: Controls how the system runs automatically.
        self.autonomous_mode_enabled: bool = True # USER NOTE: Safe to modify. If True, the system runs continuously in cycles. If False, it runs once.
        self.autonomous_cycle_interval_hours: int = 12 # USER NOTE: Safe to modify. If autonomous_mode_enabled is True, this is how many hours to wait between cycles.
        self.error_retry_delay_minutes: int = 5 # USER NOTE: Advanced. Time to wait before retrying a failed step.
        self.max_step_retries: int = 3 # USER NOTE: Advanced. Maximum number of times to retry a single failed step.

        # --- Module-Specific Configurations ---

        # == Trend Analysis ==
        # USER NOTE: Settings for how the system finds trending topics.
        self.trend_analysis: Dict[str, Any] = {
            "enabled": True, # USER NOTE: Safe to modify. Set to False to disable automatic trend finding (manual topic needed).
            "primary_sources": ["YouTube_Trending_API", "Google_Trends_API", "Twitter_Realtime_API", "Reddit_API_Targeted"], # DEV NOTE: Actual API integrations needed. These are placeholders.
            "secondary_sources": ["News_API_Aggregator", "Web_Scraper_HighAuthority", "SEO_Keyword_Tools_API"], # DEV NOTE: More placeholder API names.
            "analysis_window_days": 5, # USER NOTE: Safe to modify. How many past days of data to consider for trends.
            "min_virality_score": 70, # USER NOTE: Safe to modify (0-100). Minimum score a trend needs to be considered. Higher means more selective.
            "sentiment_thresholds": {"positive": 0.6, "negative": 0.5}, # DEV NOTE: Thresholds for classifying sentiment around a trend.
            "niche_focus_keywords": ["AI breakthroughs", "Future Tech", "Space Exploration"], # USER NOTE: VERY IMPORTANT & Safe to modify. Keywords defining your primary areas of interest. System will prioritize topics related to these.
            "exclude_topics_containing": ["controversy", "scandal", "politics", "explicit"], # USER NOTE: VERY IMPORTANT & Safe to modify. Keywords to filter out unwanted topics.
            "time_series_analysis_enabled": True, # DEV NOTE: Enables (simulated) forecasting of trend longevity.
        }

        # == Intelligence Core (Content Logic) ==
        # USER NOTE: Settings for AI models used in scriptwriting and metadata generation.
        #            Modifying model names or providers requires developer expertise.
        self.intelligence_core: Dict[str, Any] = {
            "script_generation": {
                "model": {"provider": "LLM_CLOUD_XYZ", "name": "Powerful_Model_4_Turbo", "version": "4.5"}, # DEV NOTE: Placeholder for chosen Large Language Model (LLM).
                "parameters": {"temperature": 0.75, "max_tokens": 4000, "top_p": 0.9, "frequency_penalty": 0.4}, # DEV NOTE: Parameters for LLM generation. Temperature controls creativity.
                "prompt_templates_dir": "./prompt_templates/", # USER NOTE: Directory where script prompt templates are stored. Advanced users can edit/add templates here.
                "style_adaptation_model": {"provider": "NLP_CLOUD", "name": "StyleAdapter_V3"}, # DEV NOTE: Placeholder for a style adaptation model.
                "sentiment_incorporation_strength": 0.75, # DEV NOTE: How strongly to reflect detected trend sentiment in script tone.
            },
            "metadata_generation": { # Titles, descriptions, tags
                "model": {"provider": "LLM_CLOUD_XYZ", "name": "MetadataGen_V4"}, # DEV NOTE: Placeholder for metadata LLM.
                "parameters": {"temperature": 0.5, "max_tokens": 600}, # DEV NOTE: LLM parameters for metadata.
                "strategies": ["seo_focused", "engagement_driven", "informative_neutral"], # DEV NOTE: Different approaches to generating metadata.
                "ab_test_variants_to_generate": 3, # USER NOTE: Safe to modify (e.g., 1 to 5). How many different titles/descriptions to generate for potential A/B testing.
            },
            "sentiment_analysis": { # Analyzing sentiment of trends or comments
                "model": {"provider": "NLP_CLOUD", "name": "Sentiment_V5_Multilingual"}, # DEV NOTE: Placeholder for sentiment analysis model.
                "thresholds": {"positive": 0.7, "neutral": 0.4, "negative": 0.6}, # DEV NOTE: Thresholds for sentiment classification.
                "granularity": ["overall", "section_level"], # DEV NOTE: Level of detail for sentiment analysis (e.g., whole script vs. parts).
            },
            "factual_validation": {
                "enabled": True, # USER NOTE: Safe to modify. If True, tries to check facts in the script (simulated).
                "model": {"provider": "KNOWLEDGE_GRAPH_API", "name": "FactCheck_KG_V3"}, # DEV NOTE: Placeholder for fact-checking service.
                "confidence_threshold_flag": 0.90, # DEV NOTE: If fact-checker confidence is below this, it's flagged.
            },
            "creativity_level": "high", # USER NOTE: Safe to modify ("low", "medium", "high"). Influences how creative the AI tries to be in scriptwriting.
        }

        # == Media Core (Production) ==
        # USER NOTE: Settings for generating audio, visuals, and compiling the video.
        #            Changing providers or specific model names here requires developer setup.
        self.media_core: Dict[str, Any] = {
            "text_to_speech": { # Voiceover generation
                "provider": "TTS_CLOUD_PREMIUM", # DEV NOTE: Placeholder for Text-to-Speech service.
                "voice_options": { # USER NOTE: Define preferred voices per language. Names must match provider's options.
                    "en": "ultra_realistic_male_narrator",
                    "es": "ultra_realistic_female_narrator"
                },
                "parameters": {"speed": 1.0, "pitch_adjustment": 0.0, "intonation_style": "engaging_narrative"}, # DEV NOTE: TTS voice parameters.
                "error_handling": {"fallback_voice": "standard_quality_male", "retry_strategy": "exponential_backoff"}, # DEV NOTE: What to do if preferred voice fails.
            },
            "visual_asset_procurement": { # Finding images and video clips
                "priorities": ["AI_Video_Gen", "Stock_Footage_Premium", "AI_Image_Gen_HQ", "Internal_Library_Curated"], # DEV NOTE: Order of preference for sourcing visuals.
                "ai_video_gen": {"provider": "AI_VIDEO_GEN_PRO", "quality": "1080p_hdr", "max_clip_duration": 20}, # DEV NOTE: Settings for AI video generation.
                "stock_footage": {"provider": "STOCK_API_PREMIUM", "licenses": ["extended_commercial"]}, # DEV NOTE: Settings for stock footage services.
                "ai_image_gen": {"provider": "AI_IMAGE_GEN_MAX", "resolution": "4K"}, # DEV NOTE: Settings for AI image generation.
                "internal_library_path": "./media_library_vetted/", # USER NOTE: Path to your own pre-approved media assets.
                "asset_processing": {"resize": "1920x1080", "format": "mp4", "codec": "h264_high_profile"}, # DEV NOTE: How to process raw assets.
                "attribution_tracking_enabled": True, # USER NOTE: If True, system will try to log sources for attribution (important for licensed media).
            },
            "background_music": {
                "library_provider": "MUSIC_LICENSING_PRO", # DEV NOTE: Placeholder for music licensing service.
                "license_type": "royalty_free_sync_monetizable", # DEV NOTE: Type of music license required.
                "mood_keywords": ["uplifting tech", "cinematic suspense", "ambient focus", "energetic pop"], # USER NOTE: Keywords to guide music selection.
                "dynamic_volume_ducking_enabled": True, # USER NOTE: If True, lowers music volume during narration.
            },
            "video_composition": { # Putting all elements together into the final video
                "backend": {"provider": "CLOUD_VIDEO_EDITOR_API", "version": "3.0"}, # DEV NOTE: Placeholder for video editing service/software.
                "template_engine": {"enabled": True, "templates_dir": "./video_templates_dynamic/"}, # DEV NOTE: For using pre-defined video structures.
                "rendering_settings": {"format": "mp4", "codec": "h264", "resolution": "1080p", "fps": 30, "bitrate_mbps": 10}, # USER NOTE: Quality settings for the final video. Higher values mean better quality but larger files.
                "ai_editing_assistance": {"enabled": True, "features": ["auto_scene_detection", "smart_transitions", "color_grading_assist"]}, # DEV NOTE: AI features in video editing.
            },
            "thumbnail_generation": {
                "enabled": True, # USER NOTE: Safe to modify. Set to False to disable automatic thumbnail generation.
                "method": "ai_generated_custom_template", # DEV NOTE: Method for creating thumbnails.
                "template_styles": ["bold_typography_contrast", "human_emotion_closeup", "dynamic_action_shot"], # USER NOTE: Styles to guide AI thumbnail generation.
                "ai_model": {"provider": "AI_IMAGE_GEN_MAX", "name": "ThumbnailMaster_V2"}, # DEV NOTE: AI model for thumbnails.
                "parameters": {"aspect_ratio": "16:9", "resolution": "1920x1080"}, # DEV NOTE: Thumbnail dimensions.
            }
        }

        # == Platform Operations ==
        # USER NOTE: Settings for each social media platform you want to publish to.
        #            You'll need to provide API keys for each enabled platform (see 'secrets' section).
        self.platform_ops: Dict[str, Any] = {
            "youtube": {
                "enabled": True, # USER NOTE: Safe to modify. Set to False to disable uploads to YouTube.
                "api_credentials_id": "YOUTUBE_API_PRIMARY_ACCOUNT", # DEV NOTE: Key name in 'secrets' for YouTube API access.
                "upload_strategy": "adaptive_peak_engagement_time", # DEV NOTE: When to upload (e.g., immediately, scheduled, or when your audience is most active - advanced).
                "privacy_status": "private_then_public_with_premiere", # USER NOTE: Safe to modify. Initial privacy of uploaded video (e.g., "public", "private", "unlisted"). "private_then_public_with_premiere" makes it private, then schedules a public premiere.
                "category_id": "28", # USER NOTE: YouTube's category ID (e.g., "28" for Science & Technology). Find IDs in YouTube API docs.
                "playlist_management": {"enabled": True, "strategy": "ai_semantic_match", "max_playlists_per_video": 2}, # DEV NOTE: Automatic playlist management settings.
                "comment_management": {"analyze_sentiment": True, "auto_reply_positive": False, "auto_flag_negative": True}, # USER NOTE: How to handle comments (e.g., analyze sentiment, auto-reply to positive ones - 'auto_reply_positive' is False by default for safety).
                "monetization": {"enabled": True, "ad_break_strategy": "ai_optimized_flow"}, # USER NOTE: If your channel is monetized, these settings apply. Requires platform support.
                "community_engagement": {"post_polls": True, "share_shorts_from_long_form": True} # USER NOTE: Extra engagement features.
            },
            "tiktok": {
                "enabled": True, # USER NOTE: Safe to modify. Set to False to disable uploads to TikTok.
                "api_credentials_id": "TIKTOK_API_BUSINESS_ACCOUNT", # DEV NOTE: Key name in 'secrets' for TikTok API access.
                "upload_strategy": "simulated_human_prime_time_mobile", # DEV NOTE: Upload strategy for TikTok.
                "aspect_ratio": "9:16", # DEV NOTE: Standard TikTok video aspect ratio.
                "music_overlay_strategy": "trending_sound_api_match", # DEV NOTE: How to pick music for TikToks.
                "monetization": {"enabled": True, "strategy": "tiktok_pulse_program"}, # USER NOTE: TikTok monetization settings.
                "short_form_repurpose_source": "youtube_main_video", # DEV NOTE: If creating TikToks from longer videos.
                "max_video_duration_seconds": 180, # USER NOTE: Max length for TikToks created by this system.
            },
            "instagram": { # Example for another platform
                "enabled": False, # USER NOTE: Safe to modify. Set to True to enable Instagram uploads (requires full implementation).
                "api_credentials_id": "INSTAGRAM_API_CREATOR_ACCOUNT", # DEV NOTE: Key name in 'secrets'.
                "upload_strategy": "reels_first_then_story", # DEV NOTE: Upload strategy.
                "aspect_ratio_reels": "9:16", "aspect_ratio_posts": "1:1_or_4:5",
                "caption_strategy": "engagement_focused_short",
                "hashtag_strategy": "niche_plus_trending_mix",
            }
        }

        # == Safety Systems & Resilience ==
        # USER NOTE: Settings for content safety, copyright checks, and system stability.
        #            Generally, these are advanced settings.
        self.safety_systems: Dict[str, Any] = {
            "content_moderation": { # Checking for harmful content in scripts
                "enabled": True, # USER NOTE: Safe to modify. Recommended to keep True for safety.
                "model": {"provider": "MODERATION_CLOUD_ADVANCED", "name": "ContentSafetyNet_V6"}, # DEV NOTE: Placeholder for content moderation service.
                "thresholds": {"reject": 0.98, "manual_review": 0.75}, # DEV NOTE: Confidence scores for flagging/rejecting content.
                "failover_action": "manual_review_critical", # DEV NOTE: What to do if moderation fails.
                "categories_to_check": ["hate_speech", "violence", "adult_content", "misinformation_markers"] # USER NOTE: Types of content to screen for.
            },
            "copyright_check": {
                "enabled": True, # USER NOTE: Safe to modify. Recommended to keep True to avoid copyright issues.
                "audio_visual_scanning_api": {"provider": "COPYRIGHT_SCAN_PRO_API"}, # DEV NOTE: Placeholder for copyright scanning service.
                "match_threshold_flag": 0.95, # DEV NOTE: If similarity to copyrighted material is above this, it's flagged.
                "failover_action": "replace_asset_or_manual_review", # DEV NOTE: Action on copyright match.
            },
            "bias_detection": { # Checking for unintended bias in generated text
                "enabled": True, # USER NOTE: Safe to modify. Recommended to keep True.
                "model": {"provider": "NLP_CLOUD_ETHICS", "name": "BiasGuard_V2"}, # DEV NOTE: Placeholder for bias detection service.
                "threshold_flag": 0.75, # DEV NOTE: Threshold for flagging potential bias.
                "failover_action": "rewrite_section_or_manual_review", # DEV NOTE: Action on bias detection.
            },
            "anti_ban_measures": { # Techniques to avoid issues with platform APIs (advanced)
                "enabled": True, # USER NOTE: Advanced. Enable with caution and ensure compliance with platform ToS.
                "ip_rotation_service_id": "PROXY_SERVICE_01", # DEV NOTE: Reference to a proxy service configuration in 'secrets'.
                "account_cycling_pool_id": "ACCOUNT_POOL_MAIN", # DEV NOTE: Reference to a pool of accounts if using account cycling.
                "behavioral_randomization": {"upload_time_jitter_minutes": 45, "description_template_variance_level": 0.2}, # DEV NOTE: Adds randomness to actions.
                "rate_limiting_strategy": "dynamic_adaptive_platform_specific", # DEV NOTE: How to manage API call frequency.
                "user_agent_management": {"strategy": "rotate_real_device_profiles"}, # DEV NOTE: Simulating different devices/browsers.
            },
            "resource_monitoring": { # Watching system (CPU/memory) resources
                "enabled": True, # DEV NOTE: Helps prevent system overload.
                "thresholds": {"cpu_percent": 85, "memory_percent": 80, "gpu_percent": 85, "api_error_rate_percent": 10}, # DEV NOTE: Limits for resource usage.
                "action": "pause_cycle_alert_admin", # DEV NOTE: What to do if limits are exceeded.
            },
            "error_handling_strategy": "log_retry_then_failback", # DEV NOTE: Overall strategy for errors.
            "failback_mechanisms": { # DEV NOTE: Specific backup plans if primary methods fail.
                "trend_analysis": "use_cached_or_fallback_topics_high_priority",
                "llm_calls": "try_backup_model_then_simpler_model",
                "media_asset_procurement": "use_internal_library_then_lower_quality_stock",
                "tts_generation": "use_fallback_voice_then_standard_os_tts",
                "video_composition": "use_simpler_template_or_local_ffmpeg_basic"
            }
        }

        # == Feedback Loop & Adaptation ==
        # USER NOTE: Settings for learning from video performance to improve future content.
        #            This is an advanced feature.
        self.feedback_loop: Dict[str, Any] = {
            "enabled": True, # USER NOTE: Safe to modify. Set to False to disable automatic learning from performance.
            "performance_data_sources": ["YouTube_Analytics_API_V3", "TikTok_Analytics_API_V2", "Internal_Comment_Sentiment_Engine"], # DEV NOTE: Where to get performance data.
            "tracking_window_days": 21, # USER NOTE: How many days of performance data to analyze for each video.
            "metrics_to_track": ["views", "watch_time_hours", "audience_retention_percentage", "engagement_rate_per_view", "positive_sentiment_ratio", "subscriber_change", "ctr_impressions"], # DEV NOTE: Key performance indicators (KPIs).
            "adaptation_strategy": { # How the system adjusts itself
                "enabled": True, # USER NOTE: Safe to modify. If False, data is collected but system doesn't auto-adjust.
                "trigger_frequency_hours": 12, # USER NOTE: How often to run the adaptation logic.
                "parameters_to_adjust": ["topic_niche_weighting", "content_style_prioritization", "script_tone_adjustment", "thumbnail_style_preference", "upload_timing_model_update"], # DEV NOTE: Which internal settings the system can try to change.
                "min_data_points_for_adaptation": 30, # DEV NOTE: Minimum data needed before making adjustments.
                "learning_rate_factor": 0.1 # DEV NOTE: How aggressively to make changes.
            },
            "model_fine_tuning": { # Advanced: Re-training AI models with new data
                "enabled": False, # USER NOTE: Very advanced and potentially costly. Keep False unless you have a dedicated MLOps setup.
                "trigger_condition": "sustained_underperformance_vs_benchmark",
                "data_subset_for_tuning": "top_and_bottom_10_percent_content",
            },
            "competitive_analysis_enabled": True, # USER NOTE: If True, tries to analyze competitor content (simulated).
            "competitor_channels_to_monitor": ["CompetitorChannelID1", "CompetitorKeywordSearch"] # USER NOTE: List competitor channel IDs or keywords to track.
        }

        # == Monetization ==
        # USER NOTE: Settings related to making money from content (if applicable).
        self.monetization: Dict[str, Any] = {
            "enabled": True, # USER NOTE: Safe to modify. Set to False to disable all monetization features.
            "strategies": ["ad_revenue", "affiliate_marketing", "sponsorship_tags"], # USER NOTE: Monetization methods to use.
            "ad_revenue_optimization": { # For platforms like YouTube
                "enabled": True, # USER NOTE: If your content platform supports ads.
                "high_cpm_keywords_target": ["emerging tech", "saas tools", "online education"], # USER NOTE: Keywords that might attract higher-paying ads.
                "ad_placement_optimization": "ai_driven_viewer_retention_aware", # DEV NOTE: Strategy for placing mid-roll ads.
            },
            "affiliate_marketing": {
                "enabled": True, # USER NOTE: Safe to modify. If True, system may try to include affiliate links.
                "platforms": ["Amazon_Associates_API", "ShareASale_API"], # DEV NOTE: Affiliate platforms to integrate with.
                "product_categories": ["Software", "Tech Gadgets", "Online Courses"], # USER NOTE: Categories of products relevant to your content for affiliate links.
                "auto_link_insertion_enabled": True, # USER NOTE: If True, tries to automatically add links to descriptions.
                "link_placement_strategy": "contextual_end_screen_description", # DEV NOTE: How/where to insert links.
            },
            "sponsorship_tags": { # For disclosing sponsored content
                "enabled": False, # USER NOTE: Safe to modify. Set to True if you have sponsored content and need to add disclosures.
                "tagging_strategy": "relevant_brand_mentions", # DEV NOTE: How to identify content for sponsorship tags.
                "disclosure_text": "#ad #sponsored", # USER NOTE: Text used for sponsorship disclosure (e.g., #ad, #sponsored).
            },
            "digital_product_promotion": { # Promoting your own products
                "enabled": False, # USER NOTE: Safe to modify. Set to True to promote your own digital products.
                "products": [{"name": "Exclusive AI Masterclass", "link": "your_masterclass_link.com"}], # USER NOTE: List your products with names and links.
            },
            "revenue_tracking_enabled": True, # USER NOTE: If True, system will attempt to log estimated revenue (requires platform analytics integration).
            "revenue_reporting_interval_days": 7, # DEV NOTE: How often to generate (simulated) revenue reports.
        }

        # --- Secret Management ---
        # USER NOTE: API keys and other sensitive credentials.
        #            These are BEST stored in environment variables or a secure secrets manager, NOT hardcoded.
        #            The os.environ.get() method tries to read them from environment variables.
        #            The second argument is a PLACEHOLDER if the environment variable isn't found.
        #            YOU MUST replace these placeholders with your actual keys or set them as environment variables.
        self.secrets: Dict[str, str] = {
            "YOUTUBE_API_PRIMARY_ACCOUNT": os.environ.get("YOUTUBE_API_PRIMARY_ACCOUNT", "env_placeholder_youtube_secret_REPLACE_ME"),
            "TIKTOK_API_BUSINESS_ACCOUNT": os.environ.get("TIKTOK_API_BUSINESS_ACCOUNT", "env_placeholder_tiktok_secret_REPLACE_ME"),
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", "env_placeholder_openai_secret_REPLACE_ME"), # Example if using OpenAI
            "LLM_CLOUD_XYZ_KEY": os.environ.get("LLM_CLOUD_XYZ_KEY", "env_placeholder_llm_cloud_secret_REPLACE_ME"), # Key for the main LLM provider
            "TTS_CLOUD_PREMIUM_KEY": os.environ.get("TTS_CLOUD_PREMIUM_KEY", "env_placeholder_tts_cloud_secret_REPLACE_ME"), # Key for the TTS provider
            "STOCK_API_PREMIUM_KEY": os.environ.get("STOCK_API_PREMIUM_KEY", "env_placeholder_stock_api_secret_REPLACE_ME"), # Key for stock media
            "MODERATION_CLOUD_ADVANCED_KEY": os.environ.get("MODERATION_CLOUD_ADVANCED_KEY", "env_placeholder_moderation_secret_REPLACE_ME"), # Key for content moderation
            "COPYRIGHT_SCAN_PRO_API_KEY": os.environ.get("COPYRIGHT_SCAN_PRO_API_KEY", "env_placeholder_copyright_secret_REPLACE_ME"), # Key for copyright scanning
            # DEV NOTE: Add entries for all API keys corresponding to the "provider" fields used throughout the config.
            # The key names used here (e.g., "YOUTUBE_API_PRIMARY_ACCOUNT") must match the `api_credentials_id` values in `platform_ops`.
        }

    def _load_from_dict(self, config_data: Dict[str, Any]):
        """
        Loads configuration from a dictionary (e.g., parsed from YAML/JSON).
        This allows overriding default settings with values from the dictionary.

        Args:
            config_data (Dict[str, Any]): Dictionary of configuration settings.

        DEV NOTE: This is a simple dictionary update. For nested dictionaries,
                  a deep merge strategy might be preferable in some cases.
        """
        logger.info("Loading configuration from provided dictionary.")
        for key, value in config_data.items():
            if hasattr(self, key):
                # DEV NOTE: For nested dicts, this replaces the whole dict.
                # A more sophisticated loader might merge nested dicts.
                current_value = getattr(self, key)
                if isinstance(current_value, dict) and isinstance(value, dict):
                    # Simple one-level merge for module configurations
                    current_value.update(value)
                else:
                    setattr(self, key, value)
            else:
                logger.warning(f"Unknown configuration key '{key}' in provided data. Ignoring.")
        # Ensure instance_id and project_base_dir are correctly set, possibly from loaded data or defaults.
        # These are fundamental and should always be present.
        self.instance_id = config_data.get("instance_id", getattr(self, 'instance_id', f"FALLBACK_INSTANCE_{random.randint(0,9999)}")) # Ensure it exists
        self.project_base_dir = config_data.get("project_base_dir", getattr(self, 'project_base_dir', "./autocreatorx_projects_fallback/"))

    @classmethod
    def load_from_yaml(cls, file_path: str) -> 'AutoCreatorXConfig':
        """
        Loads configuration from a YAML file.

        Args:
            file_path (str): The path to the YAML configuration file.

        Returns:
            AutoCreatorXConfig: An instance of AutoCreatorXConfig populated with
                                settings from the YAML file, or default settings if loading fails.

        USER NOTE: To use this, you need to have a YAML file (e.g., 'autocreatorx_config.yaml')
                   with settings structured similarly to how they appear in `_set_default_config`.
                   You also need the PyYAML library installed (`pip install pyyaml`).
        """
        try:
            import yaml # Local import to avoid making PyYAML a hard dependency if not used.
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            if not config_data: # Handles empty YAML file
                logger.warning(f"YAML configuration file is empty: {file_path}. Using default configuration.")
                return cls()
            logger.info(f"Successfully loaded configuration from YAML file: {file_path}")
            return cls(config_data=config_data)
        except FileNotFoundError:
            logger.error(f"YAML configuration file not found: {file_path}. Using default configuration.")
            return cls() # Return default config
        except ImportError:
            logger.error("PyYAML library is not installed. Please 'pip install pyyaml' to load YAML configurations. Using default configuration.")
            return cls()
        except yaml.YAMLError as e: # More specific YAML parsing error
            logger.error(f"Error parsing YAML configuration file {file_path}: {e}. Using default configuration.")
            return cls()
        except Exception as e: # Catch-all for other unexpected errors during loading
            logger.error(f"Unexpected error loading YAML configuration from {file_path}: {e}. Using default configuration.")
            return cls()

    def validate_config(self) -> bool:
        """
        Performs basic validation of the loaded configuration.

        Returns:
            bool: True if basic validation passes, False otherwise.

        DEV NOTE: This should be expanded with more checks for critical fields,
                  valid value ranges, consistency between settings, and existence of
                  necessary directories or files (like prompt templates).
                  For a production system, robust validation is crucial.
        USER NOTE: This step checks if some basic settings are correct. If it fails,
                   the system might not work as expected. Error messages will indicate
                   what might be wrong.
        """
        # Check 1: Project base directory
        if not isinstance(self.project_base_dir, str) or not self.project_base_dir:
            logger.error("Validation Error: 'project_base_dir' must be a non-empty string.")
            return False
        if not os.path.isdir(self.project_base_dir):
            # This is a warning because create_project_directories will attempt to create it.
            # However, if the path is fundamentally invalid (e.g., permissions), it's good to note.
            logger.warning(f"Project base directory not found: {self.project_base_dir}. The system will attempt to create it.")

        # Check 2: Prompt templates directory existence (if script generation is enabled)
        if self.intelligence_core.get("script_generation"): # Check if script_generation config exists
            prompt_templates_dir = self.intelligence_core["script_generation"].get("prompt_templates_dir")
            if not isinstance(prompt_templates_dir, str) or not prompt_templates_dir:
                 logger.error("Validation Error: 'prompt_templates_dir' in 'script_generation' must be a non-empty string.")
                 return False
            if not os.path.isdir(prompt_templates_dir):
                logger.error(f"Validation Error: Prompt templates directory not found: {prompt_templates_dir}. This is crucial for script generation.")
                # return False # This could be a critical failure.

        # Check 3: Global language supported
        if self.global_language not in self.supported_languages:
            logger.error(f"Validation Error: Global language '{self.global_language}' is not in the list of supported languages: {self.supported_languages}.")
            return False

        # Check 4: Default content style available
        if self.default_content_style not in self.available_content_styles:
            logger.error(f"Validation Error: Default content style '{self.default_content_style}' is not in available styles: {self.available_content_styles}.")
            return False

        # Check 5: Ensure API credential IDs specified for enabled platforms actually exist in secrets
        for platform_name, platform_cfg in self.platform_ops.items():
            if platform_cfg.get("enabled"):
                api_cred_id = platform_cfg.get("api_credentials_id")
                if not api_cred_id:
                    logger.error(f"Validation Error: Platform '{platform_name}' is enabled but 'api_credentials_id' is missing.")
                    return False
                if api_cred_id not in self.secrets:
                    logger.error(f"Validation Error: API credential ID '{api_cred_id}' for platform '{platform_name}' not found in 'secrets' configuration.")
                    return False
                if "env_placeholder_" in self.secrets[api_cred_id]: # Check if it's still a placeholder
                     logger.warning(f"Validation Warning: API key for '{api_cred_id}' (platform: {platform_name}) appears to be a placeholder: '{self.secrets[api_cred_id]}'. Ensure it's replaced with a real key.")


        logger.info("Configuration validation completed (basic checks passed). Further checks may occur at runtime.")
        return True

    def create_project_directories(self):
        """
        Creates the necessary directory structure for the current project instance.
        This helps organize all files generated during a single run of the system.

        Raises:
            OSError: If directory creation fails due to OS-level issues (e.g., permissions).

        USER NOTE: This function automatically sets up folders to store logs, scripts,
                   media files, etc., for each content creation cycle. You usually don't
                   need to interact with this directly, but it's good to know where files are stored.
        """
        try:
            # Ensure the main project base directory exists first
            os.makedirs(self.project_base_dir, exist_ok=True)
            # Then create the specific instance directory
            os.makedirs(self.current_project_dir, exist_ok=True)

            # Define a more structured set of subdirectories
            # These are numbered to suggest a general workflow order, aiding in Browse.
            subdirs = [
                "00_instance_logs",          # Specific logs for this instance/cycle
                "01_trend_analysis_reports", # Data and reports from trend analysis
                "02_generated_scripts",      # Drafts and final scripts
                "03_generated_metadata",     # Titles, descriptions, tags
                "04_media_assets_raw/audio", # Raw downloaded/generated audio
                "04_media_assets_raw/video", # Raw video clips
                "04_media_assets_raw/images",# Raw images
                "05_media_assets_processed/audio", # Processed audio (e.g., voiceovers)
                "05_media_assets_processed/video", # Processed video clips
                "05_media_assets_processed/images",# Processed images
                "06_final_video_compositions", # The final rendered videos
                "07_generated_thumbnails",   # Thumbnails for videos
                "08_platform_upload_receipts",# Logs/confirmations of uploads
                "09_performance_analytics_data",# Data collected by the feedback loop
                "10_monetization_data",      # Revenue reports, affiliate link usage
                "99_safety_and_compliance"   # Logs for moderation, copyright, etc.
            ]
            for subdir in subdirs:
                os.makedirs(os.path.join(self.current_project_dir, subdir), exist_ok=True)
            logger.info(f"Successfully created project instance directories under: {self.current_project_dir}")
        except OSError as e:
            logger.error(f"FATAL: Failed to create essential project directories at '{self.current_project_dir}': {e}. Check permissions and path validity.")
            raise # Re-raise to halt execution if directories crucial for operation cannot be created.

# --- Utility Functions and Classes ---
class Utilities:
    """
    A collection of reusable utility functions for common tasks within AutoCreatorX.

    This class is not meant to be instantiated; its methods are static and can be
    called directly (e.g., `Utilities.slugify("Some Text")`).

    USER NOTE: These are helper tools used internally by the system. You generally
               won't need to interact with this class directly.
    DEV NOTE: Add any generic, stateless helper functions here.
              Ensure methods are well-documented and tested.
    """
    @staticmethod
    def slugify(text: str) -> str:
        """
        Converts a string into a URL-friendly "slug".
        A slug is typically lowercase, with spaces replaced by hyphens or underscores,
        and special characters removed. Useful for creating filenames or URL parts.

        Example: "My Awesome Video!" -> "my_awesome_video"

        Args:
            text (str): The input string to be slugified.

        Returns:
            str: The slugified string. Returns "untitled" if the input results in an empty string.

        DEV NOTE: This implementation is fairly basic. For more robust slugification,
                  consider libraries like `python-slugify` which handle unicode better
                  and offer more customization.
        """
        if not isinstance(text, str): # Ensure input is a string
            text = str(text)
        text = text.lower() # Convert to lowercase
        text = re.sub(r'\s+', '_', text) # Replace one or more whitespace characters with a single underscore
        text = re.sub(r'[^a-z0-9_\-\.]', '', text) # Remove characters that are not alphanumeric, underscore, hyphen, or period
        text = re.sub(r'_+', '_', text) # Replace multiple underscores with a single underscore (in case previous steps created them)
        text = text.strip('_-.') # Remove leading/trailing underscores, hyphens, or periods
        return text if text else "untitled" # If string becomes empty, return a default

    @staticmethod
    def calculate_optimal_ad_breaks(video_duration_seconds: int, strategy: str = "auto_optimized", script_structure: Optional[Dict] = None) -> List[int]:
        """
        Calculates optimal timestamps (in seconds) for ad breaks in a video.
        The calculation depends on the video duration and the chosen strategy.

        Args:
            video_duration_seconds (int): The total duration of the video in seconds.
            strategy (str, optional): The ad placement strategy.
                Expected values are defined by platform monetization settings, e.g.,
                "ai_optimized_flow", "auto_optimized", "manual_timed".
                Defaults to "auto_optimized".
            script_structure (Optional[Dict], optional):
                A dictionary representing the script's structure (e.g., sections, timings).
                This can be used by "ai_optimized_flow" to find natural pause points.
                Defaults to None.

        Returns:
            List[int]: A list of timestamps (integers, in seconds from the start of the video)
                       where ad breaks could be placed. Returns an empty list if no mid-roll ads
                       are applicable (e.g., for short videos or unsupported strategies).

        USER NOTE: This function helps decide where ads should go in longer videos.
                   The behavior is controlled by the 'ad_break_strategy' setting for each
                   platform in the configuration file. "AI optimized" strategies try to
                   find less disruptive points for ads.

        DEV NOTE: The "ai_optimized_flow" is currently SIMULATED. A real implementation
                  would involve NLP analysis of the script (or even audio/visual cues if available post-production)
                  to identify suitable segments for ad insertion (e.g., between topics, during pauses).
                  Platforms like YouTube often have their own auto-placement, but providing suggestions can be useful.
                  Ensure timestamps are valid (e.g., not too close to start/end, not overlapping).
        """
        breaks: List[int] = []
        min_video_duration_for_midroll_ads = 60 * 8 # Generally, platforms like YouTube allow mid-rolls for videos > 8 minutes.

        if video_duration_seconds < min_video_duration_for_midroll_ads:
            logger.debug(f"Video duration ({video_duration_seconds}s) is less than minimum for mid-roll ads ({min_video_duration_for_midroll_ads}s). No ad breaks calculated.")
            return breaks

        # Standardize strategy names for easier checking
        normalized_strategy = strategy.lower()

        if "ai_optimized" in normalized_strategy or "auto_optimized" in normalized_strategy:
            logger.debug(f"Calculating AI-optimized ad breaks for {video_duration_seconds}s video using strategy '{strategy}'.")
            # --- SIMULATED AI-Driven Ad Placement Logic ---
            # A real AI would analyze script_structure (if provided) for natural pauses,
            # topic shifts, or low-engagement points.
            # It would also consider ad density rules (e.g., not too close together).
            if script_structure and 'sections' in script_structure:
                # DEV NOTE: Conceptual. Here you might iterate through script_structure['sections'],
                # look at their estimated timings, and identify good transition points.
                logger.debug(f"Script structure provided with {len(script_structure['sections'])} sections. (Simulated analysis)")
                pass # Placeholder for actual analysis

            # Example simulated logic: place ads roughly at 1/3 and 2/3 points if video is long enough,
            # with some randomization to simulate variability.
            if video_duration_seconds >= 300: # At least 5 minutes
                breaks.append(random.randint(int(video_duration_seconds * 0.25), int(video_duration_seconds * 0.35)))
            if video_duration_seconds >= 600: # At least 10 minutes
                breaks.append(random.randint(int(video_duration_seconds * 0.60), int(video_duration_seconds * 0.70)))
            if video_duration_seconds >= 900: # At least 15 minutes
                # Add a third break if very long, ensuring it's spaced out
                potential_third_break = random.randint(int(video_duration_seconds * 0.80), int(video_duration_seconds * 0.90))
                if breaks and potential_third_break > breaks[-1] + 120: # Ensure at least 2 mins from last break
                     breaks.append(potential_third_break)


        elif "manual_timed" in normalized_strategy:
            logger.debug(f"Calculating manually timed ad breaks for {video_duration_seconds}s video.")
            # Simple timed intervals. Example: one ad every 5-7 minutes.
            interval = random.randint(300, 420) # 5 to 7 minutes
            current_time = interval
            while current_time < (video_duration_seconds - 60): # Don't put an ad in the last minute
                breaks.append(current_time)
                current_time += interval
        else:
            logger.warning(f"Unknown or unsupported ad break strategy: '{strategy}'. No ad breaks calculated.")
            return []

        # Clean up: remove duplicates, sort, and ensure breaks are not too close to start/end or each other.
        if breaks:
            unique_sorted_breaks = sorted(list(set(breaks)))
            final_breaks = []
            last_break_time = 0
            min_spacing = 120 # Minimum 2 minutes between breaks (example)
            for b_time in unique_sorted_breaks:
                # Ensure break is not too early (e.g., not before 60s) and not too late (e.g., not in last 60s)
                # And ensure spacing from previous break
                if 60 < b_time < (video_duration_seconds - 60) and (b_time - last_break_time >= min_spacing):
                    final_breaks.append(b_time)
                    last_break_time = b_time
            breaks = final_breaks

        logger.info(f"Calculated ad breaks ({strategy}): {breaks} for video of {video_duration_seconds}s")
        return breaks

    @staticmethod
    def load_prompt_template(template_name: str, config: AutoCreatorXConfig, **kwargs) -> str:
        """
        Loads a prompt template text from a file and formats it with provided keyword arguments.

        Prompt templates are used to guide AI models (LLMs) in generating text
        (e.g., scripts, metadata). They often contain placeholders like {topic}
        or {keywords} that get filled in dynamically.

        Args:
            template_name (str): The name of the template file (without .txt extension).
                                 This name will be slugified to form the filename.
            config (AutoCreatorXConfig): The system configuration object, used to find
                                         the `prompt_templates_dir`.
            **kwargs: Arbitrary keyword arguments that will be used to format
                      the placeholders in the prompt template.

        Returns:
            str: The loaded and formatted prompt template string.
                 If the template is not found or an error occurs, a fallback error
                 message string is returned, which itself can act as a minimal prompt.

        USER NOTE: Prompt templates are stored in the directory specified by
                   `prompt_templates_dir` in the configuration. If you are an advanced user,
                   you can edit these .txt files to change how the AI generates content.
                   Make sure any placeholders like `{example_placeholder}` in your template
                   match the keywords used when this function is called by the system.

        DEV NOTE: Ensures template names are filesystem-friendly by slugifying them.
                  Includes basic error handling for file not found or key errors during formatting.
                  The fallback prompt should be generic enough to allow some form of generation.
        """
        # Retrieve the directory for prompt templates from the configuration.
        prompt_templates_dir = config.intelligence_core["script_generation"]["prompt_templates_dir"]
        # Sanitize the template name to create a safe filename (e.g., "My Template!" -> "my_template.txt").
        safe_filename = f"{Utilities.slugify(template_name)}.txt"
        template_path = os.path.join(prompt_templates_dir, safe_filename)

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            # Fill in placeholders in the template with provided keyword arguments.
            # For example, if template has "{topic}" and kwargs has topic="AI", it's replaced.
            return template_content.format(**kwargs)
        except FileNotFoundError:
            logger.error(f"Prompt template file not found: {template_path}. Using a fallback prompt.")
            # Fallback prompt includes the original topic if available in kwargs.
            return f"Error: Prompt template '{template_name}' not found. Please generate informative content about: {kwargs.get('topic', 'the provided subject')}."
        except KeyError as e:
            # This error means a placeholder in the template (e.g., {missing_key})
            # was not provided in the **kwargs.
            logger.error(f"Missing key for formatting prompt template '{template_name}' (file: {template_path}): {e}. Check if all placeholders are supplied. Using a fallback prompt.")
            return f"Error: Prompt template '{template_name}' has a missing placeholder {e}. Please generate informative content about: {kwargs.get('topic', 'the provided subject')}."
        except Exception as e:
            # Catch any other unexpected errors during file reading or formatting.
            logger.error(f"An unexpected error occurred while loading or formatting prompt template '{template_name}' (file: {template_path}): {e}. Using a fallback prompt.")
            return f"Error: Could not load prompt template '{template_name}'. Please generate informative content about: {kwargs.get('topic', 'the provided subject')}."

# --- Error Handling ---
class ErrorHandling:
    """
    Provides centralized mechanisms for handling errors and implementing retry logic.

    This class aims to make error recovery more consistent across the system.
    Methods are static as they provide utility functions rather than managing state.

    USER NOTE: This part of the system tries to automatically recover from temporary
               problems (like a brief internet connection issue when talking to an
               AI service). You usually don't interact with this directly, but its settings
               (like `max_step_retries` in the config) control how persistent it is.

    DEV NOTE: Enhance with more sophisticated retry strategies (e.g., jitter,
              circuit breakers). Consider integrating with a dedicated resiliency library
              if error handling logic becomes very complex.
    """
    @staticmethod
    def handle_step_error(step_name: str,
                          error: Exception,
                          attempt: int,
                          max_retries: int,
                          retry_delay_minutes: int,
                          failback_strategy: Optional[str] = None) -> bool:
        """
        Handles errors that occur during a specific workflow step, with retry logic.

        This function logs the error and, if retry attempts are remaining,
        pauses execution before indicating a retry should occur. If all retries
        are exhausted, it logs a critical failure.

        Args:
            step_name (str): A descriptive name of the workflow step where the error occurred (e.g., "TrendAnalysis_APIFetch").
            error (Exception): The actual exception object that was caught.
            attempt (int): The current attempt number for this step (e.g., 1 for the first try).
            max_retries (int): The maximum number of retry attempts allowed for this step,
                               typically from `AutoCreatorXConfig.max_step_retries`.
            retry_delay_minutes (int): The base delay in minutes before a retry,
                                       typically from `AutoCreatorXConfig.error_retry_delay_minutes`.
                                       An exponential backoff is applied to this delay.
            failback_strategy (Optional[str], optional): A string describing the failback
                                                        strategy to be used if all retries fail.
                                                        This is for logging purposes here; the caller
                                                        implements the actual failback. Defaults to None.

        Returns:
            bool: True if a retry should be attempted (i.e., `attempt < max_retries`).
                  False if all retries have been exhausted and the step has failed permanently.

        DEV NOTE: The exponential backoff (`* (2 ** (attempt - 1))`) helps prevent
                  overwhelming a struggling service by increasing delays after each failure.
                  Consider adding jitter to the backoff to avoid thundering herd problems if
                  multiple instances of this system might retry simultaneously.
        """
        # Log the error with detailed information, including the type of error and its message.
        # `exc_info=True` includes traceback information in the log, which is invaluable for debugging.
        logger.error(
            f"Error during step '{step_name}' (Attempt {attempt}/{max_retries}): {type(error).__name__} - {str(error)}",
            exc_info=True
        )

        if attempt < max_retries:
            # Calculate delay with exponential backoff: delay = base_delay * 2^(attempt-1)
            # E.g., attempt 1 (first retry): base_delay * 1
            #       attempt 2 (second retry): base_delay * 2
            #       attempt 3 (third retry): base_delay * 4
            actual_delay_seconds = retry_delay_minutes * 60 * (2 ** (attempt - 1)) # Convert minutes to seconds
            logger.info(f"Retrying step '{step_name}' in {actual_delay_seconds / 60:.2f} minutes...")
            time.sleep(actual_delay_seconds)
            return True  # Indicate that a retry should happen
        else:
            logger.critical(
                f"Step '{step_name}' failed permanently after {max_retries} attempts. "
                f"Failback strategy configured: '{failback_strategy or 'None Specified'}'."
            )
            # The calling code is responsible for implementing the actual failback action
            # based on the 'failback_strategy' string (e.g., from config.safety_systems["failback_mechanisms"]).
            return False # Indicate that the step failed permanently

    @staticmethod
    def handle_api_error(api_name: str,
                         error: Exception,
                         failback_config_key: str,
                         config: AutoCreatorXConfig) -> Any:
        """
        Handles errors from external API calls, with potential failback actions.

        This function logs the API error and attempts to enact a failback strategy
        as defined in the system configuration.

        Args:
            api_name (str): Name of the API that failed (e.g., "LLM_ScriptGeneration_API").
            error (Exception): The exception object from the API call.
            failback_config_key (str): The key within `config.safety_systems["failback_mechanisms"]`
                                       that specifies the failback strategy for this type of API call
                                       (e.g., "llm_calls", "trend_analysis").
            config (AutoCreatorXConfig): The system configuration object.

        Returns:
            Any: The result of a successful failback action (e.g., cached data,
                 response from a backup model). The exact type depends on the
                 failback strategy. If the strategy is to "skip_step", it returns None.

        Raises:
            Exception: Re-raises the original error if no effective failback strategy
                       is defined or if the failback itself encounters an unhandled issue.

        DEV NOTE: The actual failback logic (e.g., calling a backup API, loading cache)
                  is currently SIMULATED. Real implementations would go into the conditional
                  blocks below. This method centralizes the decision-making based on config.
                  The return type 'Any' is used because failback results can vary widely.
                  Consider defining specific return types or status objects for clarity in a production system.
        """
        logger.error(
            f"External API call to '{api_name}' failed: {type(error).__name__} - {str(error)}",
            exc_info=True
        )

        # Retrieve the specific failback strategy string from the configuration.
        failback_strategy_name = config.safety_systems["failback_mechanisms"].get(failback_config_key)
        logger.info(f"Attempting failback for '{api_name}' using strategy '{failback_strategy_name}' (linked to config key '{failback_config_key}').")

        # --- SIMULATED Failback Logic based on strategy_name ---
        if failback_strategy_name == "try_backup_model_or_provider" or \
           "try_backup_model_then_simpler_model" in failback_strategy_name: # More flexible matching
            logger.warning(f"FAILBACK ACTION (Simulated): For '{api_name}', attempting to use a backup model or provider.")
            # DEV NOTE: Implement logic here to:
            # 1. Check config for a defined backup model/provider for 'api_name' or 'failback_config_key'.
            # 2. Initialize a client for the backup service.
            # 3. Re-attempt the original operation using the backup client.
            # return result_from_backup_api
            return {"status": "success_via_failback", "data": "simulated_response_from_backup_model_for_" + api_name}

        elif failback_strategy_name == "use_cached_or_fallback_data" or \
             "use_cached_or_fallback_topics" in failback_strategy_name or \
             "use_internal_library_only" in failback_strategy_name or \
             "use_internal_library_then_lower_quality_stock" in failback_strategy_name or \
             "use_fallback_voice_then_standard_os_tts" in failback_strategy_name: # Group similar cache/fallback strategies
            logger.warning(f"FAILBACK ACTION (Simulated): For '{api_name}', attempting to use cached data or predefined fallback content.")
            # DEV NOTE: Implement logic here to:
            # 1. Check a local cache (e.g., Redis, file-based) for recent valid data for this request.
            # 2. If no cache, load pre-defined fallback data (e.g., a list of generic topics, default assets).
            # return cached_or_fallback_data
            return {"status": "success_via_failback", "data": "simulated_cached_or_fallback_data_for_" + api_name}

        elif failback_strategy_name == "skip_step":
            logger.warning(f"FAILBACK ACTION: For '{api_name}', the strategy is to skip this step. No further action will be taken for this item.")
            return None # Special return value indicating the step should be gracefully skipped.

        elif failback_strategy_name == "use_simpler_template_or_local_ffmpeg_basic":
             logger.warning(f"FAILBACK ACTION (Simulated): For '{api_name}', attempting to use a simpler template or basic local processing.")
             return {"status": "success_via_failback", "data": "simulated_output_from_simpler_process_for_" + api_name}

        else:
            logger.critical(
                f"No effective or recognized failback strategy ('{failback_strategy_name}') implemented for API error in '{api_name}' "
                f"(config key: '{failback_config_key}'). Re-raising original error."
            )
            raise error # Re-raise the original error if no suitable failback is defined or handled.

# --- Anti-Detection ---
class AntiDetection:
    """
    Manages techniques and strategies to minimize detection and potential blocking
    by external platforms when interacting with their APIs or services.

    This class encapsulates logic for IP rotation, user-agent management,
    behavioral randomization, and account cycling.

    USER NOTE: This is an advanced component that tries to make the system's
               interactions with platforms (like YouTube, TikTok, AI services)
               appear more like a regular user to avoid being flagged as a bot.
               Its settings are in the 'anti_ban_measures' section of the config.
               Enable and configure these features with caution and always respect
               the Terms of Service of the platforms you interact with. Misuse can
               lead to account penalties.

    DEV NOTE: The actual implementation of proxy management, account cycling, and
              user-agent rotation requires external services or libraries (e.g.,
              a proxy provider API, a database of accounts, a list of user agents).
              These are currently SIMULATED.
              Ensure all anti-detection measures are used responsibly and ethically.
    """
    def __init__(self, config: AutoCreatorXConfig):
        """
        Initializes the AntiDetection module.

        Args:
            config (AutoCreatorXConfig): The main system configuration object.
        """
        self.config_main = config # Store the main config for broader access if needed
        self.config_anti_ban = config.safety_systems["anti_ban_measures"]
        self.logger = logging.getLogger("AntiDetection")

        # DEV NOTE: Initialize actual manager instances here if features are enabled.
        # Example:
        # self.proxy_manager = None
        # if self.config_anti_ban.get("ip_rotation_enabled") and self.config_anti_ban.get("ip_rotation_service_id"):
        #     proxy_service_config = config.secrets.get(self.config_anti_ban["ip_rotation_service_id"])
        #     self.proxy_manager = ProxyManager(proxy_service_config) # Assuming ProxyManager class exists

        # self.account_manager = None
        # if self.config_anti_ban.get("account_cycling_enabled") and self.config_anti_ban.get("account_cycling_pool_id"):
        #     account_pool_config = config.secrets.get(self.config_anti_ban["account_cycling_pool_id"])
        #     self.account_manager = AccountManager(account_pool_config) # Assuming AccountManager class exists

        # self.user_agent_rotator = UserAgentRotator(self.config_anti_ban["user_agent_management"]["strategy"]) # Assuming UserAgentRotator class exists

        self.logger.info(f"AntiDetection module initialized. Strategies configured: {self.config_anti_ban}")

    def get_request_headers(self, platform_context: str) -> Dict[str, str]:
        """
        Generates HTTP headers for an outgoing request, potentially including a rotated User-Agent.

        Args:
            platform_context (str): A string indicating the target platform or context for the request
                                    (e.g., "youtube_api", "llm_provider_xyz_script_gen").
                                    This can help in selecting a more appropriate User-Agent.

        Returns:
            Dict[str, str]: A dictionary of HTTP headers.

        DEV NOTE: Currently simulates User-Agent rotation. A real UserAgentRotator would
                  maintain a list of valid, common user agents and select one, possibly
                  based on `platform_context`.
        """
        headers = {}
        user_agent_strategy = self.config_anti_ban.get("user_agent_management", {}).get("strategy", "default")

        # --- SIMULATED User-Agent Rotation ---
        if user_agent_strategy == "rotate_real_device_profiles" or user_agent_strategy == "rotate_common":
            # In a real system, self.user_agent_rotator.get_random_agent(platform_hint=platform_context)
            simulated_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36"
            ]
            headers["User-Agent"] = random.choice(simulated_agents)
            self.logger.debug(f"Using rotated User-Agent for {platform_context}: {headers['User-Agent']}")
        else: # Default or unknown strategy
            headers["User-Agent"] = f"AutoCreatorX/{self.config_main.system_id} (AutomatedContentSystem; +https://example.com/botinfo)" # Polite default
            self.logger.debug(f"Using default User-Agent for {platform_context}: {headers['User-Agent']}")

        # Add other common headers that platforms might expect or that can add to "natural" behavior.
        # These are often language preferences.
        # USER NOTE: global_language is taken from your main configuration.
        headers["Accept-Language"] = f"{self.config_main.global_language.lower()}-{self.config_main.global_language.upper()},{self.config_main.global_language.lower()};q=0.9,en-US;q=0.8,en;q=0.7"
        headers["Accept"] = "application/json, text/plain, */*" # Common accept header

        return headers

    def get_request_proxy(self, platform_context: str) -> Optional[Dict[str, str]]:
        """
        Retrieves proxy settings for an outgoing request, if IP rotation is enabled.

        Args:
            platform_context (str): Context for the request, potentially influencing proxy selection
                                    (e.g., for geo-targeting if proxies support it).

        Returns:
            Optional[Dict[str, str]]: A dictionary suitable for `requests` library's `proxies` argument
                                      (e.g., `{'http': 'http://proxy_url', 'https': 'http://proxy_url'}`),
                                      or None if IP rotation is disabled or no proxy is available.

        DEV NOTE: SIMULATED. A real ProxyManager would interact with a proxy service API or a list
                  of proxies, handle proxy authentication, and manage proxy health/cooldowns.
        """
        if self.config_anti_ban.get("ip_rotation_enabled") and self.config_anti_ban.get("ip_rotation_service_id"):
            # In a real system: proxy_url = self.proxy_manager.get_next_proxy(target_platform=platform_context)
            # For simulation, let's imagine a few proxies.
            simulated_proxies = [
                "http://user1:pass1@proxy.example.com:8080",
                "http://user2:pass2@anotherproxy.example.net:3128",
                None # Simulate occasionally not using a proxy or one not being available
            ]
            chosen_proxy_url = random.choice(simulated_proxies)

            if chosen_proxy_url:
                self.logger.debug(f"Using SIMULATED proxy for {platform_context}: {chosen_proxy_url.split('@')[1] if '@' in chosen_proxy_url else chosen_proxy_url }") # Don't log credentials
                return {"http": chosen_proxy_url, "https": chosen_proxy_url}
            else:
                self.logger.debug(f"No SIMULATED proxy selected for {platform_context} in this instance (IP rotation enabled but no proxy returned).")
                return None
        return None # IP rotation not enabled

    def simulate_human_like_delay(self, operation_type: str = "general_api_call"):
        """
        Introduces a random delay to simulate human-like pauses between operations.
        The duration of the delay can vary based on the type of operation.

        Args:
            operation_type (str, optional): A descriptor for the type of operation,
                which can influence the delay range (e.g., "upload", "api_query", "ui_interaction").
                Defaults to "general_api_call".

        USER NOTE: This adds small, random pauses to make the system's actions seem less robotic.
                   It's part of trying to be a "good citizen" on the internet, but
                   should not be used to circumvent platform rules aggressively.

        DEV NOTE: Delay ranges should be carefully considered. Too short might be ineffective;
                  too long will slow down the system. The 'behavioral_randomization'
                  config can provide base parameters for these delays.
        """
        base_jitter_minutes = self.config_anti_ban.get("behavioral_randomization", {}).get("upload_time_jitter_minutes", 5)
        min_delay_sec, max_delay_sec = 1.0, 5.0 # Default range

        if operation_type == "upload":
            # Uploads are typically longer, so allow for more significant, variable delays before/after.
            min_delay_sec = 3.0
            max_delay_sec = 10.0 + (base_jitter_minutes * 60 * 0.1) # Add 10% of jitter as variable max
        elif operation_type == "api_query":
            min_delay_sec = 0.5
            max_delay_sec = 3.0
        elif operation_type == "ui_interaction": # If simulating browser actions
            min_delay_sec = 1.5
            max_delay_sec = 7.0
        # Add more operation types and their typical delay ranges as needed.

        # Ensure min is less than max after adjustments
        if min_delay_sec >= max_delay_sec:
            max_delay_sec = min_delay_sec + 1.0 # Ensure max is always greater

        delay_duration = random.uniform(min_delay_sec, max_delay_sec)
        self.logger.debug(f"Simulating human-like delay for operation '{operation_type}': {delay_duration:.2f} seconds.")
        time.sleep(delay_duration)

    def get_active_account_credential(self, platform_name: str) -> str:
        """
        Selects an API credential (e.g., API key, access token) for the given platform.
        If account cycling is enabled, it would pick from a pool of accounts.
        Otherwise, it uses the primary configured credential for that platform.

        Args:
            platform_name (str): The name of the platform (e.g., "youtube", "tiktok").

        Returns:
            str: The API credential string. Returns a placeholder or raises an error
                 if no suitable credential can be found.

        USER NOTE: This function manages which account/API key is used for a platform.
                   If you have multiple accounts for a platform (advanced setup), this
                   could cycle through them. Usually, it just picks the main API key
                   you've set in the 'secrets' part of the configuration.

        DEV NOTE: SIMULATED account cycling. A real AccountManager would track usage,
                  cooldowns, and status for each account in the pool.
                  The credential returned should be the actual API key/token.
                  This method centralizes credential fetching.
        """
        if self.config_anti_ban.get("account_cycling_enabled") and self.config_anti_ban.get("account_cycling_pool_id"):
            # --- SIMULATED Account Cycling ---
            # In a real system:
            # account_id_or_key_name = self.account_manager.get_next_account_credential_key(platform_name)
            # self.logger.debug(f"Using account cycling for {platform_name}. Selected account key name: {account_id_or_key_name} (SIMULATED)")
            # chosen_credential = self.config_main.secrets.get(account_id_or_key_name)
            # if not chosen_credential or "env_placeholder_" in chosen_credential:
            #     logger.error(f"Account cycling selected key '{account_id_or_key_name}' for {platform_name}, but it's missing or a placeholder in secrets. Falling back.")
            # else:
            #     return chosen_credential
            # For simulation, let's pretend it sometimes picks an alternative if one was defined in secrets:
            simulated_alternative_key_name = f"{platform_name.upper()}_API_ALT_ACCOUNT"
            if simulated_alternative_key_name in self.config_main.secrets and random.choice([True, False]):
                alt_credential = self.config_main.secrets[simulated_alternative_key_name]
                if not "env_placeholder_" in alt_credential:
                    self.logger.info(f"SIMULATED: Account cycling selected alternative credential '{simulated_alternative_key_name}' for {platform_name}.")
                    return alt_credential


        # Fallback to the primary configured credential for the platform.
        platform_config = self.config_main.platform_ops.get(platform_name, {})
        api_credential_id_key = platform_config.get("api_credentials_id")

        if not api_credential_id_key:
            logger.error(f"No 'api_credentials_id' configured for platform '{platform_name}'. Cannot retrieve API key.")
            # Depending on strictness, could raise an error here.
            return f"ERROR_NO_CREDENTIAL_ID_FOR_{platform_name.upper()}"

        credential = self.config_main.secrets.get(api_credential_id_key)

        if not credential:
            logger.error(f"API credential ID '{api_credential_id_key}' for platform '{platform_name}' not found in 'secrets' configuration.")
            return f"ERROR_CREDENTIAL_NOT_FOUND_FOR_{api_credential_id_key.upper()}"
        if "env_placeholder_" in credential:
            logger.warning(f"Using PLACEHOLDER API key '{api_credential_id_key}' for platform '{platform_name}'. Real operations will likely fail.")

        self.logger.debug(f"Using primary credential '{api_credential_id_key}' for {platform_name}.")
        return credential

# --- Monetization ---
class MonetizationManager:
    """
    Manages all aspects of content monetization within AutoCreatorX.

    This includes strategies like ad revenue optimization (calculating ad breaks),
    incorporating affiliate links, promoting digital products, and applying
    sponsorship disclosures. It also handles tracking revenue from various sources.

    USER NOTE: This module helps you potentially earn money from the content created.
               You can enable/disable different monetization strategies in the 'monetization'
               section of the configuration file. For example, you can provide lists of
               relevant product categories for affiliate marketing or details of your own
               digital products to promote.

    DEV NOTE: Most monetization actions (API calls to affiliate platforms, ad networks)
              are SIMULATED. A production system would require robust integrations with these
              third-party services. Revenue tracking would also typically involve a database.
    """
    def __init__(self, config: AutoCreatorXConfig):
        """
        Initializes the MonetizationManager.

        Args:
            config (AutoCreatorXConfig): The main system configuration object.
        """
        self.config_monetization = config.monetization # Specific monetization settings
        self.global_config = config # Access to global settings like project paths, platform ops
        self.logger = logging.getLogger("MonetizationManager")

        # DEV NOTE: Initialize actual client instances for ad networks, affiliate platforms, etc.
        # self.ad_optimizer = AdOptimizer(self.config_monetization.get("ad_revenue_optimization"), config.secrets) if self.config_monetization.get("ad_revenue_optimization", {}).get("enabled") else None
        # self.affiliate_linker = AffiliateLinker(self.config_monetization.get("affiliate_marketing"), config.secrets) if self.config_monetization.get("affiliate_marketing", {}).get("enabled") else None
        # self.revenue_tracker = RevenueTrackerDB() if self.config_monetization.get("revenue_tracking_enabled") else None

        if self.config_monetization["enabled"]:
            self.logger.info(f"MonetizationManager initialized. Enabled strategies: {self.config_monetization.get('strategies')}")
        else:
            self.logger.info("MonetizationManager initialized, but monetization is globally DISABLED in config.")

    def apply_monetization_strategies(self,
                                      script_object: Dict,
                                      metadata_object: Dict,
                                      video_duration_seconds: int,
                                      topic_title: str,
                                      target_platform: str) -> Tuple[Dict, Dict]:
        """
        Applies all configured and relevant monetization strategies to the script and metadata.

        This is a central method that orchestrates calls to more specific monetization functions
        like ad break calculation, affiliate link insertion, etc.

        Args:
            script_object (Dict): The script object, potentially to be modified (e.g., adding call-outs).
            metadata_object (Dict): The metadata object (titles, descriptions, tags),
                                    potentially to be modified (e.g., adding affiliate links to description).
                                    It's expected to have a structure like:
                                    `{"variants": [{"title": "t", "description": "d", "tags": []}], "chosen_variant_index": 0}`
                                    or platform-specific metadata like:
                                    `{"youtube": {"variants": [...]}, "tiktok": {"variants": [...]}}`
            video_duration_seconds (int): The estimated duration of the video in seconds.
            topic_title (str): The title of the content's main topic, used for relevance.
            target_platform (str): The primary platform this content is being prepared for (e.g., "youtube").
                                   Some strategies might be platform-specific.

        Returns:
            Tuple[Dict, Dict]: A tuple containing the (potentially) modified script_object
                               and metadata_object.

        USER NOTE: This is where the system tries to weave in things like ad suggestions,
                   affiliate links, or promotions for your products, based on your settings.
        """
        if not self.config_monetization["enabled"]:
            # If monetization is globally disabled, return objects unmodified.
            return script_object, metadata_object

        self.logger.info(f"Applying monetization strategies for topic '{topic_title}' on platform '{target_platform}'.")

        # Make copies to avoid modifying originals if they are used elsewhere before this stage.
        # Though in the current orchestrator flow, they are typically passed sequentially.
        modified_script = script_object.copy()
        modified_metadata = metadata_object.copy()


        # Strategy 1: Ad Revenue Optimization (calculates ad breaks)
        # This primarily affects metadata by adding suggested ad break timestamps.
        if "ad_revenue" in self.config_monetization.get("strategies", []) and \
           self.config_monetization.get("ad_revenue_optimization", {}).get("enabled"):

            platform_ad_config = self.global_config.platform_ops.get(target_platform, {}).get("monetization", {})
            platform_ad_break_strategy = platform_ad_config.get("ad_break_strategy")

            if platform_ad_config.get("enabled") and platform_ad_break_strategy:
                self.logger.debug(f"Calculating ad breaks for {target_platform} with strategy: {platform_ad_break_strategy}")
                ad_breaks_timestamps = Utilities.calculate_optimal_ad_breaks(
                    video_duration_seconds,
                    platform_ad_break_strategy,
                    script_object.get("structure") # Pass script structure if available for AI strategies
                )
                if ad_breaks_timestamps:
                    # Store ad breaks in the metadata for the specific platform.
                    # Ensure metadata structure can hold platform-specific ad break info.
                    # If metadata_object is global (not platform-specific yet), we add it to the chosen variant.
                    # If metadata_object is already platform-specific, we target that.

                    meta_to_update = None
                    if target_platform in modified_metadata and "variants" in modified_metadata[target_platform]:
                        # Platform-specific metadata exists
                        chosen_idx = modified_metadata[target_platform].get("chosen_variant_index", 0)
                        if chosen_idx < len(modified_metadata[target_platform]["variants"]):
                           meta_to_update = modified_metadata[target_platform]["variants"][chosen_idx]
                    elif "variants" in modified_metadata: # Global metadata variants
                        chosen_idx = modified_metadata.get("chosen_variant_index", 0)
                        if chosen_idx < len(modified_metadata["variants"]):
                            meta_to_update = modified_metadata["variants"][chosen_idx]

                    if meta_to_update:
                        meta_to_update["ad_breaks_timestamps_seconds"] = ad_breaks_timestamps
                        self.logger.info(f"Added suggested ad breaks for {target_platform}: {ad_breaks_timestamps} to metadata.")
                    else:
                        self.logger.warning(f"Could not find a valid metadata variant to add ad breaks for {target_platform}.")
            else:
                self.logger.debug(f"Ad revenue or ad break strategy not enabled/configured for platform '{target_platform}'. Skipping ad break calculation.")


        # Strategy 2: Affiliate Marketing
        if "affiliate_marketing" in self.config_monetization.get("strategies", []) and \
           self.config_monetization.get("affiliate_marketing", {}).get("enabled"):
            modified_script, modified_metadata = self._incorporate_affiliate_links(
                modified_script, modified_metadata, topic_title, target_platform
            )

        # Strategy 3: Digital Product Promotion
        if "digital_product_promotion" in self.config_monetization.get("strategies", []) and \
           self.config_monetization.get("digital_product_promotion", {}).get("enabled"):
            modified_script, modified_metadata = self._incorporate_digital_product_promotion(
                modified_script, modified_metadata, target_platform
            )

        # Strategy 4: Sponsorship Tags
        if "sponsorship_tags" in self.config_monetization.get("strategies", []) and \
            self.config_monetization.get("sponsorship_tags", {}).get("enabled"):
            modified_metadata = self._apply_sponsorship_tags(
                modified_metadata, target_platform
            )

        return modified_script, modified_metadata

    def _incorporate_affiliate_links(self,
                                     script_obj: Dict,
                                     metadata_obj: Dict,
                                     topic_title: str,
                                     target_platform: str) -> Tuple[Dict, Dict]:
        """
        Attempts to incorporate affiliate links into the script (e.g., call-outs)
        and metadata (e.g., links in description). (SIMULATED)

        Args:
            script_obj (Dict): The script object.
            metadata_obj (Dict): The metadata object.
            topic_title (str): The main topic of the video.
            target_platform (str): The platform for which metadata is being prepared.

        Returns:
            Tuple[Dict, Dict]: Modified script and metadata objects.

        USER NOTE: If you've enabled 'affiliate_marketing' and configured 'product_categories',
                   this function will try to find relevant products (simulated) and suggest
                   mentioning them or adding links.

        DEV NOTE: SIMULATED. Real implementation requires:
                  1. NLP to analyze script/topic for product keywords.
                  2. API integration with affiliate platforms (e.g., Amazon PAAPI) to search for
                     relevant products based on keywords and configured categories.
                  3. Logic to gracefully insert mentions into script (e.g., add to CTA section)
                     and links into metadata descriptions.
                  4. Ensure link cloaking/shortening if desired.
                  5. Adhere to disclosure requirements (e.g., "As an Amazon Associate...").
        """
        aff_config = self.config_monetization.get("affiliate_marketing", {})
        if not aff_config.get("enabled") or not aff_config.get("auto_link_insertion_enabled"):
            return script_obj, metadata_obj # Return original if feature is off

        self.logger.info(f"Attempting to incorporate affiliate links for topic: '{topic_title}' on platform '{target_platform}'. (SIMULATED)")
        simulated_links_added_count = 0
        product_categories_to_target = aff_config.get("product_categories", [])

        # --- SIMULATED Affiliate Link Insertion Logic ---
        script_narration_lower = script_obj.get("narration_text", "").lower() # Full script text for keyword search
        topic_lower = topic_title.lower()

        for category in product_categories_to_target:
            # Check if the category keyword is mentioned in the script or topic
            if category.lower() in script_narration_lower or category.lower() in topic_lower:
                # SIMULATE finding a relevant product for this category
                simulated_product_name = f"Top Recommended {category} for {topic_title[:25]}"
                # SIMULATE generating an affiliate link
                # DEV NOTE: Real affiliate links need proper generation via API and tracking IDs.
                simulated_affiliate_link = f"https://affiliate.example.com/{Utilities.slugify(simulated_product_name)}?ref={self.global_config.instance_id}&platform={target_platform}"

                # 1. Modify script (e.g., add a line to the Call To Action)
                # This is a simple modification; more advanced would be contextual insertion.
                cta_section = script_obj.get("call_to_action", "")
                if cta_section: # Check if 'call_to_action' key exists and is not empty
                    script_obj["call_to_action"] = cta_section + f" Check out our recommended {category.split(' ')[0]} product in the description!"
                else: # If no 'call_to_action' or it's empty, initialize or append differently
                    script_obj["call_to_action"] = f"Find links to recommended {category.split(' ')[0]} products in the description!"
                self.logger.debug(f"Added affiliate mention for '{simulated_product_name}' to script's call_to_action.")

                # 2. Modify metadata (add link to description of the chosen variant)
                # This needs to handle both global metadata and platform-specific metadata structures.
                meta_variant_to_update = None
                description_prefix = f"\n\n✨ Recommended {category}:\n- {simulated_product_name}: {simulated_affiliate_link}"
                disclosure_text = "\n(As an affiliate, I may earn from qualifying purchases. This helps support the channel!)" # Example disclosure

                if target_platform in metadata_obj and "variants" in metadata_obj[target_platform]:
                    chosen_idx = metadata_obj[target_platform].get("chosen_variant_index", 0)
                    if chosen_idx < len(metadata_obj[target_platform]["variants"]):
                        meta_variant_to_update = metadata_obj[target_platform]["variants"][chosen_idx]
                elif "variants" in metadata_obj:
                    chosen_idx = metadata_obj.get("chosen_variant_index", 0)
                    if chosen_idx < len(metadata_obj["variants"]):
                        meta_variant_to_update = metadata_obj["variants"][chosen_idx]
                
                if meta_variant_to_update:
                    current_desc = meta_variant_to_update.get("description", "")
                    meta_variant_to_update["description"] = current_desc + description_prefix
                    # Add disclosure if not already present (simple check)
                    if disclosure_text.lower().split(' ')[1] not in current_desc.lower() and disclosure_text.lower().split(' ')[1] not in description_prefix.lower() :
                        meta_variant_to_update["description"] += disclosure_text
                    self.logger.debug(f"Added affiliate link for '{simulated_product_name}' to metadata description for {target_platform}.")
                else: # Fallback: create basic metadata structure if missing
                    if target_platform not in metadata_obj: metadata_obj[target_platform] = {}
                    if "variants" not in metadata_obj[target_platform]: metadata_obj[target_platform]["variants"] = [{"description":""}]
                    metadata_obj[target_platform]["variants"][0]["description"] += description_prefix + disclosure_text
                    metadata_obj[target_platform]["chosen_variant_index"] = 0
                    self.logger.debug(f"Created basic metadata and added affiliate link for '{simulated_product_name}' for {target_platform}.")


                simulated_links_added_count += 1
                if simulated_links_added_count >= 2: # Limit to 2 simulated links for brevity
                    break
        if simulated_links_added_count > 0:
             self.logger.info(f"Successfully incorporated {simulated_links_added_count} (simulated) affiliate links/mentions for '{topic_title}' on {target_platform}.")
        else:
            self.logger.info(f"No relevant (simulated) affiliate link opportunities found for '{topic_title}'.")

        return script_obj, metadata_obj

    def _incorporate_digital_product_promotion(self,
                                               script_obj: Dict,
                                               metadata_obj: Dict,
                                               target_platform: str) -> Tuple[Dict, Dict]:
        """
        Incorporates promotions for the user's own digital products into script and metadata. (SIMULATED)

        Args:
            script_obj (Dict): The script object.
            metadata_obj (Dict): The metadata object.
            target_platform (str): The platform for which metadata is being prepared.

        Returns:
            Tuple[Dict, Dict]: Modified script and metadata objects.

        USER NOTE: If you've enabled 'digital_product_promotion' and listed your products
                   in the config, this function will try to add mentions of them.
        """
        promo_config = self.config_monetization.get("digital_product_promotion", {})
        if not promo_config.get("enabled") or not promo_config.get("products"):
            return script_obj, metadata_obj # Return original if feature is off or no products listed

        self.logger.info(f"Attempting to incorporate digital product promotions on platform '{target_platform}'. (SIMULATED)")

        # --- SIMULATED Digital Product Promotion Logic ---
        # For simplicity, pick one product randomly to promote if multiple are defined.
        # A more advanced system might choose based on relevance to the video topic.
        available_products = promo_config.get("products", [])
        if not available_products:
            self.logger.debug("No digital products listed in configuration for promotion.")
            return script_obj, metadata_obj

        chosen_product = random.choice(available_products)
        product_name = chosen_product.get("name", "Our Exclusive Product")
        product_link = chosen_product.get("link", "https://example.com/yourproduct")

        # 1. Modify script (e.g., add to Call To Action)
        promo_text_for_script = f" Want to learn even more? Check out our '{product_name}'!"
        cta_section = script_obj.get("call_to_action", "")
        if cta_section:
            script_obj["call_to_action"] = cta_section + promo_text_for_script
        else:
            script_obj["call_to_action"] = promo_text_for_script
        self.logger.debug(f"Added promotion for '{product_name}' to script's call_to_action.")

        # 2. Modify metadata (add link to description)
        promo_text_for_metadata = f"\n\n🚀 Get Exclusive Access:\n- {product_name}: {product_link}"
        
        meta_variant_to_update = None
        if target_platform in metadata_obj and "variants" in metadata_obj[target_platform]:
            chosen_idx = metadata_obj[target_platform].get("chosen_variant_index", 0)
            if chosen_idx < len(metadata_obj[target_platform]["variants"]):
                meta_variant_to_update = metadata_obj[target_platform]["variants"][chosen_idx]
        elif "variants" in metadata_obj:
            chosen_idx = metadata_obj.get("chosen_variant_index", 0)
            if chosen_idx < len(metadata_obj["variants"]):
                meta_variant_to_update = metadata_obj["variants"][chosen_idx]

        if meta_variant_to_update:
            meta_variant_to_update["description"] = meta_variant_to_update.get("description", "") + promo_text_for_metadata
            self.logger.debug(f"Added promotion for '{product_name}' to metadata description for {target_platform}.")
        else: # Fallback: create basic metadata structure if missing
            if target_platform not in metadata_obj: metadata_obj[target_platform] = {}
            if "variants" not in metadata_obj[target_platform]: metadata_obj[target_platform]["variants"] = [{"description":""}]
            metadata_obj[target_platform]["variants"][0]["description"] += promo_text_for_metadata
            metadata_obj[target_platform]["chosen_variant_index"] = 0
            self.logger.debug(f"Created basic metadata and added promotion for '{product_name}' for {target_platform}.")


        self.logger.info(f"Successfully incorporated (simulated) promotion for digital product '{product_name}'.")
        return script_obj, metadata_obj

    def _apply_sponsorship_tags(self,
                                metadata_obj: Dict,
                                target_platform: str) -> Dict:
        """
        Applies sponsorship disclosure tags/text to metadata if configured.

        Args:
            metadata_obj (Dict): The metadata object.
            target_platform (str): The platform for which metadata is being prepared.

        Returns:
            Dict: Modified metadata object.

        USER NOTE: If 'sponsorship_tags' is enabled and you've set a 'disclosure_text'
                   (like "#ad" or "#sponsored"), this will add it to the video description
                   and potentially as a tag. This is important for transparency if your
                   content is sponsored.
        """
        spons_config = self.config_monetization.get("sponsorship_tags", {})
        if not spons_config.get("enabled"):
            return metadata_obj

        disclosure_text = spons_config.get("disclosure_text", "#ad") # Default to #ad if not specified
        if not disclosure_text: # If disclosure_text is empty, do nothing
            self.logger.warning("Sponsorship tagging enabled, but 'disclosure_text' is empty in config. Skipping.")
            return metadata_obj

        self.logger.info(f"Applying sponsorship tags/disclosure for platform '{target_platform}'. (SIMULATED)")

        # Add to description (often required at the beginning or clearly visible)
        # Ensure it's added to the correct metadata variant.
        meta_variant_to_update = None
        if target_platform in metadata_obj and "variants" in metadata_obj[target_platform]:
            chosen_idx = metadata_obj[target_platform].get("chosen_variant_index", 0)
            if chosen_idx < len(metadata_obj[target_platform]["variants"]): # Check index bounds
                meta_variant_to_update = metadata_obj[target_platform]["variants"][chosen_idx]
        elif "variants" in metadata_obj: # Global metadata
            chosen_idx = metadata_obj.get("chosen_variant_index", 0)
            if chosen_idx < len(metadata_obj["variants"]): # Check index bounds
                meta_variant_to_update = metadata_obj["variants"][chosen_idx]
        
        if meta_variant_to_update:
            current_description = meta_variant_to_update.get("description", "")
            # Add disclosure if not already present (simple check for the text itself)
            if disclosure_text.lower() not in current_description.lower():
                meta_variant_to_update["description"] = f"{disclosure_text}\n\n{current_description}".strip()
                self.logger.debug(f"Added sponsorship disclosure '{disclosure_text}' to description for {target_platform}.")

            # Add to tags/keywords if applicable for the platform (e.g., YouTube tags)
            # The tag should usually be without the '#' symbol.
            tag_to_add = disclosure_text.lstrip('#').strip()
            if tag_to_add: # Ensure tag is not empty after stripping
                if "tags" not in meta_variant_to_update:
                    meta_variant_to_update["tags"] = []
                # Add tag if not already present (case-insensitive check for tags)
                if not any(existing_tag.lower() == tag_to_add.lower() for existing_tag in meta_variant_to_update["tags"]):
                    meta_variant_to_update["tags"].append(tag_to_add)
                    self.logger.debug(f"Added sponsorship tag '{tag_to_add}' to metadata tags for {target_platform}.")
        else:
             self.logger.warning(f"Could not find a valid metadata variant to apply sponsorship tags for {target_platform}.")


        return metadata_obj

    def track_revenue(self, platform: str, video_id: str, analytics_data: Dict[str, Any]):
        """
        Tracks (simulated) revenue generated by a specific video.

        This function would typically fetch actual revenue data from platform APIs
        and store it for analysis and reporting.

        Args:
            platform (str): The platform name (e.g., "youtube").
            video_id (str): The unique identifier of the video on the platform.
            analytics_data (Dict[str, Any]): Performance data for the video, which might
                                             include estimated revenue metrics from the platform.

        USER NOTE: If 'revenue_tracking_enabled' is on, the system tries to log how
                   much money (estimated) each video makes. This is a simplified simulation.

        DEV NOTE: SIMULATED. Real implementation requires:
                  1. API integration with platform analytics (e.g., YouTube Analytics API's
                     `estimatedRevenue` metric).
                  2. A robust storage mechanism (database or structured files) for revenue data,
                     linked to video IDs, dates, and revenue sources (ads, affiliate, etc.).
                  3. Handling of different currencies and conversion if necessary.
        """
        if not self.config_monetization["enabled"] or not self.config_monetization.get("revenue_tracking_enabled"):
            self.logger.debug("Revenue tracking is disabled. Skipping.")
            return

        self.logger.debug(f"Attempting to track (simulated) revenue for video '{video_id}' on platform '{platform}'.")

        # --- SIMULATED Revenue Tracking Logic ---
        # In a real system, 'estimatedRevenue' or similar would come from `analytics_data`
        # fetched from the platform's API.
        estimated_revenue = analytics_data.get("estimatedRevenue", analytics_data.get("simulated_revenue", random.uniform(0.1, 25.0))) # Simulate if not directly provided
        currency = analytics_data.get("currencyCode", "USD") # Assume USD if not specified

        # Store this data. For simulation, append to a CSV file in the project's monetization_data directory.
        # DEV NOTE: A database would be more suitable for production for querying and aggregation.
        report_filename = f"{platform}_revenue_summary.csv"
        report_path = os.path.join(self.global_config.current_project_dir, "10_monetization_data", report_filename)

        try:
            file_exists = os.path.isfile(report_path)
            with open(report_path, "a", encoding='utf-8') as f:
                if not file_exists or os.stat(report_path).st_size == 0:
                    # Write header if file is new or empty
                    f.write("timestamp_utc,video_id,platform,estimated_revenue,currency,source_metric\n")
                # Append the new revenue data
                # Source metric indicates where the revenue number came from (e.g. direct API, simulation)
                source_metric = "platform_api" if "estimatedRevenue" in analytics_data else "simulated_placeholder"
                f.write(f"{datetime.utcnow().isoformat()},{video_id},{platform},{estimated_revenue:.2f},{currency},{source_metric}\n")
            self.logger.info(f"Successfully tracked (simulated) revenue: {currency} {estimated_revenue:.2f} for video '{video_id}' on '{platform}'. Saved to report.")
        except IOError as e:
            self.logger.error(f"Failed to write to revenue tracking report '{report_path}' for video '{video_id}': {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during revenue tracking for video '{video_id}': {e}", exc_info=True)

# --- Core Modules ---



class IntelligenceCore:
    def __init__(self, config_obj: AutoCreatorXConfig, anti_detection: AntiDetection):
        self.config = config_obj.intelligence_core
        self.global_config = config_obj
        self.secrets = config_obj.secrets
        self.anti_detection = anti_detection
        self.logger = logging.getLogger("IntelligenceCore")
        # --- Initialize API clients (conceptual) ---
        # self.llm_client = LLMClientWrapper(self.config["script_generation"]["model"], self.secrets, ...)
        # self.metadata_client = LLMClientWrapper(self.config["metadata_generation"]["model"], ...)
        # self.sentiment_client = NLPClientWrapper(self.config["sentiment_analysis"]["model"], ...)
        # self.fact_checker = KGClientWrapper(self.config["factual_validation"]["model"], ...)
        self.logger.info("Intelligence Core initialized.")

    def analyze_trends_and_select_topic(self) -> Optional[Dict[str, Any]]:
        """Analyzes trends and selects a viable topic."""
        if not self.global_config.trend_analysis["enabled"]:
            self.logger.warning("Trend analysis is disabled. No topic will be selected.")
            # Fallback: use a predefined topic or allow manual input
            return {"topic_id": "fallback_topic_001", "title": "Generic Interesting Topic", "keywords": ["general", "interesting"], "source": "fallback", "virality_score": 50, "sentiment": {"positive": 0.5, "neutral": 0.5, "negative": 0.0}}

        self.logger.info("Starting trend analysis and topic selection.")
        all_potential_trends = []
        sources = self.global_config.trend_analysis["primary_sources"] + self.global_config.trend_analysis["secondary_sources"]

        for source_api_name in sources:
            attempt = 1
            max_retries = self.global_config.max_step_retries
            retry_delay = self.global_config.error_retry_delay_minutes
            while attempt <= max_retries:
                try:
                    self.anti_detection.simulate_human_like_delay("api_call")
                    # --- Simulated API call to trend source ---
                    self.logger.debug(f"Fetching trends from {source_api_name} (Attempt {attempt})...")
                    # request_headers = self.anti_detection.get_request_headers(source_api_name)
                    # request_proxy = self.anti_detection.get_request_proxy(source_api_name)
                    # trends_from_source = actual_api_call(source_api_name, headers=request_headers, proxy=request_proxy, keywords=self.global_config.trend_analysis["niche_focus_keywords"])
                    
                    # Simulated response
                    trends_from_source = [{
                        "topic_id": f"{source_api_name}_{random.randint(1000,9999)}",
                        "title": f"Hot Topic from {source_api_name}: Keyword {random.choice(self.global_config.trend_analysis.get('niche_focus_keywords', ['AI']))} {random.randint(1,100)}",
                        "keywords": random.sample(self.global_config.trend_analysis.get('niche_focus_keywords', ['AI', 'tech']) + ['news', 'update'], 2),
                        "source": source_api_name,
                        "raw_virality": random.randint(50, 100),
                        "raw_sentiment_score": random.uniform(-1, 1),
                        "link": f"https://example.com/trends/{Utilities.slugify(f'Hot Topic from {source_api_name}')}"
                    } for _ in range(random.randint(1,3))] # Simulate getting 1-3 trends per source

                    self.logger.info(f"Successfully fetched {len(trends_from_source)} potential trends from {source_api_name}.")
                    all_potential_trends.extend(trends_from_source)
                    break # Success
                except Exception as e:
                    self.logger.error(f"Error fetching trends from {source_api_name}: {e}")
                    if not ErrorHandling.handle_step_error(f"TrendSource_{source_api_name}", e, attempt, max_retries, retry_delay, self.global_config.safety_systems["failback_mechanisms"]["trend_analysis"]):
                        # Permanent failure for this source after retries
                        # Potentially use a failback for this specific source, or just move on
                        break
                    attempt += 1
        
        if not all_potential_trends:
            self.logger.warning("No potential trends found from any source.")
            # Implement failback strategy from config (e.g., use_cached_or_fallback_topics)
            failback_strategy = self.global_config.safety_systems["failback_mechanisms"]["trend_analysis"]
            if "use_cached_or_fallback_topics" in failback_strategy:
                self.logger.info("Using fallback topic due to no trends found.")
                return {"topic_id": "fallback_topic_002", "title": "The Future of Everything", "keywords": ["future", "technology"], "source": "system_fallback", "virality_score": 60, "sentiment": {"positive": 0.6}}
            return None

        # --- Filtering and Scoring ---
        viable_trends = self._filter_and_score_trends(all_potential_trends)

        if not viable_trends:
            self.logger.warning("No viable trends after filtering and scoring.")
            return None # Or fallback

        # --- Select the best trend (e.g., highest score) ---
        selected_trend = max(viable_trends, key=lambda t: t.get("final_score", 0))
        self.logger.info(f"Selected Trend: '{selected_trend['title']}' (Score: {selected_trend.get('final_score',0)}) from {selected_trend['source']}")
        
        # Save trend analysis details
        trend_file = os.path.join(self.global_config.current_project_dir, "1_trends_analysis", f"{Utilities.slugify(selected_trend['title'])}_analysis.json")
        try:
            with open(trend_file, 'w') as f:
                json.dump(selected_trend, f, indent=4)
        except Exception as e:
            self.logger.error(f"Could not save trend analysis file: {e}")

        return selected_trend

    def _filter_and_score_trends(self, trends: List[Dict]) -> List[Dict]:
        """Filters trends based on config and scores them."""
        filtered = []
        cfg_trend = self.global_config.trend_analysis
        min_virality = cfg_trend["min_virality_score"]
        exclusions = cfg_trend["exclude_topics_containing"]
        niche_keywords = cfg_trend.get("niche_focus_keywords", [])

        for trend in trends:
            title_lower = trend["title"].lower()
            # Exclusion filter
            if any(ex_word in title_lower for ex_word in exclusions):
                self.logger.debug(f"Excluding trend '{trend['title']}' due to exclusion keywords.")
                continue
            # Niche filter (if keywords are defined)
            if niche_keywords and not any(niche_kw.lower() in title_lower for niche_kw in niche_keywords):
                 self.logger.debug(f"Excluding trend '{trend['title']}' due to not matching niche keywords.")
                 continue
            
            # Virality Score
            virality_score = trend.get("raw_virality", 0)
            if virality_score < min_virality:
                self.logger.debug(f"Excluding trend '{trend['title']}' (Virality: {virality_score} < {min_virality}).")
                continue

            # Sentiment Analysis (simulated - actual would call sentiment model)
            raw_sentiment = trend.get("raw_sentiment_score", 0) # Assume -1 to 1
            sentiment_map = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
            if raw_sentiment > cfg_trend["sentiment_thresholds"]["positive"]: sentiment_map["positive"] = raw_sentiment
            elif raw_sentiment < -cfg_trend["sentiment_thresholds"]["negative"]: sentiment_map["negative"] = abs(raw_sentiment)
            else: sentiment_map["neutral"] = 1.0 - (abs(raw_sentiment)/max(cfg_trend["sentiment_thresholds"]["positive"],cfg_trend["sentiment_thresholds"]["negative"] )) # Simple neutral score
            trend["sentiment_analysis"] = sentiment_map

            # (Conceptual) Time Series Analysis: Predict longevity/peak
            if cfg_trend["time_series_analysis_enabled"]:
                trend["predicted_longevity_days"] = random.randint(3, 14) # Simulated
                trend["final_score"] = virality_score * (1 + sentiment_map["positive"] - sentiment_map["negative"]) * (trend["predicted_longevity_days"]/7)
            else:
                trend["final_score"] = virality_score * (1 + sentiment_map["positive"] - sentiment_map["negative"])
            
            filtered.append(trend)
        self.logger.info(f"Filtered {len(trends)} potential trends down to {len(filtered)} viable trends.")
        return filtered

    def generate_script_and_metadata(self, trend_data: Dict[str, Any], content_style: str) -> Optional[Tuple[Dict, Dict]]:
        """Generates script and metadata using LLMs."""
        self.logger.info(f"Generating script and metadata for topic: '{trend_data['title']}' in style '{content_style}'.")
        
        # --- Script Generation ---
        script_prompt_template_name = f"script_{content_style}_{self.global_config.global_language}"
        script_prompt = Utilities.load_prompt_template(
            script_prompt_template_name,
            self.global_config,
            topic=trend_data["title"],
            keywords=", ".join(trend_data.get("keywords", [])),
            target_audience="general public interested in " + trend_data.get("keywords", ["tech"])[0], # Example
            desired_tone="engaging and informative", # Could be dynamic
            creativity_level=self.config["creativity_level"]
        )
        if "Error:" in script_prompt:
            self.logger.error("Failed to load script prompt template. Aborting script generation.")
            return None

        # --- Simulated LLM call for script ---
        self.logger.debug("Simulating LLM call for script generation...")
        # llm_script_response = self.llm_client.generate(script_prompt, self.config["script_generation"]["parameters"])
        # This would be a structured JSON ideally, or parsable text.
        simulated_llm_script_response = {
            "title_suggestion": f"The Amazing Truth About {trend_data['title']}",
            "hook": f"You won't BELIEVE what's new with {trend_data['title']}!",
            "sections": [
                {"id": "intro", "heading": "Introduction", "narration": f"Let's dive into {trend_data['title']}.", "visual_cue": "Dynamic intro animation"},
                {"id": "main_point_1", "heading": "Key Aspect 1", "narration": "Firstly, consider this important detail...", "visual_cue": "Informative graphic"},
                {"id": "main_point_2", "heading": "Key Aspect 2", "narration": "Secondly, another crucial point is...", "visual_cue": "Supporting b-roll footage"},
                {"id": "conclusion", "heading": "Conclusion", "narration": f"In summary, {trend_data['title']} is truly fascinating.", "visual_cue": "Recap slide"},
            ],
            "call_to_action": "Like, subscribe, and comment below with your thoughts!",
            "estimated_duration_minutes": random.randint(3,10),
            "language": self.global_config.global_language
        }
        # For simplicity, combining narration for full text
        simulated_llm_script_response["narration_text"] = "\n".join(
            [simulated_llm_script_response["hook"]] +
            [s["narration"] for s in simulated_llm_script_response["sections"]] +
            [simulated_llm_script_response["call_to_action"]]
        )

        script_object = simulated_llm_script_response # Assume this is the parsed output
        self.logger.info(f"Generated draft script for '{script_object['title_suggestion']}'.")

        # --- Factual Validation (if enabled) ---
        if self.config["factual_validation"]["enabled"]:
            script_object = self._validate_facts(script_object)

        # --- Content Moderation (on script text) ---
        if self.global_config.safety_systems["content_moderation"]["enabled"]:
            moderation_passed, moderation_details = self._moderate_content(script_object["narration_text"], "script")
            if not moderation_passed:
                self.logger.error(f"Script content failed moderation: {moderation_details}. Cannot proceed with this script.")
                # Handle failure: discard, manual review, or regenerate
                return None # Or trigger regeneration attempt

        # --- Metadata Generation ---
        metadata_prompt_template_name = f"metadata_{content_style}_{self.global_config.global_language}"
        metadata_prompt = Utilities.load_prompt_template(
            metadata_prompt_template_name,
            self.global_config,
            video_title=script_object["title_suggestion"],
            script_summary=script_object["narration_text"][:500], # First 500 chars as summary
            keywords=", ".join(trend_data.get("keywords", []) + script_object.get("extracted_keywords", [])), # Add keywords from script too
            num_variants=self.config["metadata_generation"]["ab_test_variants_to_generate"]
        )
        if "Error:" in metadata_prompt:
            self.logger.error("Failed to load metadata prompt template. Proceeding with basic metadata.")
            # Create basic metadata instead of full LLM gen
            metadata_object = self._generate_basic_metadata(script_object, trend_data)
        else:
            self.logger.debug("Simulating LLM call for metadata generation...")
            # metadata_llm_response = self.metadata_client.generate(metadata_prompt, self.config["metadata_generation"]["parameters"])
            # Expected: list of metadata variants (title, desc, tags)
            simulated_metadata_variants = []
            for i in range(self.config["metadata_generation"]["ab_test_variants_to_generate"]):
                simulated_metadata_variants.append({
                    "title": f"{script_object['title_suggestion']} - Option {i+1}",
                    "description": f"Explore {script_object['title_suggestion']}. We cover: {', '.join(s['heading'] for s in script_object['sections'])}. \n\n#hashtags #{Utilities.slugify(trend_data['keywords'][0] if trend_data['keywords'] else 'awesome')} #{Utilities.slugify(content_style)}",
                    "tags": trend_data.get("keywords", []) + [Utilities.slugify(s['heading']) for s in script_object['sections']] + [f"variant_{i+1}"],
                    "seo_score_estimate": random.randint(60,95) # Simulated
                })
            metadata_object = {"variants": simulated_metadata_variants, "chosen_variant_index": 0} # Default to first
            # Logic to choose the "best" variant or use for A/B testing on platforms
            if simulated_metadata_variants:
                 metadata_object["chosen_variant_index"] = max(range(len(simulated_metadata_variants)), key=lambda i: simulated_metadata_variants[i]['seo_score_estimate'])

            self.logger.info(f"Generated {len(metadata_object['variants'])} metadata variants.")

        # Save script and metadata
        script_filename = Utilities.slugify(script_object['title_suggestion'])
        with open(os.path.join(self.global_config.current_project_dir, "2_script_drafts", f"{script_filename}.json"), 'w') as f:
            json.dump(script_object, f, indent=4)
        with open(os.path.join(self.global_config.current_project_dir, "3_metadata_drafts", f"{script_filename}_meta.json"), 'w') as f:
            json.dump(metadata_object, f, indent=4)

        return script_object, metadata_object

    def _generate_basic_metadata(self, script_object: Dict, trend_data: Dict) -> Dict:
        title = script_object.get("title_suggestion", trend_data.get("title", "Untitled Video"))
        description = f"An overview of {title}.\nKeywords: {', '.join(trend_data.get('keywords', []))}"
        tags = trend_data.get("keywords", []) + [self.global_config.default_content_style]
        return {
            "variants": [{"title": title, "description": description, "tags": tags, "seo_score_estimate": 40}],
            "chosen_variant_index": 0
        }

    def _validate_facts(self, script_object: Dict) -> Dict:
        self.logger.info("Performing factual validation (simulated).")
        # --- Simulated Fact-Checking ---
        # For each claim/statement in script_object["narration_text"] or sections:
        #   Call self.fact_checker.verify(claim)
        #   If confidence < threshold, flag it or suggest alternative wording.
        # For now, just a placeholder
        script_object["factual_validation_status"] = "passed_simulated"
        script_object["flagged_statements_count"] = random.randint(0,1) # Simulate 0-1 flagged statements
        if script_object["flagged_statements_count"] > 0:
             self.logger.warning(f"Fact check flagged {script_object['flagged_statements_count']} statements. Manual review may be needed.")
        return script_object

    def _moderate_content(self, text_content: str, content_type: str) -> Tuple[bool, Dict]:
        self.logger.info(f"Performing content moderation for {content_type} (simulated).")
        # --- Simulated Moderation API Call ---
        # moderation_result = self.moderation_client.check(text_content, self.global_config.safety_systems["content_moderation"]["categories_to_check"])
        # moderation_result = {"passed": True, "flags": [], "scores": {"hate": 0.1, "violence": 0.05}}
        simulated_scores = {cat: random.uniform(0.0, 0.5) for cat in self.global_config.safety_systems["content_moderation"]["categories_to_check"]}
        
        moderation_thresholds = self.global_config.safety_systems["content_moderation"]["thresholds"]
        passed = True
        flags = []
        highest_risk_score = 0.0

        for category, score in simulated_scores.items():
            if score >= moderation_thresholds["reject"]:
                passed = False
                flags.append({"category": category, "score": score, "action": "reject"})
                highest_risk_score = max(highest_risk_score, score)
            elif score >= moderation_thresholds["manual_review"]:
                # Passed for now, but flagged for review
                flags.append({"category": category, "score": score, "action": "manual_review"})
                highest_risk_score = max(highest_risk_score, score)
        
        if not passed:
            self.logger.warning(f"Content moderation failed for {content_type}. Highest risk score: {highest_risk_score}. Flags: {flags}")
        elif flags: # Passed but needs review
            self.logger.info(f"Content moderation passed for {content_type} but requires manual review. Highest risk score: {highest_risk_score}. Flags: {flags}")
        else: # Passed cleanly
            self.logger.info(f"Content moderation passed cleanly for {content_type}.")

        return passed, {"flags": flags, "scores": simulated_scores, "overall_passed_auto": passed}


class MediaCore:
    def __init__(self, config_obj: AutoCreatorXConfig, anti_detection: AntiDetection):
        self.config = config_obj.media_core
        self.global_config = config_obj
        self.secrets = config_obj.secrets
        self.anti_detection = anti_detection
        self.logger = logging.getLogger("MediaCore")
        # --- Initialize API clients (conceptual) ---
        # self.tts_client = TTSClientWrapper(self.config["text_to_speech"]["provider"], ...)
        # self.video_gen_client = AIVideoClientWrapper(...)
        # self.image_gen_client = AIImageClientWrapper(...)
        # self.stock_footage_client = StockProviderWrapper(...)
        # self.video_editor_client = VideoEditingAPIWrapper(...)
        self.logger.info("Media Core initialized.")

    def generate_voiceover(self, script_text: str, language: str, script_title_slug: str) -> Optional[str]:
        """Generates voiceover from script text."""
        self.logger.info(f"Generating voiceover for '{script_title_slug}' in {language}.")
        tts_config = self.config["text_to_speech"]
        voice = tts_config["voice_options"].get(language, tts_config["error_handling"]["fallback_voice"])
        
        # --- Simulated TTS API Call ---
        # self.anti_detection.simulate_human_like_delay("tts_api_call")
        # audio_data = self.tts_client.synthesize(script_text, voice, tts_config["parameters"])
        # if not audio_data:
        #     # Handle error, try fallback if configured
        #     if tts_config["error_handling"]["fallback_voice"]:
        #         voice = tts_config["error_handling"]["fallback_voice"]
        #         audio_data = self.tts_client.synthesize(script_text, voice, tts_config["parameters"])
        #     if not audio_data:
        #         self.logger.error("TTS generation failed even with fallback.")
        #         return None

        output_filename = f"{script_title_slug}_voiceover_{language}.mp3"
        output_path = os.path.join(self.global_config.current_project_dir, "5_assets_processed/audio", output_filename)
        
        # Simulate saving the file
        with open(output_path, 'w') as f: # 'wb' for actual audio data
            f.write("Simulated MP3 audio data for voiceover.") 
        self.logger.info(f"Successfully generated voiceover and saved to: {output_path}")
        return output_path # Path to the generated audio file

    def procure_visual_assets(self, script_object: Dict, script_title_slug: str) -> Dict[str, List[str]]:
        """Procures visual assets (video clips, images) based on script cues."""
        self.logger.info(f"Procuring visual assets for '{script_title_slug}'.")
        assets = {"video_clips": [], "images": []}
        visual_cues = [section.get("visual_cue", "general b-roll") for section in script_object.get("sections", [])]
        
        # --- Procurement Logic (Simulated) ---
        # Iterate through self.config["visual_asset_procurement"]["priorities"]
        # For each cue, try to find/generate an asset using the highest priority method first.
        
        # Example: Simulate finding a few assets
        for i, cue in enumerate(visual_cues[:3]): # Limit for simulation
            asset_type = random.choice(["video", "image"])
            asset_filename = f"{script_title_slug}_visual_{i+1}_{Utilities.slugify(cue[:20])}.{'mp4' if asset_type == 'video' else 'jpg'}"
            
            if asset_type == "video":
                asset_path = os.path.join(self.global_config.current_project_dir, "4_assets_raw/video", asset_filename)
                with open(asset_path, 'w') as f: f.write(f"Simulated raw video for cue: {cue}")
                # Simulate processing (resize, reformat)
                processed_path = os.path.join(self.global_config.current_project_dir, "5_assets_processed/video", asset_filename)
                with open(processed_path, 'w') as f: f.write(f"Simulated processed video for cue: {cue}")
                assets["video_clips"].append(processed_path)
            else: # image
                asset_path = os.path.join(self.global_config.current_project_dir, "4_assets_raw/images", asset_filename)
                with open(asset_path, 'w') as f: f.write(f"Simulated raw image for cue: {cue}")
                processed_path = os.path.join(self.global_config.current_project_dir, "5_assets_processed/images", asset_filename)
                with open(processed_path, 'w') as f: f.write(f"Simulated processed image for cue: {cue}")
                assets["images"].append(processed_path)

            self.logger.debug(f"Procured and processed asset for cue '{cue}': {asset_filename}")
            if self.config["visual_asset_procurement"]["attribution_tracking_enabled"]:
                # Log attribution info
                pass
        
        self.logger.info(f"Procured {len(assets['video_clips'])} video clips and {len(assets['images'])} images.")
        return assets

    def select_background_music(self, mood_keywords: List[str], video_duration_seconds: int, script_title_slug: str) -> Optional[str]:
        """Selects background music."""
        self.logger.info(f"Selecting background music for '{script_title_slug}' with mood: {mood_keywords}.")
        music_cfg = self.config["background_music"]
        # --- Simulated Music Library API Call ---
        # matching_tracks = self.music_library_client.search(mood_keywords, duration_min=video_duration_seconds, license=music_cfg["license_type"])
        # selected_track = choose_best_track(matching_tracks)
        
        selected_track_filename = f"{script_title_slug}_music_{Utilities.slugify(mood_keywords[0] if mood_keywords else 'general')}.mp3"
        music_path = os.path.join(self.global_config.current_project_dir, "5_assets_processed/audio", selected_track_filename)
        with open(music_path, 'w') as f: f.write("Simulated background music audio data.")
        self.logger.info(f"Selected background music: {music_path}")
        return music_path

    def compose_video(self, script_object: Dict, voiceover_path: str, visual_assets: Dict, music_path: Optional[str], script_title_slug: str) -> Optional[str]:
        """Composes the final video using a video editing API or library."""
        self.logger.info(f"Composing final video for '{script_title_slug}'.")
        composition_cfg = self.config["video_composition"]
        
        # --- Video Editing Logic (Simulated) ---
        # Prepare timeline/instructions for the video editor API/library
        # E.g., sequence of visual_assets, voiceover timing, music volume, transitions, text overlays from script_object
        # job_id = self.video_editor_client.submit_job(timeline_instructions, composition_cfg["rendering_settings"])
        # final_video_url_or_path = self.video_editor_client.wait_for_job_completion(job_id)
        
        output_filename = f"{script_title_slug}_final_video.mp4"
        final_video_path = os.path.join(self.global_config.current_project_dir, "6_final_videos", output_filename)
        with open(final_video_path, 'w') as f: f.write("Simulated final MP4 video data.")
        
        self.logger.info(f"Video composition complete: {final_video_path}")
        # Perform copyright check on final video if configured
        if self.global_config.safety_systems["copyright_check"]["enabled"]:
            if not self._check_copyright(final_video_path):
                self.logger.error(f"Final video '{final_video_path}' failed copyright check. Aborting further processing of this video.")
                # Handle copyright failure: remove file, try different assets, or manual review
                try: os.remove(final_video_path)
                except OSError: pass
                return None
        return final_video_path

    def _check_copyright(self, media_path: str) -> bool:
        self.logger.info(f"Performing copyright check on {media_path} (simulated).")
        # --- Simulated Copyright Scan API Call ---
        # scan_result = self.copyright_scan_client.scan(media_path)
        # if scan_result.match_confidence > self.global_config.safety_systems["copyright_check"]["match_threshold_flag"]:
        #     self.logger.warning(f"Copyright match detected for {media_path}. Details: {scan_result.details}")
        #     return False
        # Assume it passes for simulation
        if random.random() < 0.05: # 5% chance of simulated failure
            self.logger.warning(f"SIMULATED: Copyright match detected for {media_path}.")
            return False
        self.logger.info(f"Copyright check passed for {media_path}.")
        return True


    def generate_thumbnail(self, video_title: str, script_object: Dict, visual_assets: Dict, script_title_slug: str) -> Optional[str]:
        """Generates a thumbnail for the video."""
        if not self.config["thumbnail_generation"]["enabled"]:
            self.logger.info("Thumbnail generation is disabled.")
            return None
            
        self.logger.info(f"Generating thumbnail for '{script_title_slug}'.")
        thumb_cfg = self.config["thumbnail_generation"]
        
        # --- Thumbnail Generation Logic (Simulated) ---
        # if thumb_cfg["method"] == "ai_generated_template":
        #     prompt = f"Create a compelling YouTube thumbnail for a video titled '{video_title}'. Style: {random.choice(thumb_cfg['template_styles'])}. Key elements: {script_object.get('hook','')}"
        #     thumbnail_image_data = self.image_gen_client.generate(prompt, thumb_cfg["ai_model"], thumb_cfg["parameters"])
        # elif thumb_cfg["method"] == "key_frame_extraction_enhanced":
        #     # Extract keyframes from video, choose best, enhance with text/graphics
        #     pass
        
        thumbnail_filename = f"{script_title_slug}_thumbnail.jpg"
        thumbnail_path = os.path.join(self.global_config.current_project_dir, "7_thumbnails", thumbnail_filename)
        with open(thumbnail_path, 'w') as f: f.write("Simulated JPEG thumbnail image data.")
        self.logger.info(f"Generated thumbnail: {thumbnail_path}")
        return thumbnail_path


class PlatformOperations:
    def __init__(self, config_obj: AutoCreatorXConfig, anti_detection: AntiDetection):
        self.config = config_obj.platform_ops
        self.global_config = config_obj
        self.secrets = config_obj.secrets
        self.anti_detection = anti_detection
        self.logger = logging.getLogger("PlatformOperations")
        # --- Initialize Platform API Clients (conceptual) ---
        # self.youtube_api = YouTubeAPIWrapper(self.secrets.get(self.config["youtube"]["api_credentials_id"]), ...)
        # self.tiktok_api = TikTokAPIWrapper(self.secrets.get(self.config["tiktok"]["api_credentials_id"]), ...)
        self.logger.info("Platform Operations initialized.")

    def upload_content_to_platforms(self, final_video_path: str, thumbnail_path: Optional[str], metadata_object: Dict, script_object: Dict) -> Dict[str, Dict]:
        """Uploads the video and metadata to all enabled platforms."""
        upload_statuses = {}
        chosen_meta_variant_index = metadata_object.get("chosen_variant_index",0)
        
        for platform_name, platform_cfg in self.config.items():
            if platform_cfg.get("enabled"):
                self.logger.info(f"Starting upload process for platform: {platform_name}")
                self.anti_detection.simulate_human_like_delay("upload")
                
                # Get the specific metadata for this platform (if variants exist per platform)
                # For now, assume metadata_object["variants"][chosen_meta_variant_index] is universal
                # but ideally, metadata_object could be structured as:
                # metadata_object = {"youtube": {"variants": [...], "chosen_variant_index":0}, "tiktok": {...}}
                
                current_metadata = metadata_object.get("variants", [])[chosen_meta_variant_index]
                if platform_name in metadata_object and "variants" in metadata_object[platform_name]: # Platform specific metadata
                    current_metadata = metadata_object[platform_name]["variants"][metadata_object[platform_name].get("chosen_variant_index",0)]
                elif "variants" not in metadata_object or not metadata_object["variants"]: # Safety net
                     self.logger.error(f"No valid metadata variants found for {platform_name}. Using basic from script.")
                     current_metadata = IntelligenceCore._generate_basic_metadata(None, script_object, {"topic_id":"unknown", "title": script_object.get("title_suggestion", "Video")})["variants"][0]


                title = current_metadata.get("title", script_object.get("title_suggestion", "Untitled Video"))
                description = current_metadata.get("description", "No description available.")
                tags = current_metadata.get("tags", [])
                ad_breaks = current_metadata.get("ad_breaks_timestamps_seconds") # From MonetizationManager step

                upload_params = {
                    "video_file_path": final_video_path,
                    "thumbnail_file_path": thumbnail_path,
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "category_id": platform_cfg.get("category_id"),
                    "privacy_status": platform_cfg.get("privacy_status"),
                    "playlist_ids": None, # Placeholder for playlist logic
                    "ad_breaks": ad_breaks, # For YouTube etc.
                    "api_key": self.anti_detection.get_active_account_credential(platform_name),
                    "headers": self.anti_detection.get_request_headers(platform_name),
                    "proxy": self.anti_detection.get_request_proxy(platform_name)
                }

                # --- Platform-Specific Logic (Simulated) ---
                try:
                    if platform_name == "youtube":
                        # video_id = self.youtube_api.upload(**upload_params)
                        video_id = f"yt_sim_{random.randint(10000,99999)}"
                        self.logger.info(f"Successfully uploaded to YouTube. Video ID: {video_id}")
                        upload_statuses[platform_name] = {"status": "success", "video_id": video_id, "platform_url": f"https://www.youtube.com/watch?v={video_id}"}
                        # Post-upload: playlist management, comment pinning, etc.
                        # self.youtube_api.add_to_playlist(video_id, platform_cfg["playlist_management"]...)

                    elif platform_name == "tiktok":
                        # video_id = self.tiktok_api.upload_video_mobile_simulated(**upload_params, aspect_ratio=platform_cfg["aspect_ratio"])
                        video_id = f"tk_sim_{random.randint(10000,99999)}"
                        self.logger.info(f"Successfully uploaded to TikTok. Video ID: {video_id}")
                        upload_statuses[platform_name] = {"status": "success", "video_id": video_id, "platform_url": f"https://www.tiktok.com/@[yourchannel]/video/{video_id}"}
                        # Post-upload: music overlay, effects
                        # self.tiktok_api.apply_trending_sound(video_id, platform_cfg["music_overlay_strategy"]...)

                    # Add other platforms here...
                    else:
                        self.logger.warning(f"Upload logic for platform '{platform_name}' is not implemented.")
                        upload_statuses[platform_name] = {"status": "not_implemented"}
                
                except Exception as e:
                    self.logger.error(f"Failed to upload to {platform_name}: {e}", exc_info=True)
                    ErrorHandling.handle_api_error(f"{platform_name}_upload", e, f"{platform_name}_upload_failback", self.global_config) # Conceptual failback key
                    upload_statuses[platform_name] = {"status": "failed", "error": str(e)}
            else:
                self.logger.debug(f"Skipping upload to {platform_name} as it's disabled in config.")
        
        # Save upload statuses
        upload_log_path = os.path.join(self.global_config.current_project_dir, "8_platform_uploads", f"{Utilities.slugify(script_object.get('title_suggestion','untitled'))}_upload_report.json")
        with open(upload_log_path, 'w') as f:
            json.dump(upload_statuses, f, indent=4)

        return upload_statuses


class FeedbackLoop:
    def __init__(self, config_obj: AutoCreatorXConfig):
        self.config = config_obj.feedback_loop
        self.global_config = config_obj # To modify global parameters
        self.secrets = config_obj.secrets
        self.logger = logging.getLogger("FeedbackLoop")
        # self.analytics_clients = { # Conceptual
        # "youtube": YouTubeAnalyticsAPI(self.secrets.get(...)),
        # "tiktok": TikTokAnalyticsAPI(self.secrets.get(...))
        # }
        self.logger.info("Feedback Loop initialized.")

    def collect_and_analyze_performance(self, upload_statuses: Dict[str, Dict]) -> Optional[Dict]:
        """Collects performance data for recently uploaded content and analyzes it."""
        if not self.config["enabled"]:
            self.logger.info("Feedback loop is disabled. Skipping performance analysis.")
            return None

        self.logger.info("Collecting and analyzing content performance data.")
        all_performance_data = {} # Keyed by platform, then video_id

        for platform_name, status_info in upload_statuses.items():
            if status_info.get("status") == "success" and platform_name in self.config["performance_data_sources"]:
                video_id = status_info["video_id"]
                self.logger.debug(f"Fetching performance data for {video_id} on {platform_name} (simulated).")
                # --- Simulated API call to platform analytics ---
                # performance_data = self.analytics_clients[platform_name].get_video_stats(video_id, self.config["metrics_to_track"])
                simulated_data = {metric: random.randint(10, 10000) for metric in self.config["metrics_to_track"]}
                simulated_data["positive_sentiment_ratio"] = random.uniform(0.3, 0.9)
                simulated_data["watch_time_ratio"] = random.uniform(0.2, 0.7) # e.g. audience retention
                
                if platform_name not in all_performance_data: all_performance_data[platform_name] = {}
                all_performance_data[platform_name][video_id] = simulated_data
                self.logger.info(f"Collected (simulated) performance for {video_id} ({platform_name}): Views - {simulated_data.get('views', 'N/A')}")
        
        # Save performance data
        perf_data_path = os.path.join(self.global_config.current_project_dir, "9_performance_data", f"performance_summary_{datetime.now().strftime('%Y%m%d%H%M')}.json")
        with open(perf_data_path, 'w') as f:
            json.dump(all_performance_data, f, indent=4)
        
        if all_performance_data:
            self._adapt_strategies(all_performance_data)
        
        return all_performance_data

    def _adapt_strategies(self, performance_data: Dict):
        """Adapts system parameters based on performance data (conceptual)."""
        if not self.config["adaptation_strategy"]["enabled"]:
            self.logger.info("Strategy adaptation is disabled.")
            return

        self.logger.info("Adapting strategies based on performance data (conceptual).")
        # --- Adaptation Logic ---
        # 1. Aggregate performance across videos/platforms.
        # 2. Identify high/low performing content attributes (topics, styles, thumbnail types, etc.).
        # 3. Adjust weights/biases in self.global_config for parameters listed in "parameters_to_adjust".
        #    For example, if "viral_explainer_short" style performs well, increase its selection chance.
        #    If topics with "AI Ethics" perform poorly, decrease their niche_focus_keywords weight.
        
        # Example: Simple adjustment to niche keyword focus based on views (highly simplified)
        # This is where true ML/adaptive logic would go.
        # For now, this is a placeholder for a complex system.
        
        avg_views_per_topic_kw = {} # topic_keyword: [total_views, count]
        # This requires linking performance_data back to the original trend/topic keywords.
        # Assume we have this link for now.

        # Imagine we analyzed that videos about "Sustainable Energy Tech" got more views
        param_to_adjust = "topic_selection_bias" # Example parameter
        if param_to_adjust in self.config["adaptation_strategy"]["parameters_to_adjust"]:
            current_niches = self.global_config.trend_analysis.get("niche_focus_keywords", [])
            # Example: if "Sustainable Energy Tech" is doing well, we might want to ensure it's prioritized
            # This would typically involve changing weights in a more sophisticated topic selection model,
            # not just reordering a list.
            # For simulation, let's say we log an intent:
            self.logger.info(f"ADAPTATION SUGGESTION: Consider increasing focus on 'Sustainable Energy Tech' due to positive performance signals.")
            
            # A more concrete (but still simple) example: Adjusting content style weighting
            # This would require a new config field like: self.global_config.content_style_weights = {"viral_explainer_short": 0.6, ...}
            # style_performance = {"viral_explainer_short": {"avg_views": 5000, "avg_engagement": 0.05}, ...}
            # for style, perf in style_performance.items():
            #    if perf["avg_views"] > some_threshold:
            #       self.global_config.content_style_weights[style] = min(1.0, self.global_config.content_style_weights[style] * (1 + self.config["adaptation_strategy"]["learning_rate_factor"]))
            #    else:
            #       self.global_config.content_style_weights[style] = max(0.1, self.global_config.content_style_weights[style] * (1 - self.config["adaptation_strategy"]["learning_rate_factor"]))
            # logger.info(f"Updated content style weights: {self.global_config.content_style_weights}")
            self.logger.info("Conceptual strategy adaptation logged.")


# --- Main Orchestrator ---
class AutoCreatorXOrchestrator:
    def __init__(self, config: AutoCreatorXConfig):
        self.config = config
        self.logger = logging.getLogger("Orchestrator")
        
        # Initialize core components, passing the config and other necessary modules
        self.anti_detection = AntiDetection(self.config)
        self.intelligence_core = IntelligenceCore(self.config, self.anti_detection)
        self.media_core = MediaCore(self.config, self.anti_detection)
        self.platform_ops = PlatformOperations(self.config, self.anti_detection)
        self.feedback_loop = FeedbackLoop(self.config)
        self.monetization_manager = MonetizationManager(self.config)
        
        self.logger.info(f"AutoCreatorX Orchestrator initialized with System ID: {self.config.system_id}, Instance ID: {self.config.instance_id}")

    def run_full_cycle(self) -> bool:
        """Runs a complete content creation and publishing cycle."""
        self.logger.info(f"--- Starting new AutoCreatorX cycle (Instance: {self.config.instance_id}) ---")
        
        # 0. Create project directories for this cycle/instance
        try:
            self.config.create_project_directories()
        except Exception as e:
            self.logger.critical(f"Failed to create project directories. Cycle cannot continue: {e}")
            return False

        # 1. Trend Analysis and Topic Selection
        self.logger.info("STEP 1: Trend Analysis and Topic Selection")
        selected_trend = self.intelligence_core.analyze_trends_and_select_topic()
        if not selected_trend:
            self.logger.error("Failed to select a viable trend. Ending cycle.")
            return False
        current_topic_title_slug = Utilities.slugify(selected_trend.get("title", "untitled-topic"))

        # 2. Script and Metadata Generation
        self.logger.info("STEP 2: Script and Metadata Generation")
        content_style = self.config.default_content_style # Could be dynamically chosen
        script_metadata_tuple = self.intelligence_core.generate_script_and_metadata(selected_trend, content_style)
        if not script_metadata_tuple:
            self.logger.error("Failed to generate script and metadata. Ending cycle.")
            return False
        script_object, metadata_object = script_metadata_tuple
        script_title_slug = Utilities.slugify(script_object.get("title_suggestion", current_topic_title_slug))


        # (Intermediate) Monetization Strategy Application (Modifies Script/Metadata)
        video_duration_seconds = script_object.get("estimated_duration_minutes", 5) * 60
        self.logger.info("STEP 2.5: Applying Monetization Strategies")
        script_object, metadata_object = self.monetization_manager.apply_monetization_strategies(
            script_object, metadata_object, video_duration_seconds, selected_trend.get("title"), platform="youtube" # Example platform for now
        )
        # Re-save potentially modified script/metadata (optional, or pass objects along)


        # 3. Media Production
        self.logger.info("STEP 3: Media Production")
        # 3a. Voiceover
        voiceover_path = self.media_core.generate_voiceover(script_object["narration_text"], self.config.global_language, script_title_slug)
        if not voiceover_path:
            self.logger.error("Failed to generate voiceover. Ending cycle.")
            return False
        
        # 3b. Visual Assets
        visual_assets = self.media_core.procure_visual_assets(script_object, script_title_slug)
        # Add checks for sufficient assets if necessary

        # 3c. Background Music
        music_mood_keywords = script_object.get("mood_tags", selected_trend.get("keywords", ["general"])) # Get mood from script or trend
        music_path = self.media_core.select_background_music(music_mood_keywords, video_duration_seconds, script_title_slug)
        # Music is optional, so don't fail cycle if None, but log it.
        if not music_path:
             self.logger.warning("No background music selected or an error occurred.")

        # 3d. Video Composition
        final_video_path = self.media_core.compose_video(script_object, voiceover_path, visual_assets, music_path, script_title_slug)
        if not final_video_path:
            self.logger.error("Failed to compose final video. Ending cycle.")
            return False

        # 3e. Thumbnail Generation
        thumbnail_path = self.media_core.generate_thumbnail(script_object["title_suggestion"], script_object, visual_assets, script_title_slug)
        if not thumbnail_path:
             self.logger.warning("Failed to generate thumbnail, platform defaults may be used or upload might fail on some platforms.")
             # Depending on platform requirements, this could be critical.

        # 4. Platform Operations (Upload)
        self.logger.info("STEP 4: Platform Upload")
        upload_statuses = self.platform_ops.upload_content_to_platforms(final_video_path, thumbnail_path, metadata_object, script_object)
        if not any(status.get("status") == "success" for status in upload_statuses.values()):
            self.logger.error("Failed to upload to any platform. Ending cycle with partial success (content created).")
            # Still, content is created, so it's not a total failure of the cycle's primary goal.
            # It could be re-attempted later.
            # return False # Or True if local content creation is a valid outcome

        # 5. Feedback Loop (Data Collection and Adaptation)
        if self.config.feedback_loop["enabled"]:
            self.logger.info("STEP 5: Feedback Loop Operations")
            performance_summary = self.feedback_loop.collect_and_analyze_performance(upload_statuses)
            if performance_summary:
                self.logger.info("Performance data collected and strategies potentially adapted.")
                # Monetization revenue tracking using performance data
                for platform, vids in performance_summary.items():
                    for video_id, metrics in vids.items():
                        self.monetization_manager.track_revenue(platform, video_id, metrics)

        self.logger.info(f"--- AutoCreatorX cycle completed for Instance: {self.config.instance_id} ---")
        return True


# --- Main Execution ---
if __name__ == "__main__":
    logger.info("Initializing AutoCreatorX System...")

    # --- Configuration Loading ---
    # Option 1: Load from YAML
    # config_file_path = "autocreatorx_config.yaml" # Create this file
    # config = AutoCreatorXConfig.load_from_yaml(config_file_path)

    # Option 2: Use default config (if no YAML or for testing)
    config = AutoCreatorXConfig() # Uses defaults if YAML load fails or not implemented

    if not config.validate_config():
        logger.critical("Configuration validation failed. Please check settings. Exiting.")
        exit(1)

    orchestrator = AutoCreatorXOrchestrator(config)

    if config.autonomous_mode_enabled:
        logger.info(f"Autonomous mode enabled. Cycle interval: {config.autonomous_cycle_interval_hours} hours.")
        while True:
            try:
                cycle_successful = orchestrator.run_full_cycle()
                if cycle_successful:
                    logger.info("Cycle completed successfully.")
                else:
                    logger.warning("Cycle completed with errors or did not fully succeed.")
            except Exception as e:
                logger.critical(f"Unhandled critical error in main autonomous loop: {e}", exc_info=True)
                # Potentially implement an emergency stop or a longer backoff here
            
            logger.info(f"Next cycle in {config.autonomous_cycle_interval_hours} hours. Sleeping...")
            time.sleep(config.autonomous_cycle_interval_hours * 60 * 60)
    else:
        logger.info("Autonomous mode disabled. Running a single cycle.")
        try:
            cycle_successful = orchestrator.run_full_cycle()
            if cycle_successful:
                logger.info("Single cycle completed successfully.")
            else:
                logger.warning("Single cycle completed with errors or did not fully succeed.")
        except Exception as e:
            logger.critical(f"Unhandled critical error in single cycle execution: {e}", exc_info=True)

    logger.info("AutoCreatorX System shutdown.")