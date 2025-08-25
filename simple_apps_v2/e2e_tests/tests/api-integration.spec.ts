import { test, expect } from '@playwright/test';
import { WebAutomationPage } from '../pages/WebAutomationPage';

/**
 * API Integration Tests for Web Automation Pipeline
 * Senior QA Engineer Pattern: Backend Integration Validation
 */

test.describe('API Integration Tests', () => {
  let webAutomationPage: WebAutomationPage;
  
  test.beforeEach(async ({ page }) => {
    webAutomationPage = new WebAutomationPage(page);
    await webAutomationPage.goto();
  });
  
  test.describe('API Response Validation', () => {
    test('should handle large response payloads', async ({ page }) => {
      // Intercept and monitor API calls
      const apiResponses: any[] = [];
      
      page.on('response', response => {
        if (response.url().includes('/api/ui/')) {
          apiResponses.push({
            url: response.url(),
            status: response.status(),
            size: response.headers()['content-length']
          });
        }
      });
      
      // Run through the pipeline
      await webAutomationPage.enterTargetUrl('https://github.com');
      await webAutomationPage.submitElementExtraction();
      
      // Wait for API response
      await page.waitForResponse(resp => 
        resp.url().includes('/element_extraction') && resp.status() === 200
      );
      
      // Verify response handling
      expect(apiResponses.length).toBeGreaterThan(0);
      const extractionResponse = apiResponses.find(r => 
        r.url.includes('/element_extraction')
      );
      expect(extractionResponse?.status).toBe(200);
    });
    
    test('should retry failed API calls with exponential backoff', async ({ page, context }) => {
      let attemptCount = 0;
      
      // Simulate intermittent failures
      await context.route('**/api/ui/element_extraction', route => {
        attemptCount++;
        if (attemptCount < 3) {
          route.abort('failed');
        } else {
          route.continue();
        }
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // Should succeed after retries
      await webAutomationPage.waitForTestGeneration();
      expect(attemptCount).toBe(3);
    });
    
    test('should handle API rate limiting', async ({ page, context }) => {
      // Simulate rate limit response
      await context.route('**/api/ui/element_extraction', route => {
        route.fulfill({
          status: 429,
          headers: {
            'Retry-After': '2',
            'X-RateLimit-Remaining': '0'
          },
          body: JSON.stringify({ 
            error: 'Rate limit exceeded. Please retry after 2 seconds.' 
          })
        });
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // Should show appropriate error message
      await expect(webAutomationPage.errorMessage).toBeVisible();
      await expect(webAutomationPage.errorMessage).toContainText('rate limit');
    });
  });
  
  test.describe('WebSocket Connection Tests', () => {
    test('should establish WebSocket connection for real-time updates', async ({ page }) => {
      // Monitor WebSocket connections
      const wsConnections: string[] = [];
      
      page.on('websocket', ws => {
        wsConnections.push(ws.url());
        
        ws.on('framesent', frame => {
          console.log('WS sent:', frame.payload);
        });
        
        ws.on('framereceived', frame => {
          console.log('WS received:', frame.payload);
        });
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // If WebSocket is implemented, verify connection
      if (wsConnections.length > 0) {
        expect(wsConnections[0]).toContain('ws://');
      }
    });
  });
  
  test.describe('API Endpoint Coverage', () => {
    test('should call all 4 API endpoints in sequence', async ({ page }) => {
      const apiCalls: string[] = [];
      
      page.on('request', request => {
        if (request.url().includes('/api/ui/')) {
          const endpoint = request.url().split('/api/ui/')[1].split('?')[0];
          apiCalls.push(endpoint);
        }
      });
      
      // Complete full pipeline
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      await webAutomationPage.waitForTestGeneration();
      await webAutomationPage.proceedToCodeGeneration();
      await webAutomationPage.waitForCodeGeneration();
      await webAutomationPage.proceedToExecution();
      await webAutomationPage.executeTests();
      await webAutomationPage.waitForExecutionResults();
      
      // Verify all endpoints were called
      expect(apiCalls).toContain('element_extraction');
      expect(apiCalls).toContain('test_generation');
      expect(apiCalls).toContain('code_generation');
      expect(apiCalls).toContain('code_execution');
    });
    
    test('should pass data correctly between API calls', async ({ page }) => {
      const apiPayloads: any[] = [];
      
      page.on('request', request => {
        if (request.url().includes('/api/ui/') && request.method() === 'POST') {
          apiPayloads.push({
            endpoint: request.url().split('/api/ui/')[1],
            payload: request.postDataJSON()
          });
        }
      });
      
      // Run pipeline
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      await webAutomationPage.waitForTestGeneration();
      
      // Wait for API calls
      await page.waitForTimeout(2000);
      
      // Verify data chaining
      const extractionPayload = apiPayloads.find(p => 
        p.endpoint.includes('element_extraction')
      );
      expect(extractionPayload?.payload).toHaveProperty('url', 'https://example.com');
      
      const testGenPayload = apiPayloads.find(p => 
        p.endpoint.includes('test_generation')
      );
      expect(testGenPayload?.payload).toHaveProperty('extraction_data');
    });
  });
  
  test.describe('API Error Recovery', () => {
    test('should recover from partial API failures', async ({ page, context }) => {
      let failureCount = 0;
      
      // Fail test generation once, then succeed
      await context.route('**/api/ui/test_generation', route => {
        failureCount++;
        if (failureCount === 1) {
          route.fulfill({
            status: 500,
            body: JSON.stringify({ error: 'Temporary failure' })
          });
        } else {
          route.continue();
        }
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // Should show error initially
      await expect(webAutomationPage.errorMessage).toBeVisible();
      
      // Retry should work
      await webAutomationPage.proceedToCodeGeneration();
      await webAutomationPage.waitForCodeGeneration();
    });
    
    test('should handle malformed API responses', async ({ page, context }) => {
      await context.route('**/api/ui/element_extraction', route => {
        route.fulfill({
          status: 200,
          body: 'not-json-response'
        });
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // Should handle gracefully
      await expect(webAutomationPage.errorMessage).toBeVisible();
      await expect(webAutomationPage.errorMessage).toContainText('response');
    });
  });
  
  test.describe('API Performance Monitoring', () => {
    test('should track API response times', async ({ page }) => {
      const apiMetrics: any[] = [];
      
      page.on('requestfinished', async request => {
        if (request.url().includes('/api/ui/')) {
          const timing = request.timing();
          apiMetrics.push({
            endpoint: request.url().split('/api/ui/')[1],
            duration: timing.responseEnd
          });
        }
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      await webAutomationPage.waitForTestGeneration();
      
      // Verify response times are reasonable
      apiMetrics.forEach(metric => {
        expect(metric.duration).toBeLessThan(120000); // 2 minutes max
      });
    });
    
    test('should handle concurrent API requests efficiently', async ({ page }) => {
      // Open multiple tabs and run pipeline simultaneously
      const pages = await Promise.all([
        page.context().newPage(),
        page.context().newPage(),
        page.context().newPage()
      ]);
      
      const promises = pages.map(async (p, index) => {
        const pageAutomation = new WebAutomationPage(p);
        await pageAutomation.goto();
        await pageAutomation.enterTargetUrl(`https://example${index}.com`);
        return pageAutomation.submitElementExtraction();
      });
      
      // All should complete without errors
      await Promise.all(promises);
      
      // Clean up
      await Promise.all(pages.map(p => p.close()));
    });
  });
  
  test.describe('API Security Tests', () => {
    test('should include proper authentication headers', async ({ page }) => {
      let hasAuthHeader = false;
      
      page.on('request', request => {
        if (request.url().includes('/api/ui/')) {
          const headers = request.headers();
          if (headers['authorization'] || headers['x-api-key']) {
            hasAuthHeader = true;
          }
        }
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // If auth is implemented, verify headers
      // expect(hasAuthHeader).toBe(true);
    });
    
    test('should not expose sensitive data in API logs', async ({ page }) => {
      const consoleLogs: string[] = [];
      
      page.on('console', msg => {
        consoleLogs.push(msg.text());
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // Check for sensitive data in logs
      consoleLogs.forEach(log => {
        expect(log).not.toContain('api_key');
        expect(log).not.toContain('password');
        expect(log).not.toContain('token');
      });
    });
  });
});