#!/bin/bash
# API 测试脚本 (Shell 版本)
# 用法: ./test-api.sh [BASE_URL]
# 例如: ./test-api.sh http://localhost:3000
#       ./test-api.sh https://your-app.railway.app

BASE_URL="${1:-http://localhost:3000}"
BASE_URL="${BASE_URL%/}"  # 移除尾部斜杠

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

TEST_EMAIL="test-$(date +%s)@example.com"

echo -e "${BLUE}=================================================="
echo -e "Testing API: ${BASE_URL}"
echo -e "==================================================${NC}"

# 测试函数
test_endpoint() {
    local name="$1"
    local method="$2"
    local path="$3"
    local data="$4"
    
    echo -e "\n${CYAN}🧪 Testing: ${name}${NC}"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${BASE_URL}${path}")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            "${BASE_URL}${path}")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✅ ${name}: PASSED (HTTP ${http_code})${NC}"
        echo -e "${YELLOW}   Response: ${body}${NC}"
        return 0
    else
        echo -e "${RED}❌ ${name}: FAILED (HTTP ${http_code})${NC}"
        echo -e "${RED}   Response: ${body}${NC}"
        return 1
    fi
}

# 运行测试
FAILED=0

# 1. 健康检查
test_endpoint "Health Check" "GET" "/api/health" || FAILED=1

# 2. 订阅
test_endpoint "Subscribe" "POST" "/api/subscribe" "{\"email\":\"${TEST_EMAIL}\",\"tags\":[\"tech\"]}" || FAILED=1

# 3. 获取统计信息
test_endpoint "Get Stats" "GET" "/api/stats" || FAILED=1

# 4. 更新标签
ENCODED_EMAIL=$(echo -n "$TEST_EMAIL" | jq -sRr @uri)
test_endpoint "Update Tags" "PATCH" "/api/subscribers/${ENCODED_EMAIL}/tags" "{\"tag\":\"ai\",\"add\":true}" || FAILED=1

# 5. 取消订阅
test_endpoint "Unsubscribe" "POST" "/api/unsubscribe" "{\"email\":\"${TEST_EMAIL}\"}" || FAILED=1

# 6. 删除订阅者
test_endpoint "Delete Subscriber" "DELETE" "/api/subscribers/${ENCODED_EMAIL}" || FAILED=1

# 7. 测试无效邮箱（应该失败）
echo -e "\n${CYAN}🧪 Testing: Invalid Email Validation${NC}"
INVALID_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"invalid-email"}' \
    "${BASE_URL}/api/subscribe")
INVALID_CODE=$(echo "$INVALID_RESPONSE" | tail -n1)
if [ "$INVALID_CODE" -eq 400 ]; then
    echo -e "${GREEN}✅ Invalid Email Validation: PASSED (correctly rejected)${NC}"
else
    echo -e "${RED}❌ Invalid Email Validation: FAILED (should return 400)${NC}"
    FAILED=1
fi

# 结果总结
echo -e "\n${BLUE}==================================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed!${NC}"
fi
echo -e "${BLUE}==================================================${NC}\n"

exit $FAILED

