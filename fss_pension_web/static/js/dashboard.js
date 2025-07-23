// 연금 대시보드 JavaScript

class PensionDashboard {
    constructor() {
        this.apiBase = '/api';
        this.charts = {};
        this.userId = this.generateUserId();
        this.init();
    }

    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }

    async init() {
        try {
            await this.loadMarketSummary();
            await this.loadLowFeeProducts();
            await this.loadCompanyRanking();
            await this.loadPensionStats();
            this.setupEventListeners();
            this.updateTimestamp();
        } catch (error) {
            console.error('대시보드 초기화 실패:', error);
            this.showError('데이터 로딩 중 오류가 발생했습니다.');
        }
    }

    async loadMarketSummary() {
        try {
            const response = await fetch(`${this.apiBase}/market-summary`);
            const result = await response.json();
            
            if (result.success && result.data) {
                const data = result.data;
                document.getElementById('totalProducts').textContent = 
                    this.formatNumber(data.totalProducts);
                document.getElementById('averageFeeRate').textContent = 
                    `${data.averageFeeRate}%`;
                document.getElementById('averageEarnRate').textContent = 
                    `${data.averageEarnRate}%`;
                document.getElementById('lowestFeeRate').textContent = 
                    `${data.lowestFeeRate}%`;
            }
        } catch (error) {
            console.error('시장 요약 로딩 실패:', error);
        }
    }

    async loadLowFeeProducts() {
        try {
            const response = await fetch(`${this.apiBase}/low-fee-products?limit=10`);
            const result = await response.json();
            
            if (result.success && result.data) {
                this.displayLowFeeProducts(result.data);
            }
        } catch (error) {
            console.error('저비용 상품 로딩 실패:', error);
            this.showTableError('lowFeeProductsTable', '데이터 로딩 실패');
        }
    }

    displayLowFeeProducts(products) {
        const tbody = document.getElementById('lowFeeProductsTable');
        tbody.innerHTML = '';
        
        if (products.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted">데이터가 없습니다</td>
                </tr>
            `;
            return;
        }

        products.forEach(product => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>
                    <span class="rank-badge ${this.getRankClass(product.rank)}">
                        ${product.rank}
                    </span>
                </td>
                <td class="fw-semibold">${product.company}</td>
                <td>
                    <div class="product-name" title="${product.product}">
                        ${this.truncateText(product.product, 30)}
                    </div>
                </td>
                <td>
                    <span class="badge bg-secondary">${product.productType}</span>
                </td>
                <td class="highlight-number fee-rate-low">
                    ${product.avgFeeRate3}%
                </td>
                <td class="highlight-number">
                    ${product.avgEarnRate3}%
                </td>
                <td>
                    <span class="guarantee-badge ${product.guarantees ? 'guarantee-yes' : 'guarantee-no'}">
                        ${product.guarantees ? '보장' : '미보장'}
                    </span>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadCompanyRanking() {
        try {
            const response = await fetch(`${this.apiBase}/company-ranking`);
            const result = await response.json();
            
            if (result.success && result.data) {
                this.displayCompanyRanking(result.data.slice(0, 10)); // 상위 10개만 표시
            }
        } catch (error) {
            console.error('회사 순위 로딩 실패:', error);
            this.showError('회사 순위 데이터 로딩에 실패했습니다.');
        }
    }

    displayCompanyRanking(companies) {
        const container = document.getElementById('companyRankingList');
        container.innerHTML = '';
        
        if (companies.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">데이터가 없습니다</p>';
            return;
        }

        companies.forEach(company => {
            const item = document.createElement('div');
            item.className = 'company-ranking-item';
            item.innerHTML = `
                <div class="d-flex align-items-center">
                    <span class="rank-badge ${this.getRankClass(company.rank)} me-2">
                        ${company.rank}
                    </span>
                    <div class="flex-grow-1">
                        <div class="company-name">${company.company}</div>
                        <div class="text-muted small">${company.area}</div>
                    </div>
                    <div class="text-end">
                        <div class="fee-rate">${company.avgFeeRate3}%</div>
                        <div class="text-muted small">수수료</div>
                    </div>
                </div>
            `;
            container.appendChild(item);
        });
    }

    async loadPensionStats() {
        try {
            const response = await fetch(`${this.apiBase}/pension-statistics`);
            const result = await response.json();
            
            if (result.success && result.data && result.data.list) {
                this.createPensionChart(result.data.list);
            }
        } catch (error) {
            console.error('연금 통계 로딩 실패:', error);
        }
    }

    createPensionChart(statsData) {
        const ctx = document.getElementById('pensionStatsChart');
        if (!ctx) return;

        // 데이터 정리 (최근 5년)
        const years = [...new Set(statsData.map(item => item.year))].sort().slice(-5);
        const items = [...new Set(statsData.map(item => item.item))];
        
        const datasets = items.map((item, index) => {
            const data = years.map(year => {
                const record = statsData.find(s => s.year === year && s.item === item);
                return record ? record.value : 0;
            });
            
            const colors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0'];
            
            return {
                label: item,
                data: data,
                backgroundColor: colors[index % colors.length],
                borderColor: colors[index % colors.length],
                borderWidth: 2
            };
        });

        this.charts.pensionStats = new Chart(ctx, {
            type: 'line',
            data: {
                labels: years,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '연금별 적립금 추이 (조원)'
                    },
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '적립금 (조원)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '연도'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    setupEventListeners() {
        // AI 채팅 이벤트
        this.setupChatEventListeners();
        
        // 상품 검색 폼 (기존 코드는 제거하고 챗봇으로 대체)
        // const searchForm = document.getElementById('productSearchForm');
        // if (searchForm) {
        //     searchForm.addEventListener('submit', (e) => {
        //         e.preventDefault();
        //         this.handleProductSearch();
        //     });
        // }
    }

    setupChatEventListeners() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendChatBtn');
        const quickQuestionBtns = document.querySelectorAll('.quick-question-btn');

        // 전송 버튼 클릭
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Enter 키로 메시지 전송
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 빠른 질문 버튼들
        quickQuestionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.getAttribute('data-question');
                chatInput.value = question;
                this.sendMessage();
            });
        });
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message) return;

        // 사용자 메시지 표시
        this.addMessageToChat(message, 'user');
        chatInput.value = '';

        // 타이핑 인디케이터 표시
        this.showTypingIndicator();

        try {
            // 사용자 프로필 수집
            const userProfile = this.getUserProfile();
            
            // API 호출
            const response = await fetch(`${this.apiBase}/ai-chat-with-profile`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.userId,
                    user_profile: userProfile
                })
            });

            const result = await response.json();
            
            // 타이핑 인디케이터 제거
            this.hideTypingIndicator();

            if (result.success) {
                this.addMessageToChat(result.response, 'ai');
            } else {
                // 더 자세한 에러 메시지 표시
                const errorMsg = result.error || '서버 오류가 발생했습니다';
                const detailedError = `죄송합니다. 오류가 발생했습니다: ${errorMsg}`;
                this.addMessageToChat(detailedError, 'ai', true);
                console.error('AI Chat Error:', result);
            }

        } catch (error) {
            console.error('메시지 전송 실패:', error);
            this.hideTypingIndicator();
            this.addMessageToChat('네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'ai', true);
        }
    }

    getUserProfile() {
        const age = parseInt(document.getElementById('userAge').value) || null;
        const income = parseInt(document.getElementById('userIncome').value) || null;
        const risk = document.getElementById('userRisk').value || null;
        const retirement = parseInt(document.getElementById('userRetirement').value) || null;

        // 값이 있는 경우만 포함
        const profile = {};
        if (age) profile.age = age;
        if (income) profile.monthly_income = income;
        if (risk) profile.risk_preference = risk;
        if (retirement) profile.target_retirement_age = retirement;

        return Object.keys(profile).length > 0 ? profile : null;
    }

    addMessageToChat(message, sender, isError = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        const timestamp = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.className = sender === 'user' ? 'user-message' : 'ai-message';
        if (isError) messageDiv.classList.add('error-message');
        
        const icon = sender === 'user' ? '<i class="fas fa-user me-2"></i>' : '<i class="fas fa-robot me-2"></i>';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${sender === 'ai' ? icon : ''}
                ${this.formatMessage(message)}
                ${sender === 'user' ? icon : ''}
            </div>
            <div class="message-timestamp">${timestamp}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    formatMessage(message) {
        // 마크다운 스타일 간단 변환
        return message
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.className = 'ai-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <i class="fas fa-robot me-2"></i>
                <span class="typing-dots">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </span>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async handleProductSearch() {
        const company = document.getElementById('companySearch').value.trim();
        const productType = document.getElementById('productTypeSearch').value;
        const maxFeeRate = parseFloat(document.getElementById('maxFeeRate').value) || null;
        const minEarnRate = parseFloat(document.getElementById('minEarnRate').value) || null;

        try {
            const params = new URLSearchParams();
            if (company) params.append('company', company);
            if (productType) params.append('product_type', productType);
            if (maxFeeRate !== null) params.append('max_fee_rate', maxFeeRate);
            if (minEarnRate !== null) params.append('min_earn_rate', minEarnRate);

            const response = await fetch(`${this.apiBase}/products/search?${params}`);
            const result = await response.json();

            if (result.success) {
                this.displaySearchResults(result.data);
            } else {
                this.showError('검색 중 오류가 발생했습니다.');
            }
        } catch (error) {
            console.error('상품 검색 실패:', error);
            this.showError('검색 중 오류가 발생했습니다.');
        }
    }

    displaySearchResults(products) {
        const resultsContainer = document.getElementById('searchResults');
        const resultsList = document.getElementById('searchResultsList');
        
        resultsList.innerHTML = '';
        
        if (products.length === 0) {
            resultsList.innerHTML = '<p class="text-muted">검색 결과가 없습니다.</p>';
        } else {
            products.slice(0, 20).forEach(product => { // 최대 20개 결과
                const item = document.createElement('div');
                item.className = 'search-result-item';
                item.innerHTML = `
                    <div class="product-name">${product.product}</div>
                    <div class="product-details">
                        <span class="badge bg-primary me-2">${product.company}</span>
                        <span class="badge bg-secondary me-2">${product.productType}</span>
                        <span class="text-muted me-2">수수료: ${product.avgFeeRate3}%</span>
                        <span class="text-muted me-2">수익률: ${product.avgEarnRate3}%</span>
                        <span class="guarantee-badge ${product.guarantees ? 'guarantee-yes' : 'guarantee-no'}">
                            ${product.guarantees ? '원금보장' : '미보장'}
                        </span>
                    </div>
                `;
                resultsList.appendChild(item);
            });
            
            if (products.length > 20) {
                const moreInfo = document.createElement('p');
                moreInfo.className = 'text-muted text-center mt-2';
                moreInfo.textContent = `총 ${products.length}개 결과 중 20개만 표시됩니다.`;
                resultsList.appendChild(moreInfo);
            }
        }
        
        resultsContainer.style.display = 'block';
    }

    // 유틸리티 메서드들
    getRankClass(rank) {
        if (rank === 1) return 'rank-1';
        if (rank === 2) return 'rank-2';
        if (rank === 3) return 'rank-3';
        return 'rank-other';
    }

    formatNumber(num) {
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    showError(message) {
        // 간단한 에러 표시
        console.error(message);
        // 실제로는 toast나 alert을 사용할 수 있음
    }

    showTableError(tableId, message) {
        const tbody = document.getElementById(tableId);
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-danger">
                    <i class="fas fa-exclamation-triangle me-1"></i>
                    ${message}
                </td>
            </tr>
        `;
    }

    updateTimestamp() {
        const now = new Date();
        const timestamp = now.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const lastUpdateElement = document.getElementById('lastUpdate');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = timestamp;
        }
    }
}

// 페이지 로드 후 대시보드 초기화
document.addEventListener('DOMContentLoaded', () => {
    new PensionDashboard();
});