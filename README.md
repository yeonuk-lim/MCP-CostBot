# AWS Cost Explorer MCP Chatbot

AWS Cost Explorer를 활용한 MCP 기반 비용 분석 챗봇입니다. 자연어로 AWS 비용을 질문하고 실시간으로 분석할 수 있습니다.

## 🚀 주요 기능

- **자연어 질의**: 한국어로 편리하게 AWS 비용 질문
- **실시간 비용 분석**: AWS Cost Explorer API를 통한 실시간 데이터 조회
- **MCP 아키텍처**: 표준 MCP 서버를 통한 확장 가능한 구조
- **9가지 분석 도구**: 기본 비용 조회부터 비교 분석까지
- **대화형 인터페이스**: Streamlit 기반 사용자 친화적 UI

## 📋 사전 요구사항

- **AWS 계정**: Cost Explorer 및 Bedrock 액세스 권한
- **Python 3.8+**: Python 3.8 이상 버전
- **EC2 인스턴스**: 권장 사양 t3.medium 이상

## 🔐 AWS 권한 설정

### 1. IAM 정책 생성

다음 권한을 가진 IAM 정책을 생성하세요:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetDimensionValues",
                "ce:GetCostForecast",
                "ce:GetUsageReport",
                "ce:ListCostCategoryDefinitions",
                "ce:GetCostCategories"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
            ]
        }
    ]
}
```

### 2. AWS 자격 증명 설정 방법

#### 🎯 **방법 1: EC2 IAM Role (권장)**

**가장 안전한 방법입니다. 액세스 키를 하드코딩하지 않습니다.**

1. **IAM Role 생성**:
   - AWS Console → IAM → Roles → Create role
   - Trusted entity: AWS service → EC2
   - 위에서 생성한 정책 연결
   - Role 이름: `CostExplorerChatbotRole`

2. **EC2에 Role 연결**:
   - EC2 Console → 인스턴스 선택 → Actions → Security → Modify IAM role
   - 생성한 Role 선택

3. **코드에서 자동 인식**:
   ```python
   # 코드 변경 불필요 - boto3가 자동으로 Role 사용
   cost_explorer = boto3.client('ce', region_name='us-east-1')
   ```

#### 🔑 **방법 2: AWS CLI 설정**

1. **AWS CLI 설치**:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

2. **자격 증명 설정**:
   ```bash
   aws configure
   # AWS Access Key ID: [YOUR_ACCESS_KEY]
   # AWS Secret Access Key: [YOUR_SECRET_KEY]
   # Default region name: us-east-1
   # Default output format: json
   ```

#### 🌍 **방법 3: 환경 변수**

```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1
```

## 🛠️ EC2에서 설치 및 실행

### 1. EC2 인스턴스 준비

**권장 사양**:
- 인스턴스 타입: `t3.medium` 이상
- OS: Amazon Linux 2 또는 Ubuntu 20.04+
- 스토리지: 20GB 이상
- 보안 그룹: 포트 8501 (Streamlit) 오픈

### 2. 시스템 업데이트 및 Python 설치

```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install -y python3 python3-pip git

# Ubuntu
sudo apt update
sudo apt install -y python3 python3-pip git
```

### 3. 프로젝트 클론 및 설정

```bash
# 프로젝트 클론
git clone https://github.com/your-username/aws-cost-explorer-mcp-chatbot.git
cd aws-cost-explorer-mcp-chatbot

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# 환경 변수 편집
nano .env
```

`.env` 파일 내용:
```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_PROFILE=default

# Bedrock Configuration  
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_REGION=us-east-1

# Streamlit Configuration (EC2 배포용)
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 5. Bedrock 모델 액세스 활성화

1. **AWS Console → Bedrock → Model access**
2. **Claude 3.5 Sonnet 모델 활성화**
3. **리전 확인**: `us-east-1` 또는 `us-west-2`

## 🚀 실행 방법

### 터미널 1: MCP 서버 실행
```bash
source venv/bin/activate
python standard_mcp_server.py
```

### 터미널 2: Streamlit 앱 실행
```bash
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 또는 스크립트 사용
```bash
chmod +x run.sh
./run.sh
```

## 🌐 외부 접속 설정

### 1. 보안 그룹 설정
- **포트 8501** 인바운드 규칙 추가
- **소스**: 필요에 따라 특정 IP 또는 0.0.0.0/0

### 2. 접속 URL
```
http://[EC2_PUBLIC_IP]:8501
```

## 🔒 보안 고려사항

### 1. IAM Role 사용 (권장)
- ✅ 액세스 키 하드코딩 방지
- ✅ 자동 키 로테이션
- ✅ 최소 권한 원칙

### 2. 네트워크 보안
- 🔐 보안 그룹에서 필요한 포트만 오픈
- 🔐 가능하면 특정 IP 대역으로 제한
- 🔐 HTTPS 사용 권장 (프로덕션 환경)

### 3. 환경 변수 보안
```bash
# .env 파일 권한 설정
chmod 600 .env

# Git에서 제외 확인
echo ".env" >> .gitignore
```

## 💬 사용 예시

챗봇에서 다음과 같은 질문을 해보세요:

### 기본 비용 조회
- "이번 달 AWS 비용이 얼마나 나왔나요?"
- "지난 3개월간 서비스별 비용을 보여주세요"
- "리전별 비용 분석해주세요"

### 고급 분석
- "6월과 7월 비용 변화를 분석해주세요"
- "왜 비용이 늘었는지 원인을 분석해주세요"
- "어떤 AWS 서비스들을 사용하고 있나요?"

## 🛠️ 문제 해결

### AWS 권한 오류
```bash
# AWS 자격 증명 확인
aws sts get-caller-identity

# Cost Explorer 권한 테스트
aws ce get-cost-and-usage --time-period Start=2025-01-01,End=2025-02-01 --granularity MONTHLY --metrics BlendedCost
```

### Bedrock 액세스 오류
1. Bedrock 콘솔에서 모델 액세스 확인
2. 올바른 리전 설정 확인
3. IAM 권한 확인

### 포트 접속 오류
```bash
# 포트 사용 확인
sudo netstat -tlnp | grep 8501

# 방화벽 확인 (Ubuntu)
sudo ufw status
```

## 📁 프로젝트 구조

```
aws-cost-explorer-mcp-chatbot/
├── app.py                    # Streamlit 애플리케이션
├── standard_mcp_server.py    # MCP 서버 (9개 도구)
├── ai_assistant.py           # AI 어시스턴트
├── mcp_client.py            # MCP 클라이언트
├── config.py                # 설정 관리
├── requirements.txt         # Python 의존성
├── .env.example            # 환경 변수 예시
├── .gitignore              # Git 제외 파일
├── run.sh                  # 실행 스크립트
└── README.md              # 이 문서
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## ⚠️ 비용 주의사항

- **Cost Explorer API**: 호출당 $0.01 비용 발생
- **Bedrock**: 토큰 사용량에 따른 비용
- **EC2**: 인스턴스 실행 비용

정확한 비용은 [AWS 요금 계산기](https://calculator.aws)에서 확인하세요.
