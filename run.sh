#!/bin/bash

# AWS Cost Explorer MCP Chatbot 실행 스크립트 (EC2 배포용)

echo "🚀 AWS Cost Explorer MCP Chatbot 시작 중..."

# 현재 디렉토리 확인
if [ ! -f "app.py" ]; then
    echo "❌ app.py 파일을 찾을 수 없습니다. 올바른 디렉토리에서 실행해주세요."
    exit 1
fi

# 가상환경 확인 및 활성화
if [ ! -d "venv" ]; then
    echo "📦 가상환경을 생성 중..."
    python3 -m venv venv
fi

echo "📦 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치
echo "📋 의존성 설치 중..."
pip install -r requirements.txt > /dev/null 2>&1

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    if [ -f ".env.example" ]; then
        echo "📝 .env.example을 복사하여 .env 파일을 생성합니다."
        cp .env.example .env
        echo "✏️  .env 파일을 편집하여 AWS 설정을 완료해주세요."
        echo "   nano .env"
    fi
fi

# AWS 자격 증명 확인
echo "🔐 AWS 자격 증명 확인 중..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS 자격 증명이 설정되지 않았습니다."
    echo ""
    echo "다음 중 하나의 방법으로 AWS 자격 증명을 설정해주세요:"
    echo "1. EC2 IAM Role 사용 (권장)"
    echo "2. aws configure 실행"
    echo "3. 환경 변수 설정"
    echo ""
    echo "자세한 내용은 README.md를 참조하세요."
    exit 1
fi

echo "✅ AWS 자격 증명 확인 완료"

# 실행 방법 선택
echo ""
echo "🌟 실행 방법을 선택하세요:"
echo "1. MCP 서버만 실행 (다른 터미널에서 Streamlit 실행)"
echo "2. Streamlit 앱만 실행 (MCP 서버가 이미 실행 중인 경우)"
echo "3. 사용 방법 안내"
echo ""
read -p "선택 (1-3): " choice

case $choice in
    1)
        echo "🖥️  MCP 서버 실행 중..."
        echo "다른 터미널에서 다음 명령어를 실행하세요:"
        echo "  source venv/bin/activate"
        echo "  streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
        echo ""
        python standard_mcp_server.py
        ;;
    2)
        echo "🌐 Streamlit 앱 실행 중..."
        echo "브라우저에서 http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8501 로 접속하세요."
        echo "종료하려면 Ctrl+C를 누르세요."
        echo ""
        streamlit run app.py --server.port 8501 --server.address 0.0.0.0
        ;;
    3)
        echo ""
        echo "📖 사용 방법:"
        echo ""
        echo "1. 터미널 1에서 MCP 서버 실행:"
        echo "   ./run.sh  (옵션 1 선택)"
        echo ""
        echo "2. 터미널 2에서 Streamlit 앱 실행:"
        echo "   ./run.sh  (옵션 2 선택)"
        echo ""
        echo "3. 브라우저 접속:"
        echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_EC2_IP"):8501"
        echo ""
        echo "4. 보안 그룹에서 포트 8501이 열려있는지 확인하세요."
        echo ""
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac
