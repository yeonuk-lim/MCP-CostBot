"""Configuration settings for the MCP Cost Chatbot."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "default")

# Anthropic Configuration (optional - for direct API usage)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "localhost")
MCP_SERVER_PORT = os.getenv("MCP_SERVER_PORT", "8000")

# Bedrock Configuration
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")

# Streamlit Configuration
STREAMLIT_PAGE_TITLE = "AWS Cost Explorer Assistant"
STREAMLIT_PAGE_ICON = "💰"
STREAMLIT_LAYOUT = "wide"
STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

# Chat Configuration
MAX_CHAT_HISTORY = 50
DEFAULT_WELCOME_MESSAGE = """
# 💰 AWS Cost Explorer Assistant

안녕하세요! AWS 비용 분석을 도와드리는 AI 어시스턴트입니다.

## 🚀 주요 기능
- **실시간 비용 조회**: 현재 AWS 계정의 실제 비용 데이터
- **상세 분석**: 서비스별, 리전별, 기간별 비용 분석
- **비교 분석**: 월별 비용 변화 및 원인 분석
- **예측**: 향후 비용 예측 및 트렌드 분석

## 💬 질문 예시
- "이번 달 AWS 비용이 얼마나 나왔나요?"
- "지난 3개월간 서비스별 비용을 보여주세요"
- "6월과 7월 비용 변화를 분석해주세요"
- "왜 비용이 늘었는지 원인을 분석해주세요"
- "어떤 AWS 서비스들을 사용하고 있나요?"

자연어로 편하게 질문해주시면 됩니다!

---
⚡ **실시간 데이터**: AWS Cost Explorer API에서 직접 조회  
🔒 **보안**: IAM Role 기반 안전한 액세스  
🌐 **오픈소스**: [GitHub에서 소스코드 확인](https://github.com/your-repo/aws-cost-explorer-mcp-chatbot)
"""

# Validation
def validate_config():
    """Validate configuration settings."""
    issues = []
    
    if not AWS_REGION:
        issues.append("AWS_REGION이 설정되지 않았습니다.")
    
    if not BEDROCK_MODEL_ID:
        issues.append("BEDROCK_MODEL_ID가 설정되지 않았습니다.")
    
    if not BEDROCK_REGION:
        issues.append("BEDROCK_REGION이 설정되지 않았습니다.")
    
    return issues

# Auto-validation on import
config_issues = validate_config()
if config_issues:
    import logging
    logger = logging.getLogger(__name__)
    for issue in config_issues:
        logger.warning(f"Configuration issue: {issue}")
