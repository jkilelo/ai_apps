import { Page, Locator, expect } from '@playwright/test';

/**
 * Page Object Model for Web Automation Pipeline
 * Senior QA Engineer Pattern: Encapsulated UI interactions
 */
export class WebAutomationPage {
  readonly page: Page;
  
  // Step indicators
  readonly stepIndicators: Locator;
  readonly activeStepIndicator: Locator;
  
  // Step 1: Element Extraction
  readonly targetUrlInput: Locator;
  readonly step1NextButton: Locator;
  readonly step1Container: Locator;
  
  // Step 2: Test Generation
  readonly step2Container: Locator;
  readonly testScenariosList: Locator;
  readonly step2NextButton: Locator;
  readonly generatedTestsCount: Locator;
  
  // Step 3: Code Generation  
  readonly step3Container: Locator;
  readonly codeViewer: Locator;
  readonly codeLanguageSelector: Locator;
  readonly step3NextButton: Locator;
  readonly downloadCodeButton: Locator;
  
  // Step 4: Code Execution
  readonly step4Container: Locator;
  readonly executeButton: Locator;
  readonly executionResults: Locator;
  readonly testResultsList: Locator;
  readonly passedTestsCount: Locator;
  readonly failedTestsCount: Locator;
  
  // Common elements
  readonly loadingSpinner: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;
  readonly resetButton: Locator;
  readonly backButton: Locator;
  
  constructor(page: Page) {
    this.page = page;
    
    // Step indicators
    this.stepIndicators = page.locator('[data-testid="step-indicator"]');
    this.activeStepIndicator = page.locator('[data-testid="step-indicator"].active');
    
    // Step 1: Element Extraction
    this.targetUrlInput = page.getByLabel('Target URL');
    this.step1NextButton = page.locator('[data-testid="step1-next"]');
    this.step1Container = page.locator('[data-testid="element-extraction"]');
    
    // Step 2: Test Generation
    this.step2Container = page.locator('[data-testid="test-generation"]');
    this.testScenariosList = page.locator('[data-testid="test-scenarios-list"]');
    this.step2NextButton = page.locator('[data-testid="step2-next"]');
    this.generatedTestsCount = page.locator('[data-testid="tests-count"]');
    
    // Step 3: Code Generation
    this.step3Container = page.locator('[data-testid="code-generation"]');
    this.codeViewer = page.locator('[data-testid="code-viewer"]');
    this.codeLanguageSelector = page.locator('[data-testid="language-selector"]');
    this.step3NextButton = page.locator('[data-testid="step3-next"]');
    this.downloadCodeButton = page.locator('[data-testid="download-code"]');
    
    // Step 4: Code Execution
    this.step4Container = page.locator('[data-testid="code-execution"]');
    this.executeButton = page.locator('[data-testid="execute-tests"]');
    this.executionResults = page.locator('[data-testid="execution-results"]');
    this.testResultsList = page.locator('[data-testid="test-results-list"]');
    this.passedTestsCount = page.locator('[data-testid="passed-count"]');
    this.failedTestsCount = page.locator('[data-testid="failed-count"]');
    
    // Common elements
    this.loadingSpinner = page.locator('[data-testid="loading-spinner"]');
    this.errorMessage = page.locator('[data-testid="error-message"]');
    this.successMessage = page.locator('[data-testid="success-message"]');
    this.resetButton = page.locator('[data-testid="reset-flow"]');
    this.backButton = page.locator('[data-testid="back-button"]');
  }
  
  /**
   * Navigate to the Web Automation page
   */
  async goto() {
    await this.page.goto('/flows/web-automation');
    await this.page.waitForLoadState('networkidle');
  }
  
  /**
   * Step 1: Enter URL and extract elements
   */
  async enterTargetUrl(url: string) {
    await this.targetUrlInput.fill(url);
    await expect(this.targetUrlInput).toHaveValue(url);
  }
  
