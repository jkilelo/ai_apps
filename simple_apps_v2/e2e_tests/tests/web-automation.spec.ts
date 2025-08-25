import { test, expect } from '@playwright/test';
import { WebAutomationPage } from '../pages/WebAutomationPage';

/**
 * E2E Test Suite for Web Automation Pipeline
 * Senior QA Engineer Pattern: Comprehensive Test Coverage
 */

test.describe('Web Automation Pipeline E2E Tests', () => {
  let webAutomationPage: WebAutomationPage;
  
  test.beforeEach(async ({ page }) => {
    webAutomationPage = new WebAutomationPage(page);
    await webAutomationPage.goto();
  });
  
  test.afterEach(async ({ page }, testInfo) => {
    // Capture screenshot on failure
    if (testInfo.status !== 'passed') {
      await page.screenshot({
        path: `test-results/failures/${testInfo.title}-failure.png`,
        fullPage: true
      });
    }
  });
  
  test.describe('Happy Path - Complete Pipeline Flow', () => {
    test('should complete full 4-step pipeline successfully', async ({ page }) => {
      // Test data
      const testUrl = 'https://example.com';
      
      // Step 1: Element Extraction
      await test.step('Step 1: Extract elements from target URL', async () => {
        await expect(webAutomationPage.step1Container).toBeVisible();
        await webAutomationPage.verifyStepIsActive(1);
        
        await webAutomationPage.enterTargetUrl(testUrl);
        await webAutomationPage.submitElementExtraction();
        
        // Verify extraction completed
        await webAutomationPage.verifyErrorNotPresent();
        await webAutomationPage.captureStepScreenshot('1-extraction-complete');
      });
      
      // Step 2: Test Generation
      await test.step('Step 2: Generate test scenarios', async () => {
        await webAutomationPage.verifyStepIsActive(2);
        await expect(webAutomationPage.step2Container).toBeVisible();
        
        await webAutomationPage.waitForTestGeneration();
        
        // Verify tests were generated
        const testCount = await webAutomationPage.getGeneratedTestsCount();
        expect(testCount).toBeGreaterThan(0);
        
        await webAutomationPage.captureStepScreenshot('2-tests-generated');
        await webAutomationPage.proceedToCodeGeneration();
      });
      
      // Step 3: Code Generation
      await test.step('Step 3: Generate test code', async () => {
        await webAutomationPage.verifyStepIsActive(3);
        await expect(webAutomationPage.step3Container).toBeVisible();
        
        await webAutomationPage.waitForCodeGeneration();
        
        // Verify code was generated
        await expect(webAutomationPage.codeViewer).not.toBeEmpty();
        
        await webAutomationPage.captureStepScreenshot('3-code-generated');
        await webAutomationPage.proceedToExecution();
      });
      
      // Step 4: Code Execution
      await test.step('Step 4: Execute generated tests', async () => {
        await webAutomationPage.verifyStepIsActive(4);
        await expect(webAutomationPage.step4Container).toBeVisible();
        
        await webAutomationPage.executeTests();
        await webAutomationPage.waitForExecutionResults();
        
        // Verify execution results
        const results = await webAutomationPage.getTestExecutionResults();
        expect(results.total).toBeGreaterThan(0);
        expect(results.passed).toBeGreaterThan(0);
        
        await webAutomationPage.captureStepScreenshot('4-execution-complete');
      });
    });
  });
  
  test.describe('Input Validation', () => {
    test('should validate URL format', async () => {
      const invalidUrls = [
        '',
        'not-a-url',
        'http://',
        'ftp://example.com',
        'javascript:alert(1)',
      ];
      
      for (const url of invalidUrls) {
        await webAutomationPage.enterTargetUrl(url);
        const isValid = await webAutomationPage.validateUrlInput(url);
        expect(isValid).toBe(false);
      }
      
      const validUrls = [
        'https://example.com',
        'http://localhost:3000',
        'https://www.google.com',
      ];
      
      for (const url of validUrls) {
        await webAutomationPage.enterTargetUrl(url);
        const isValid = await webAutomationPage.validateUrlInput(url);
        expect(isValid).toBe(true);
      }
    });
    
    test('should show error for empty URL submission', async () => {
      await webAutomationPage.submitElementExtraction();
      await expect(webAutomationPage.errorMessage).toBeVisible();
      await expect(webAutomationPage.errorMessage).toContainText('URL is required');
    });
  });
  
  test.describe('Navigation and State Management', () => {
    test('should allow navigation between completed steps', async () => {
      const testUrl = 'https://example.com';
      
      // Complete step 1
      await webAutomationPage.enterTargetUrl(testUrl);
      await webAutomationPage.submitElementExtraction();
      await webAutomationPage.waitForTestGeneration();
      
      // Navigate back to step 1
      await webAutomationPage.navigateBack();
      await webAutomationPage.verifyStepIsActive(1);
      await expect(webAutomationPage.targetUrlInput).toHaveValue(testUrl);
      
      // Navigate forward to step 2
      await webAutomationPage.submitElementExtraction();
      await webAutomationPage.verifyStepIsActive(2);
    });
    
    test('should reset flow when reset button is clicked', async () => {
      const testUrl = 'https://example.com';
      
      // Progress to step 2
      await webAutomationPage.enterTargetUrl(testUrl);
      await webAutomationPage.submitElementExtraction();
      await webAutomationPage.waitForTestGeneration();
      await webAutomationPage.verifyStepIsActive(2);
      
      // Reset flow
      await webAutomationPage.resetFlow();
      
      // Verify reset
      await webAutomationPage.verifyStepIsActive(1);
      await expect(webAutomationPage.targetUrlInput).toHaveValue('');
    });
  });
  
  test.describe('Loading States and User Feedback', () => {
    test('should show loading spinner during API calls', async ({ page }) => {
      const testUrl = 'https://example.com';
      
      await webAutomationPage.enterTargetUrl(testUrl);
      
      // Start extraction and immediately check for spinner
      const extractionPromise = webAutomationPage.submitElementExtraction();
      
      // Verify loading spinner appears
      await expect(webAutomationPage.loadingSpinner).toBeVisible({ timeout: 5000 });
      
      // Wait for completion
      await extractionPromise;
      
      // Verify loading spinner disappears
      await expect(webAutomationPage.loadingSpinner).not.toBeVisible();
    });
    
    test('should disable form controls during processing', async () => {
      const testUrl = 'https://example.com';
      
      await webAutomationPage.enterTargetUrl(testUrl);
      const extractionPromise = webAutomationPage.submitElementExtraction();
      
      // Check that input is disabled during processing
      await expect(webAutomationPage.targetUrlInput).toBeDisabled();
      await expect(webAutomationPage.step1NextButton).toBeDisabled();
      
      await extractionPromise;
    });
  });
  
  test.describe('Error Handling', () => {
    test('should handle network errors gracefully', async ({ page, context }) => {
      // Block API requests to simulate network error
      await context.route('**/api/ui/element_extraction', route => {
        route.abort('failed');
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // Verify error message is shown
      await expect(webAutomationPage.errorMessage).toBeVisible();
      await expect(webAutomationPage.errorMessage).toContainText('network');
      
      // Verify user can retry
      await expect(webAutomationPage.step1NextButton).toBeEnabled();
    });
    
    test('should handle API timeout gracefully', async ({ page, context }) => {
      // Delay API response to simulate timeout
      await context.route('**/api/ui/element_extraction', async route => {
        await new Promise(resolve => setTimeout(resolve, 35000)); // Exceed timeout
        route.continue();
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      // Verify timeout error is shown
      await expect(webAutomationPage.errorMessage).toBeVisible({ timeout: 40000 });
      await expect(webAutomationPage.errorMessage).toContainText('timeout');
    });
    
    test('should handle server errors (500) gracefully', async ({ context }) => {
      await context.route('**/api/ui/element_extraction', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal server error' })
        });
      });
      
      await webAutomationPage.enterTargetUrl('https://example.com');
      await webAutomationPage.submitElementExtraction();
      
      await expect(webAutomationPage.errorMessage).toBeVisible();
      await expect(webAutomationPage.errorMessage).toContainText('server error');
    });
  });
  
  test.describe('Responsive Design', () => {
    test('should be usable on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 812 });
      
      await webAutomationPage.goto();
      
      // Verify all essential elements are visible
      await expect(webAutomationPage.targetUrlInput).toBeVisible();
      await expect(webAutomationPage.step1NextButton).toBeVisible();
      
      // Test basic interaction
      await webAutomationPage.enterTargetUrl('https://example.com');
      await expect(webAutomationPage.step1NextButton).toBeEnabled();
    });
    
    test('should adapt layout for tablet devices', async ({ page }) => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      await webAutomationPage.goto();
      
      // Verify layout adaptation
      await expect(webAutomationPage.step1Container).toBeVisible();
      await webAutomationPage.captureStepScreenshot('tablet-layout');
    });
  });
  
  test.describe('Accessibility', () => {
    test('should be keyboard navigable', async ({ page }) => {
      await webAutomationPage.goto();
      
      // Tab to URL input
      await page.keyboard.press('Tab');
      await expect(webAutomationPage.targetUrlInput).toBeFocused();
      
      // Type URL
      await page.keyboard.type('https://example.com');
      
      // Tab to submit button
      await page.keyboard.press('Tab');
      await expect(webAutomationPage.step1NextButton).toBeFocused();
      
      // Submit with Enter
      await page.keyboard.press('Enter');
      
      // Verify submission worked
      await webAutomationPage.waitForLoadingToComplete();
    });
    
    test('should have proper ARIA labels', async () => {
      const violations = await webAutomationPage.checkAccessibility();
      expect(violations).toHaveLength(0);
    });
    
    test('should support screen readers', async ({ page }) => {
      // Check for ARIA live regions
      const liveRegions = await page.locator('[aria-live]').count();
      expect(liveRegions).toBeGreaterThan(0);
      
      // Check for proper heading hierarchy
      const h1Count = await page.locator('h1').count();
      expect(h1Count).toBe(1);
    });
  });
  
  test.describe('Performance', () => {
    test('should load initial page within acceptable time', async ({ page }) => {
      const startTime = Date.now();
      await webAutomationPage.goto();
      const loadTime = Date.now() - startTime;
      
      expect(loadTime).toBeLessThan(3000); // 3 seconds max
    });
    
    test('should handle rapid user interactions', async () => {
      // Rapidly click next button multiple times
      for (let i = 0; i < 5; i++) {
        await webAutomationPage.step1NextButton.click({ force: true });
      }
      
      // Verify no duplicate requests or errors
      await webAutomationPage.verifyErrorNotPresent();
    });
  });
  
  test.describe('Data Persistence', () => {
    test('should persist data on page refresh during flow', async ({ page }) => {
      const testUrl = 'https://example.com';
      
      // Complete step 1
      await webAutomationPage.enterTargetUrl(testUrl);
      await webAutomationPage.submitElementExtraction();
      await webAutomationPage.waitForTestGeneration();
      
      // Refresh page
      await page.reload();
      
      // Verify data persists
      await webAutomationPage.verifyStepIsActive(2);
      await expect(webAutomationPage.testScenariosList).toBeVisible();
    });
  });
  
  test.describe('Security', () => {
    test('should prevent XSS attacks in URL input', async () => {
      const xssPayload = '<script>alert("XSS")</script>';
      
      await webAutomationPage.enterTargetUrl(xssPayload);
      await webAutomationPage.submitElementExtraction();
      
      // Verify script is not executed
      const alerts = [];
      webAutomationPage.page.on('dialog', dialog => {
        alerts.push(dialog.message());
        dialog.dismiss();
      });
      
      await webAutomationPage.page.waitForTimeout(1000);
      expect(alerts).toHaveLength(0);
    });
    
    test('should validate and sanitize user inputs', async () => {
      const maliciousInputs = [
        'javascript:void(0)',
        'data:text/html,<script>alert(1)</script>',
        'file:///etc/passwd',
      ];
      
      for (const input of maliciousInputs) {
        await webAutomationPage.enterTargetUrl(input);
        const isValid = await webAutomationPage.validateUrlInput(input);
        expect(isValid).toBe(false);
      }
    });
  });
});