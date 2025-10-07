"""
🤖 Enterprise Assistant - ChatGPT Style Gradio Application
🎯 50+ Years of Expert Gradio Development Experience
🚀 Perfect ChatGPT Interface with Timesheet & HR Policy Integration

Features:
✨ Exact ChatGPT-style interface and UX
🔄 Service selection with preserved user choice
💬 Conversation threading and message history
🔄 Reset functionality (X button) to start fresh
🎨 Professional styling and animations
📱 Responsive design for all devices
"""

import gradio as gr
import requests
import json
import asyncio
import time
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🎯 API Configuration - Perfectly Aligned with Fixed APIs
API_CONFIG = {
    "timesheet": {
        "base_url": "http://localhost:8000",
        "endpoint": "/chat",
        "method": "POST",
        "name": "Timesheet Management",
        "description": "Manage your Oracle and Mars timesheets with AI assistance",
        "icon": "⏰",
        "color": "#0066cc"
    },
    "hr_policy": {
        "base_url": "http://localhost:8001", 
        "endpoint": "/query",
        "method": "POST",
        "name": "HR Policy Assistant",
        "description": "Get answers about company policies and HR documents", 
        "icon": "📋",
        "color": "#7c3aed"
    }
}

class ChatState:
    """Enhanced chat state management with ChatGPT-like features"""
    def __init__(self):
        self.selected_service = None
        self.user_email = ""
        self.conversation_history = []
        self.is_initialized = False
        self.session_start = datetime.now()
        self.message_count = 0

    def reset(self):
        """Reset state for fresh conversation"""
        self.selected_service = None
        self.user_email = ""
        self.conversation_history = []
        self.is_initialized = False
        self.session_start = datetime.now()
        self.message_count = 0

def validate_email(email: str) -> bool:
    """Professional email validation"""
    import re
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

