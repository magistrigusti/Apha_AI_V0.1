import os
import re
import asyncio
from dotenv import load_dotenv
from gradio_client import Client
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
  Application,
  CommandHandler,
  ContentTypes,
  MessageHandler,
  filters,
)

load_dotenv()

ALPHA_BOT_TOKEN = os.getenv("ALPHA_BOT_TOKEN", "")
HF_TOKEN = os.getenv("HF_TOKEN",)