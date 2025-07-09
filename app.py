"""
AWS Cost Explorer Assistant - Streamlit Application

MCP 기반 AWS 비용 분석 챗봇 애플리케이션
"""

import streamlit as st
import asyncio
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

from ai_assistant import CostAnalysisAssistant
from config import (
    STREAMLIT_PAGE_TITLE, 
    STREAMLIT_PAGE_ICON, 
    STREAMLIT_LAYOUT,
    DEFAULT_WELCOME_MESSAGE,
    MAX_CHAT_HISTORY,
    STREAMLIT_SERVER_PORT,
    STREAMLIT_SERVER_ADDRESS
)
from aws_utils import get_aws_status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout=STREAMLIT_LAYOUT,
    initial_sidebar_state="expanded"
)

# EC2 배포 시 외부 접속을 위한 설정
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and "--server.address" not in sys.argv:
        # EC2에서 실행 시 외부 접속 허용
        import subprocess
        import os
        
        # 현재 스크립트를 외부 접속 가능하도록 재실행
        cmd = [
            "streamlit", "run", __file__,
            "--server.port", str(STREAMLIT_SERVER_PORT),
            "--server.address", STREAMLIT_SERVER_ADDRESS
        ]
        subprocess.run(cmd)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF9900;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #F3E5F5;
        border-left: 4px solid #9C27B0;
    }
    .cost-metric {
        background-color: #E8F5E8;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_assistant():
    """Get or create the AI assistant instance."""
    return CostAnalysisAssistant()

async def initialize_assistant():
    """Initialize the AI assistant."""
    assistant = get_assistant()
    await assistant.initialize()
    return assistant

def display_welcome_message():
    """Display welcome message."""
    st.markdown('<div class="main-header">💰 AWS Cost Explorer Assistant</div>', unsafe_allow_html=True)
    st.markdown(DEFAULT_WELCOME_MESSAGE)

def display_chat_history():
    """Display chat history."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def add_message_to_history(role: str, content: str):
    """Add message to session state history."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    st.session_state.messages.append({"role": role, "content": content})
    
    # Keep only last MAX_CHAT_HISTORY messages
    if len(st.session_state.messages) > MAX_CHAT_HISTORY:
        st.session_state.messages = st.session_state.messages[-MAX_CHAT_HISTORY:]

def create_cost_visualization(cost_data):
    """Create cost visualization from data."""
    try:
        if not cost_data or "ResultsByTime" not in cost_data:
            return None
        
        # Extract data for visualization
        dates = []
        amounts = []
        services = []
        
        for result in cost_data["ResultsByTime"]:
            date = result["TimePeriod"]["Start"]
            
            if "Groups" in result:
                for group in result["Groups"]:
                    service = group["Keys"][0] if group["Keys"] else "Unknown"
                    amount = float(group["Metrics"]["BlendedCost"]["Amount"])
                    dates.append(date)
                    amounts.append(amount)
                    services.append(service)
            else:
                amount = float(result["Total"]["BlendedCost"]["Amount"])
                dates.append(date)
                amounts.append(amount)
                services.append("Total")
        
        if not dates:
            return None
        
        # Create DataFrame
        df = pd.DataFrame({
            "Date": dates,
            "Amount": amounts,
            "Service": services
        })
        
        # Create visualization based on data structure
        if len(df["Service"].unique()) > 1:
            # Multiple services - create grouped bar chart
            fig = px.bar(df, x="Date", y="Amount", color="Service",
                        title="AWS 비용 분석",
                        labels={"Amount": "비용 (USD)", "Date": "날짜"})
        else:
            # Single service or total - create line chart
            fig = px.line(df, x="Date", y="Amount",
                         title="AWS 비용 추이",
                         labels={"Amount": "비용 (USD)", "Date": "날짜"})
        
        fig.update_layout(
            xaxis_title="날짜",
            yaxis_title="비용 (USD)",
            hovermode="x unified"
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating visualization: {e}")
        return None

async def process_user_query(query: str):
    """Process user query and generate response."""
    try:
        assistant = get_assistant()
        response = await assistant.generate_response(query)
        return response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return f"죄송합니다. 질문 처리 중 오류가 발생했습니다: {str(e)}"

def main():
    """Main application function."""
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 설정")
        
        # AWS 상태 확인
        st.subheader("🔗 AWS 연결 상태")
        if st.button("상태 확인", key="aws_status_check"):
            with st.spinner("AWS 상태 확인 중..."):
                aws_status = get_aws_status()
                
                # 자격 증명 상태
                if aws_status['credentials']['status']:
                    st.success(aws_status['credentials']['message'])
                else:
                    st.error(aws_status['credentials']['message'])
                
                # Cost Explorer 상태
                if aws_status['cost_explorer']['status']:
                    st.success(aws_status['cost_explorer']['message'])
                elif "자격 증명 필요" in aws_status['cost_explorer']['message']:
                    st.warning(aws_status['cost_explorer']['message'])
                else:
                    st.error(aws_status['cost_explorer']['message'])
                
                # Bedrock 상태
                if aws_status['bedrock']['status']:
                    st.success(aws_status['bedrock']['message'])
                elif "자격 증명 필요" in aws_status['bedrock']['message']:
                    st.warning(aws_status['bedrock']['message'])
                else:
                    st.error(aws_status['bedrock']['message'])
        
        st.divider()
        
        # Quick actions
        st.subheader("빠른 질문")
        quick_questions = [
            "이번 달 AWS 비용이 얼마나 나왔나요?",
            "지난 3개월간 서비스별 비용을 보여주세요",
            "EC2 비용을 리전별로 분석해주세요",
            "비용이 가장 많이 나온 서비스 TOP 5는?",
            "다음 달 예상 비용을 알려주세요"
        ]
        
        for question in quick_questions:
            if st.button(question, key=f"quick_{hash(question)}"):
                st.session_state.quick_question = question
        
        st.divider()
        
        # Clear chat history
        if st.button("💬 대화 기록 지우기"):
            st.session_state.messages = []
            st.rerun()
        
        # AWS Region info
        st.subheader("ℹ️ 정보")
        st.info("현재 AWS 리전: us-east-1")
        st.info("데이터 소스: AWS Cost Explorer")
    
    # Main content
    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        display_welcome_message()
    
    # Display chat history
    display_chat_history()
    
    # Handle quick question
    if hasattr(st.session_state, 'quick_question'):
        user_input = st.session_state.quick_question
        delattr(st.session_state, 'quick_question')
    else:
        user_input = None
    
    # Chat input
    if prompt := st.chat_input("AWS 비용에 대해 궁금한 것을 물어보세요...") or user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        add_message_to_history("user", prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("분석 중..."):
                try:
                    # Run async function
                    response = asyncio.run(process_user_query(prompt))
                    st.markdown(response)
                    add_message_to_history("assistant", response)
                    
                except Exception as e:
                    error_msg = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
                    st.error(error_msg)
                    add_message_to_history("assistant", error_msg)

if __name__ == "__main__":
    main()
