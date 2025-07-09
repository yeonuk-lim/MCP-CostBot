"""AWS 유틸리티 함수들"""

import boto3
import logging
from botocore.exceptions import NoCredentialsError, ClientError

logger = logging.getLogger(__name__)

def check_aws_credentials():
    """AWS 자격 증명 확인"""
    try:
        # STS를 사용하여 현재 자격 증명 확인
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        
        account_id = response.get('Account')
        user_arn = response.get('Arn')
        
        logger.info(f"AWS 자격 증명 확인 성공: Account {account_id}")
        return True, {
            'account_id': account_id,
            'user_arn': user_arn,
            'method': get_credential_method()
        }
        
    except NoCredentialsError:
        logger.error("AWS 자격 증명을 찾을 수 없습니다.")
        return False, "AWS 자격 증명이 설정되지 않았습니다."
    except ClientError as e:
        logger.error(f"AWS 자격 증명 확인 실패: {e}")
        return False, f"AWS 자격 증명 오류: {str(e)}"
    except Exception as e:
        logger.error(f"예상치 못한 오류: {e}")
        return False, f"오류: {str(e)}"

def get_credential_method():
    """현재 사용 중인 자격 증명 방법 확인"""
    import os
    
    # 환경 변수 확인
    if os.getenv('AWS_ACCESS_KEY_ID'):
        return "환경 변수"
    
    # AWS CLI 프로파일 확인
    try:
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            # EC2 인스턴스 메타데이터 확인
            try:
                import requests
                response = requests.get(
                    'http://169.254.169.254/latest/meta-data/iam/security-credentials/',
                    timeout=1
                )
                if response.status_code == 200:
                    return "EC2 IAM Role"
            except:
                pass
            
            return "AWS CLI 프로파일"
    except:
        pass
    
    return "알 수 없음"

def check_cost_explorer_permissions():
    """Cost Explorer 권한 확인"""
    try:
        ce = boto3.client('ce', region_name='us-east-1')
        
        # 간단한 Cost Explorer API 호출로 권한 테스트
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        response = ce.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='MONTHLY',
            Metrics=['BlendedCost']
        )
        
        logger.info("Cost Explorer 권한 확인 성공")
        return True, "Cost Explorer 권한 확인 완료"
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            return False, "Cost Explorer 권한이 없습니다. IAM 정책을 확인해주세요."
        else:
            return False, f"Cost Explorer 오류: {str(e)}"
    except Exception as e:
        return False, f"Cost Explorer 권한 확인 실패: {str(e)}"

def check_bedrock_permissions():
    """Bedrock 권한 확인"""
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # 간단한 텍스트로 모델 호출 테스트
        import json
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.1
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=json.dumps(body)
        )
        
        logger.info("Bedrock 권한 확인 성공")
        return True, "Bedrock 권한 확인 완료"
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            return False, "Bedrock 권한이 없습니다. IAM 정책을 확인해주세요."
        elif error_code == 'ValidationException':
            if 'model access' in str(e).lower():
                return False, "Bedrock 모델 액세스가 활성화되지 않았습니다. Bedrock 콘솔에서 모델 액세스를 활성화해주세요."
            else:
                return False, f"Bedrock 설정 오류: {str(e)}"
        else:
            return False, f"Bedrock 오류: {str(e)}"
    except Exception as e:
        return False, f"Bedrock 권한 확인 실패: {str(e)}"

def get_aws_status():
    """전체 AWS 상태 확인"""
    status = {
        'credentials': {'status': False, 'message': ''},
        'cost_explorer': {'status': False, 'message': ''},
        'bedrock': {'status': False, 'message': ''}
    }
    
    # 자격 증명 확인
    cred_status, cred_info = check_aws_credentials()
    status['credentials']['status'] = cred_status
    if cred_status:
        status['credentials']['message'] = f"✅ 계정: {cred_info['account_id'][:8]}**** ({cred_info['method']})"
    else:
        status['credentials']['message'] = f"❌ {cred_info}"
    
    # Cost Explorer 권한 확인 (자격 증명이 있는 경우에만)
    if cred_status:
        ce_status, ce_message = check_cost_explorer_permissions()
        status['cost_explorer']['status'] = ce_status
        status['cost_explorer']['message'] = f"{'✅' if ce_status else '❌'} {ce_message}"
        
        # Bedrock 권한 확인
        br_status, br_message = check_bedrock_permissions()
        status['bedrock']['status'] = br_status
        status['bedrock']['message'] = f"{'✅' if br_status else '❌'} {br_message}"
    else:
        status['cost_explorer']['message'] = "⏸️ 자격 증명 필요"
        status['bedrock']['message'] = "⏸️ 자격 증명 필요"
    
    return status
