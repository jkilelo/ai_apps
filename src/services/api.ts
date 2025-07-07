/**
 * API Client for UI Web Auto Testing
 */

// Use relative URL in development to leverage Vite proxy
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export interface ElementExtractionRequest {
  web_page_url: string
  profile?: string
  include_screenshots?: boolean
  max_depth?: number
}

export interface ElementExtractionResponse {
  job_id: string
  status: string
  message: string
  started_at: string
}

export interface ElementExtractionResult {
  job_id: string
  status: string
  started_at: string
  completed_at?: string
  duration?: number
  extracted_elements?: Array<{
    id: string
    type: string
    tag: string
    text: string
    href?: string
    selector: string
    xpath: string
    attributes: Record<string, any>
    is_visible: boolean
    is_interactive: boolean
    screenshot?: string
    page_url: string
  }>
  error?: string
  metadata?: Record<string, any>
}

export interface TestGenerationRequest {
  extracted_elements: Array<any>
  test_type?: string
  framework?: string
  include_negative_tests?: boolean
}

export interface TestGenerationResponse {
  job_id: string
  status: string
  message: string
  started_at: string
}

export interface TestGenerationResult {
  job_id: string
  status: string
  started_at: string
  completed_at?: string
  duration?: number
  test_cases?: Array<{
    id: string
    name: string
    type: string
    element_id?: string
    steps: string[]
    expected_result: string
    selector?: string
    href?: string
  }>
  test_files?: Record<string, string>
  error?: string
  metadata?: Record<string, any>
}

export interface TestExecutionRequest {
  test_cases: Array<any>
  test_files?: Record<string, string>
  execution_mode?: string
  timeout?: number
  browser?: string
}

export interface TestExecutionResponse {
  job_id: string
  status: string
  message: string
  started_at: string
}

export interface TestExecutionResult {
  job_id: string
  status: string
  started_at: string
  completed_at?: string
  duration?: number
  test_results?: Array<{
    test_id: string
    test_name: string
    status: string
    duration: number
    error?: string
    screenshot?: string
    logs?: string[]
  }>
  summary?: {
    total: number
    passed: number
    failed: number
    skipped: number
    pass_rate: number
  }
  error?: string
  metadata?: Record<string, any>
}

class ApiClient {
  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    console.log(`API Request: ${options?.method || 'GET'} ${url}`)
    if (options?.body) {
      console.log('Request body:', options.body)
    }
    
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
      console.error(`API Error (${response.status}):`, error)
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log('API Response:', data)
    return data
  }

  // Element Extraction APIs
  async startElementExtraction(request: ElementExtractionRequest): Promise<ElementExtractionResponse> {
    console.log('startElementExtraction called with:', request)
    return this.fetch('/element-extraction/extract', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getElementExtractionStatus(jobId: string): Promise<ElementExtractionResult> {
    return this.fetch(`/element-extraction/extract/${jobId}`)
  }

  async getExtractionProfiles(): Promise<Array<any>> {
    return this.fetch('/element-extraction/profiles')
  }

  // Test Generation APIs
  async startTestGeneration(request: TestGenerationRequest): Promise<TestGenerationResponse> {
    return this.fetch('/test-generation/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getTestGenerationStatus(jobId: string): Promise<TestGenerationResult> {
    return this.fetch(`/test-generation/generate/${jobId}`)
  }

  // Test Execution APIs
  async startTestExecution(request: TestExecutionRequest): Promise<TestExecutionResponse> {
    return this.fetch('/test-execution/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  }

  async getTestExecutionStatus(jobId: string): Promise<TestExecutionResult> {
    return this.fetch(`/test-execution/execute/${jobId}`)
  }

  async getExecutionReport(jobId: string, format: string = 'json'): Promise<any> {
    return this.fetch(`/test-execution/results/${jobId}/report?format=${format}`)
  }

  // Polling helper
  async pollJobStatus<T>(
    jobId: string,
    statusFn: (jobId: string) => Promise<T>,
    onProgress?: (result: T) => void,
    interval: number = 2000
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const result = await statusFn(jobId)
          
          if (onProgress) {
            onProgress(result)
          }

          if ((result as any).status === 'completed') {
            resolve(result)
          } else if ((result as any).status === 'failed') {
            reject(new Error((result as any).error || 'Job failed'))
          } else {
            setTimeout(poll, interval)
          }
        } catch (error) {
          reject(error)
        }
      }

      poll()
    })
  }
}

export const apiClient = new ApiClient()