  async submitElementExtraction() {
    await this.step1NextButton.click();
    await this.waitForLoadingToComplete();
  }
  
  /**
   * Step 2: Review and generate tests
   */
  async waitForTestGeneration() {
    await expect(this.testScenariosList).toBeVisible({ timeout: 120000 });
    await this.waitForLoadingToComplete();
  }
  
  async proceedToCodeGeneration() {
    await this.step2NextButton.click();
    await this.waitForLoadingToComplete();
  }
  
  /**
   * Step 3: Review generated code
   */
  async waitForCodeGeneration() {
    await expect(this.codeViewer).toBeVisible({ timeout: 120000 });
    await this.waitForLoadingToComplete();
  }
  
  async proceedToExecution() {
    await this.step3NextButton.click();
    await this.waitForLoadingToComplete();
  }
  
  /**
   * Step 4: Execute tests
   */
  async executeTests() {
    await this.executeButton.click();
    await this.waitForLoadingToComplete();
  }
  
  async waitForExecutionResults() {
    await expect(this.executionResults).toBeVisible({ timeout: 120000 });
    await this.waitForLoadingToComplete();
  }
  
  /**
   * Utility methods
   */
  async waitForLoadingToComplete() {
    // Wait for loading spinner to appear and disappear
    if (await this.loadingSpinner.isVisible()) {
      await expect(this.loadingSpinner).not.toBeVisible({ timeout: 120000 });
    }
    await this.page.waitForLoadState('networkidle');
  }
  
  async getCurrentStep(): Promise<number> {
    const activeStep = await this.activeStepIndicator.getAttribute('data-step');
    return parseInt(activeStep || '1');
  }
  
  async verifyStepIsActive(stepNumber: number) {
    const currentStep = await this.getCurrentStep();
    expect(currentStep).toBe(stepNumber);
  }
  
  async verifyErrorNotPresent() {
    await expect(this.errorMessage).not.toBeVisible();
  }
  
  async verifySuccessMessage(message?: string) {
    await expect(this.successMessage).toBeVisible();
    if (message) {
      await expect(this.successMessage).toContainText(message);
    }
  }
  
  async resetFlow() {
    await this.resetButton.click();
    await this.page.waitForLoadState('networkidle');
    await this.verifyStepIsActive(1);
  }
  
  async navigateBack() {
    await this.backButton.click();
    await this.waitForLoadingToComplete();
  }
  
  /**
   * Validation methods
   */
  async validateUrlInput(url: string): Promise<boolean> {
    await this.enterTargetUrl(url);
    const isValid = await this.step1NextButton.isEnabled();
    return isValid;
  }
  
  async getGeneratedTestsCount(): Promise<number> {
    const countText = await this.generatedTestsCount.textContent();
    return parseInt(countText?.match(/\d+/)?.[0] || '0');
  }
  
  async getTestExecutionResults(): Promise<{
    passed: number;
    failed: number;
    total: number;
  }> {
    const passed = parseInt(await this.passedTestsCount.textContent() || '0');
    const failed = parseInt(await this.failedTestsCount.textContent() || '0');
    return {
      passed,
      failed,
      total: passed + failed
    };
  }
  
  /**
   * Screenshot methods for visual validation
   */
  async captureStepScreenshot(stepName: string) {
    await this.page.screenshot({
      path: `test-results/screenshots/step-${stepName}.png`,
      fullPage: true
    });
  }
  
  /**
   * Accessibility checks
   */
  async checkAccessibility() {
    const violations = await this.page.evaluate(() => {
      // This would typically use axe-core or similar
      // Simplified check for demo
      const elements = document.querySelectorAll('button, input, a');
      const issues: string[] = [];
      
      elements.forEach(el => {
        if (!el.getAttribute('aria-label') && !el.textContent?.trim()) {
          issues.push(`Element ${el.tagName} missing accessible label`);
        }
      });
      
      return issues;
    });
    
    return violations;
  }
}