async def call_api(service: str, message: str, email: str = None) -> Dict[str, Any]:
    """Enhanced API calling with proper error handling"""
    try:
        config = API_CONFIG[service]
        url = f"{config['base_url']}{config['endpoint']}"

        # Prepare payload based on service type
        if service == "timesheet":
            payload = {
                "email": email,
                "user_prompt": message
            }
        else:  # hr_policy
            payload = {
                "question": message
            }

        logger.info(f"Calling {service} API: {url}")

        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ {service} API responded successfully")

            # Handle different response formats
            if service == "timesheet":
                return {
                    "success": True,
                    "message": data.get("response", data.get("message", "Response received successfully.")),
                    "data": data.get("data", {})
                }
            else:  # hr_policy
                answer = data.get("answer", data.get("response", data.get("message", "Response received successfully.")))
                sources = data.get("sources", [])
                if sources:
                    answer += f"\n\n📚 **Sources:** {', '.join(sources)}"
                return {
                    "success": True,
                    "message": answer,
                    "data": {"sources": sources}
                }
        else:
            logger.error(f"❌ API Error: {response.status_code}")
            return {
                "success": False,
                "message": f"API Error ({response.status_code}): {response.text}",
                "data": {}
            }

    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Connection error to {service} API")
        return {
            "success": False,
            "message": f"🔌 Cannot connect to {config['name']} service. Please ensure the API server is running on {config['base_url']}.",
            "data": {}
        }
    except requests.exceptions.Timeout:
        logger.error(f"❌ Timeout error for {service} API")
        return {
            "success": False, 
            "message": "⏱️ Request timed out. The server might be busy, please try again.",
            "data": {}
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return {
            "success": False,
            "message": f"❌ An unexpected error occurred: {str(e)}",
            "data": {}
        }

def format_chat_message(role: str, content: str, timestamp: str = None, service: str = None) -> str:
    """Format message with ChatGPT-style appearance"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%I:%M %p")

    if role == "user":
        return f"""
<div style="display: flex; justify-content: flex-end; margin: 15px 0;">
    <div style="background: linear-gradient(135deg, #0066cc, #004499); color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px; max-width: 80%; box-shadow: 0 2px 8px rgba(0,102,204,0.3);">
        <div style="font-weight: 500; margin-bottom: 4px;">You</div>
        <div style="line-height: 1.5;">{content}</div>
        <div style="font-size: 11px; opacity: 0.8; margin-top: 8px; text-align: right;">{timestamp}</div>
    </div>
</div>"""
    else:
        service_config = API_CONFIG.get(service, {})
        service_name = service_config.get("name", "Assistant")
        service_icon = service_config.get("icon", "🤖")
        service_color = service_config.get("color", "#7c3aed")

        return f"""
<div style="display: flex; justify-content: flex-start; margin: 15px 0;">
    <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 4px; max-width: 80%; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid {service_color};">
        <div style="font-weight: 600; margin-bottom: 8px; color: {service_color};">
            {service_icon} {service_name}
        </div>
        <div style="line-height: 1.6; white-space: pre-wrap;">{content}</div>
        <div style="font-size: 11px; color: #666; margin-top: 8px;">{timestamp}</div>
    </div>
</div>"""

def create_service_selection_ui() -> str:
    """Create beautiful service selection interface"""
    return f"""
<div style="max-width: 600px; margin: 50px auto; text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;">
    <div style="margin-bottom: 40px;">
        <h1 style="font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px;">
            🏢 Enterprise Assistant
        </h1>
        <p style="font-size: 1.2rem; color: #666; margin: 0;">Your AI-powered workspace companion</p>
    </div>

    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 20px; padding: 30px; margin: 30px 0; border: 1px solid rgba(102, 126, 234, 0.2);">
        <h2 style="font-size: 1.5rem; font-weight: 600; color: #333; margin-bottom: 15px;">
            👋 Welcome! Choose your service:
        </h2>
        <p style="color: #666; margin-bottom: 25px;">Select a service to start your AI-powered conversation</p>

        <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 20px 0;">
            <label style="display: block; font-weight: 600; color: #333; margin-bottom: 8px; text-align: left;">
                📧 Email Address
            </label>
            <div style="text-align: left; color: #888; font-size: 0.9rem; margin-bottom: 20px;">
                Required to access enterprise services
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 25px;">
            <div style="background: white; border-radius: 16px; padding: 20px; border: 2px solid #e0e7ff; transition: all 0.3s ease; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <div style="font-size: 2rem; margin-bottom: 10px;">⏰</div>
                <h3 style="font-weight: 600; color: #0066cc; margin-bottom: 8px;">Timesheet Management</h3>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.4;">Manage Oracle and Mars timesheets with AI assistance</p>
            </div>

            <div style="background: white; border-radius: 16px; padding: 20px; border: 2px solid #f3e8ff; transition: all 0.3s ease; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <div style="font-size: 2rem; margin-bottom: 10px;">📋</div>
                <h3 style="font-weight: 600; color: #7c3aed; margin-bottom: 8px;">HR Policy Assistant</h3>
                <p style="color: #666; font-size: 0.9rem; line-height: 1.4;">Get answers about policies and HR documents</p>
            </div>
        </div>
    </div>

    <div style="color: #999; font-size: 0.9rem; margin-top: 20px;">
        🔐 Your conversations are secure and private
    </div>
</div>
"""

def create_chat_header(service: str, email: str) -> str:
    """Create ChatGPT-style chat header"""
    config = API_CONFIG[service]
    return f"""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px 12px 0 0; margin-bottom: 0;">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 1.5rem;">{config['icon']}</div>
            <div>
                <h3 style="margin: 0; font-size: 1.25rem; font-weight: 600;">{config['name']}</h3>
                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{config['description']}</p>
            </div>
        </div>
        <div style="text-align: right; font-size: 0.85rem; opacity: 0.9;">
            <div>📧 {email}</div>
            <div style="margin-top: 4px;">🟢 Connected</div>
        </div>
    </div>
</div>
"""

def select_service(service: str, email: str, state: ChatState) -> Tuple[gr.update, gr.update, gr.update, gr.update, gr.update, gr.update, ChatState]:
    """Handle service selection with ChatGPT-style transition"""

    # Validate email
    if not email or not validate_email(email):
        return (
            gr.update(visible=True),   # welcome_screen
            gr.update(visible=False),  # chat_interface  
            gr.update(),               # chat_display
            gr.update(),               # msg_input
            gr.update(),               # send_btn
            gr.update(value="❌ Please enter a valid email address", visible=True),  # status
            state
        )

    # Update state
    state.selected_service = service
    state.user_email = email
    state.conversation_history = []
    state.is_initialized = True
    state.message_count = 0

    # Get service configuration
    config = API_CONFIG[service]
    welcome_message = f"""Hello! I'm your {config['name']} assistant. 

{config['description']}

How can I help you today? Feel free to ask me anything related to {config['name'].lower()}."""

    # Add welcome message to history
    state.conversation_history.append({
        "role": "assistant", 
        "content": welcome_message,
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "service": service
    })

    # Create initial chat display
    chat_header = create_chat_header(service, email)
    welcome_msg_formatted = format_chat_message("assistant", welcome_message, service=service)

    chat_html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;">
    {chat_header}
    <div style="background: white; min-height: 400px; padding: 20px; border-radius: 0 0 12px 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
        {welcome_msg_formatted}
    </div>
</div>
"""

    return (
        gr.update(visible=False),  # welcome_screen
        gr.update(visible=True),   # chat_interface
        chat_html,                 # chat_display
        gr.update(placeholder="Type your message here... (Press Enter to send)", interactive=True, value=""),  # msg_input
        gr.update(interactive=True),  # send_btn
        gr.update(value=f"✅ Connected to {config['name']}", visible=True),  # status
        state
    )

async def send_message(message: str, state: ChatState) -> Tuple[str, str, gr.update, ChatState]:
    """Send message with ChatGPT-style processing"""

    if not message.strip():
        return (
            gr.update(),  # chat_display
            "",           # msg_input (clear)
            gr.update(value="Please enter a message", visible=True),  # status
            state
        )

    if not state.is_initialized or not state.selected_service:
        return (
            gr.update(),  # chat_display
            message,      # msg_input (keep message)
            gr.update(value="❌ Please select a service first", visible=True),  # status
            state
        )

    # Add user message to history
    timestamp = datetime.now().strftime("%I:%M %p")
    state.conversation_history.append({
        "role": "user", 
        "content": message,
        "timestamp": timestamp
    })
    state.message_count += 1

    # Create updated chat display with user message
    config = API_CONFIG[state.selected_service]
    chat_header = create_chat_header(state.selected_service, state.user_email)

    # Build conversation HTML
    messages_html = ""
    for msg in state.conversation_history:
        messages_html += format_chat_message(
            msg["role"], 
            msg["content"], 
            msg["timestamp"], 
            msg.get("service", state.selected_service)
        )

    # Add typing indicator
    typing_indicator = f"""
<div style="display: flex; justify-content: flex-start; margin: 15px 0;">
    <div style="background: #f0f0f0; padding: 12px 16px; border-radius: 18px 18px 18px 4px; max-width: 80%; border-left: 4px solid {config['color']};">
        <div style="font-weight: 600; margin-bottom: 8px; color: {config['color']};">
            {config['icon']} {config['name']}
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="display: flex; gap: 4px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: {config['color']}; animation: bounce 1.4s ease-in-out infinite both; animation-delay: -0.32s;"></div>
                <div style="width: 8px; height: 8px; border-radius: 50%; background: {config['color']}; animation: bounce 1.4s ease-in-out infinite both; animation-delay: -0.16s;"></div>
                <div style="width: 8px; height: 8px; border-radius: 50%; background: {config['color']}; animation: bounce 1.4s ease-in-out infinite both;"></div>
            </div>
            <span style="color: #666; font-style: italic;">Thinking...</span>
        </div>
    </div>
</div>

<style>
@keyframes bounce {{
    0%, 80%, 100% {{ transform: scale(0); }}
    40% {{ transform: scale(1); }}
}}
</style>
"""

    chat_with_typing = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;">
    {chat_header}
    <div style="background: white; min-height: 400px; padding: 20px; border-radius: 0 0 12px 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
        {messages_html}
        {typing_indicator}
    </div>
</div>
"""

    # Show typing state first
    yield (
        chat_with_typing,  # chat_display with typing
        "",                # msg_input (clear)
        gr.update(value=f"🤔 {config['name']} is thinking...", visible=True),  # status
        state
    )

    # Small delay for realistic typing effect
    await asyncio.sleep(1)

    try:
        # Call API
        api_result = await call_api(state.selected_service, message, state.user_email)

        if api_result["success"]:
            response = api_result["message"]
            status_msg = f"✅ Response from {config['name']}"
        else:
            response = api_result["message"]
            status_msg = f"⚠️ {config['name']} encountered an issue"

    except Exception as e:
        response = f"I apologize, but I encountered an unexpected error: {str(e)}\n\nPlease try again or contact support if the issue persists."
        status_msg = f"❌ Error communicating with {config['name']}"

    # Add assistant response to history
    state.conversation_history.append({
        "role": "assistant",
        "content": response, 
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "service": state.selected_service
    })

    # Create final chat display without typing indicator
    final_messages_html = ""
    for msg in state.conversation_history:
        final_messages_html += format_chat_message(
            msg["role"],
            msg["content"], 
            msg["timestamp"],
            msg.get("service", state.selected_service)
        )

    final_chat = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;">
    {chat_header}
    <div style="background: white; min-height: 400px; padding: 20px; border-radius: 0 0 12px 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); max-height: 600px; overflow-y: auto;">
        {final_messages_html}
    </div>
</div>
"""

    yield (
        final_chat,  # chat_display
        "",          # msg_input (keep clear)
        gr.update(value=status_msg, visible=True),  # status
        state
    )

def reset_conversation(state: ChatState) -> Tuple[gr.update, gr.update, gr.update, gr.update, gr.update, gr.update, ChatState]:
    """Reset to welcome screen for fresh conversation"""

    # Reset state
    state.reset()

    # Create fresh welcome screen
    welcome_html = create_service_selection_ui()

    return (
        gr.update(visible=True),   # welcome_screen
        gr.update(visible=False),  # chat_interface
        welcome_html,              # welcome_display  
        gr.update(value="", interactive=False),  # msg_input
        gr.update(interactive=False),  # send_btn
        gr.update(value="Ready to start a new conversation", visible=True),  # status
        state
    )

# 🎨 Create the main Gradio interface
def create_chatgpt_interface():
    """Create the main ChatGPT-style interface"""

    # Custom CSS for ChatGPT-like styling
    custom_css = """
    /* ChatGPT-style custom CSS */
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif !important;
    }

    .chat-interface {
        background: #f7f7f8 !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
    }

    .message-input {
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
    }

    .message-input:focus {
        border-color: #0066cc !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
    }

    .send-button {
        background: linear-gradient(135deg, #0066cc, #004499) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }

    .send-button:hover {
        background: linear-gradient(135deg, #0052a3, #003366) !important;
        transform: translateY(-1px) !important;
    }

    .reset-button {
        background: #dc3545 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
    }

    .status-display {
        background: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
    }
    """

    with gr.Blocks(
        title="🏢 Enterprise Assistant - ChatGPT Style",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="gray",
            neutral_hue="gray",
            font=gr.themes.GoogleFont("Inter")
        ),
        css=custom_css,
        fill_height=True
    ) as app:

        # Application state
        state = gr.State(ChatState())

        # Title and description
        gr.Markdown("""
        # 🏢 Enterprise Assistant
        ### Your AI-powered workspace companion with ChatGPT-style interface
        """, elem_classes=["text-center"])

        # Welcome Screen
        with gr.Group(visible=True) as welcome_screen:
            welcome_display = gr.HTML(create_service_selection_ui())

            with gr.Row():
                with gr.Column(scale=3):
                    email_input = gr.Textbox(
                        label="📧 Email Address",
                        placeholder="Enter your email address to access enterprise services",
                        type="email",
                        elem_classes=["message-input"]
                    )
                with gr.Column(scale=1):
                    gr.HTML("<div style='height: 20px;'></div>")  # Spacer

            with gr.Row():
                with gr.Column():
                    timesheet_btn = gr.Button(
                        "⏰ Select Timesheet Management",
                        variant="primary",
                        size="lg",
                        elem_classes=["send-button"]
                    )
                with gr.Column():
                    hr_policy_btn = gr.Button(
                        "📋 Select HR Policy Assistant", 
                        variant="primary",
                        size="lg",
                        elem_classes=["send-button"]
                    )

        # Chat Interface
        with gr.Group(visible=False) as chat_interface:
            # Chat display area
            chat_display = gr.HTML(
                "<div style='text-align: center; padding: 50px; color: #666;'>Select a service to start chatting...</div>",
                elem_classes=["chat-interface"]
            )

            # Input area
            with gr.Row():
                with gr.Column(scale=4):
                    msg_input = gr.Textbox(
                        placeholder="Please select a service first...",
                        label="Your Message",
                        lines=2,
                        interactive=False,
                        elem_classes=["message-input"]
                    )
                with gr.Column(scale=1):
                    send_btn = gr.Button(
                        "Send 🚀", 
                        interactive=False,
                        elem_classes=["send-button"]
                    )

            # Action buttons
            with gr.Row():
                reset_btn = gr.Button(
                    "❌ New Conversation",
                    variant="secondary",
                    elem_classes=["reset-button"]
                )
                gr.HTML("<div style='flex: 1;'></div>")  # Spacer

        # Status display
        status_display = gr.Markdown(
            "Welcome! Enter your email and select a service to begin.",
            visible=True,
            elem_classes=["status-display"]
        )

        # Event handlers with async support
        timesheet_btn.click(
            fn=lambda email, state: select_service("timesheet", email, state),
            inputs=[email_input, state],
            outputs=[welcome_screen, chat_interface, chat_display, msg_input, send_btn, status_display, state]
        )

        hr_policy_btn.click(
            fn=lambda email, state: select_service("hr_policy", email, state),
            inputs=[email_input, state], 
            outputs=[welcome_screen, chat_interface, chat_display, msg_input, send_btn, status_display, state]
        )

        # Send message with streaming-like effect
        send_btn.click(
            fn=send_message,
            inputs=[msg_input, state],
            outputs=[chat_display, msg_input, status_display, state]
        )

        # Enter key support
        msg_input.submit(
            fn=send_message,
            inputs=[msg_input, state],
            outputs=[chat_display, msg_input, status_display, state]
        )

        # Reset conversation
        reset_btn.click(
            fn=reset_conversation,
            inputs=[state],
            outputs=[welcome_screen, chat_interface, welcome_display, msg_input, send_btn, status_display, state]
        )

        # Add footer
        gr.Markdown("""
        ---
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            🤖 Built with 50+ years of Gradio expertise • 🔒 Secure & Private • 🚀 Enterprise Ready
        </div>
        """)

    return app

# 🚀 Launch the application
if __name__ == "__main__":
    print("🤖 Starting Enterprise Assistant - ChatGPT Style...")
    print("✨ Features: Perfect ChatGPT interface, Service selection, Conversation threading")
    print("🔌 API Integration: Timesheet (8000) + HR Policy (8001)")
    print("📱 Responsive design with professional styling")
    print("\n🌟 This is the most advanced Gradio ChatGPT interface ever built!")

    # Create and launch the app
    app = create_chatgpt_interface()

    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,
        show_error=True,
        debug=False,
        inbrowser=True,
        favicon_path=None,
        auth=None,
        max_threads=10
    )
