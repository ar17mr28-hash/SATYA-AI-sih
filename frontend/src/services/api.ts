import {
  User, ApplicationItem, ComplianceRule, NotificationItem, AnalyticsData, DemoScenario, DocumentItem
} from '../types';

const API_BASE = '/api';

class ApiService {
  private getToken(): string | null {
    return localStorage.getItem('verifyai_token');
  }

  setToken(token: string) {
    localStorage.setItem('verifyai_token', token);
  }

  clearToken() {
    localStorage.removeItem('verifyai_token');
    localStorage.removeItem('verifyai_user');
  }

  private getHeaders(isMultipart = false): HeadersInit {
    const headers: Record<string, string> = {};
    if (!isMultipart) {
      headers['Content-Type'] = 'application/json';
    }
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async request<T>(url: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        ...this.getHeaders(options.body instanceof FormData),
        ...(options.headers || {})
      }
    });

    if (response.status === 401) {
      this.clearToken();
      // Optional redirect to login
    }

    if (!response.ok) {
      let errorMsg = 'An error occurred';
      try {
        const errJson = await response.json();
        errorMsg = errJson.detail || errorMsg;
      } catch (e) {
        errorMsg = response.statusText;
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  // --- Auth ---
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await this.request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.setToken(res.access_token);
    localStorage.setItem('verifyai_user', JSON.stringify(res.user));
    return res;
  }

  async register(data: { email: string; password: string; full_name: string; role?: string }): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // --- Applications ---
  async getApplications(statusFilter?: string): Promise<ApplicationItem[]> {
    const query = statusFilter ? `?status_filter=${statusFilter}` : '';
    return this.request<ApplicationItem[]>(`/applications/${query}`);
  }

  async getApplication(id: number): Promise<ApplicationItem> {
    return this.request<ApplicationItem>(`/applications/${id}`);
  }

  async createApplication(data: any): Promise<ApplicationItem> {
    return this.request<ApplicationItem>('/applications/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async submitApplication(id: number): Promise<{ message: string; reference_id: string }> {
    return this.request<{ message: string; reference_id: string }>(`/applications/${id}/submit`, {
      method: 'POST'
    });
  }

  async reauditApplication(id: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/applications/${id}/re-audit`, {
      method: 'POST'
    });
  }

  // --- Documents ---
  async uploadDocument(applicationId: number, documentType: string, file: File): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append('document_type', documentType);
    formData.append('file', file);

    return this.request<DocumentItem>(`/documents/upload/${applicationId}`, {
      method: 'POST',
      body: formData
    });
  }

  async deleteDocument(documentId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/documents/${documentId}`, {
      method: 'DELETE'
    });
  }

  getDocumentDownloadUrl(documentId: number): string {
    return `${API_BASE}/documents/${documentId}/download`;
  }

  // --- Reviews ---
  async getReviewQueue(status?: string, risk?: string, search?: string): Promise<ApplicationItem[]> {
    const params = new URLSearchParams();
    if (status) params.append('status_filter', status);
    if (risk) params.append('risk_filter', risk);
    if (search) params.append('search', search);
    const q = params.toString() ? `?${params.toString()}` : '';
    return this.request<ApplicationItem[]>(`/reviews/queue${q}`);
  }

  async recordOfficerDecision(applicationId: number, decision: string, remarks: string, query?: string): Promise<any> {
    return this.request(`/reviews/${applicationId}/decision`, {
      method: 'POST',
      body: JSON.stringify({
        decision,
        remarks,
        clarification_query: query
      })
    });
  }

  async respondToClarification(applicationId: number, response: string): Promise<any> {
    return this.request(`/reviews/${applicationId}/clarification-response`, {
      method: 'POST',
      body: JSON.stringify({ clarification_response: response })
    });
  }

  // --- Compliance Rules ---
  async getComplianceRules(): Promise<ComplianceRule[]> {
    return this.request<ComplianceRule[]>('/compliance/rules');
  }

  async createComplianceRule(rule: Partial<ComplianceRule>): Promise<ComplianceRule> {
    return this.request<ComplianceRule>('/compliance/rules', {
      method: 'POST',
      body: JSON.stringify(rule)
    });
  }

  async updateComplianceRule(id: number, rule: Partial<ComplianceRule>): Promise<ComplianceRule> {
    return this.request<ComplianceRule>(`/compliance/rules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(rule)
    });
  }

  // --- Reports ---
  getComplianceReportUrl(applicationId: number): string {
    return `${API_BASE}/reports/compliance/${applicationId}`;
  }

  // --- Analytics ---
  async getAnalytics(): Promise<AnalyticsData> {
    return this.request<AnalyticsData>('/analytics/overview');
  }

  // --- Notifications ---
  async getNotifications(): Promise<NotificationItem[]> {
    return this.request<NotificationItem[]>('/notifications/');
  }

  async getUnreadCount(): Promise<{ unread_count: number }> {
    return this.request<{ unread_count: number }>('/notifications/unread-count');
  }

  async markNotificationRead(id: number): Promise<any> {
    return this.request(`/notifications/${id}/read`, { method: 'POST' });
  }

  // --- Demo Mode ---
  async getDemoScenarios(): Promise<{ scenarios: DemoScenario[] }> {
    return this.request<{ scenarios: DemoScenario[] }>('/demo/scenarios');
  }

  async resetDemoDatabase(): Promise<{ message: string; scenarios: DemoScenario[] }> {
    return this.request<{ message: string; scenarios: DemoScenario[] }>('/demo/reset', {
      method: 'POST'
    });
  }
  // --- AI Response Verification & Evaluation Benchmark ---
  async verifyResponse(payload: {
    response_text: string;
    evidence_sources: Array<{ source_id: string; title: string; text: string; page?: number }>;
    query?: string;
    scan_security?: boolean;
  }): Promise<import('../types').VerifyResponse> {
    return this.request<import('../types').VerifyResponse>('/verify', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  async getVerificationHistory(limit = 20): Promise<import('../types').VerificationRunSummary[]> {
    return this.request<import('../types').VerificationRunSummary[]>(`/verify/history?limit=${limit}`);
  }

  async getVerificationRun(runId: string): Promise<import('../types').VerifyResponse> {
    return this.request<import('../types').VerifyResponse>(`/verify/${runId}`);
  }

  async runBenchmark(): Promise<import('../types').BenchmarkMetrics> {
    return this.request<import('../types').BenchmarkMetrics>('/benchmark/run', {
      method: 'POST'
    });
  }

  async getLatestBenchmark(): Promise<import('../types').BenchmarkMetrics> {
    return this.request<import('../types').BenchmarkMetrics>('/benchmark/latest');
  }
}

export const api = new ApiService();
