# DRY Violation Fix Plan - Extractors

## Root Cause
I violated DRY by:
1. Renaming classes without checking dependencies
2. Fixing modules in isolation
3. Not verifying module integration
4. Creating duplicate code

## Systematic Fix Approach

### Phase 1: Dependency Mapping
- [ ] Map ALL module dependencies
- [ ] Identify what each module expects
- [ ] Document the dependency tree

### Phase 2: Fix Strategy
**Option A: Rename NoLLMExtractor to ElementsExtractorNoLLM**
- Pros: Minimal changes to with_llm
- Cons: None

**Option B: Update with_llm to use NoLLMExtractor**
- Pros: Keep current naming
- Cons: Need to update imports

**Decision: Option A (less risky)**

### Phase 3: Implementation Steps
1. **Fix the import issue**
   - Rename NoLLMExtractor → ElementsExtractorNoLLM in no_llm.py
   - This will fix the broken import in with_llm.py

2. **Remove duplicate code from with_llm**
   - Delete `_filter_interactive_elements` (use base class version)
   - Delete `_create_basic_enriched_element` (use base class version)
   - Keep only LLM-specific additions

3. **Ensure proper inheritance**
   - with_llm should properly use base_extractor
   - No reimplementation of base functionality

4. **Test integration**
   - Verify both modules work
   - Verify with_llm uses no_llm properly
   - No duplicate code remains

### Phase 4: Validation Checklist
- [ ] No duplicate methods between modules
- [ ] with_llm successfully imports from no_llm
- [ ] with_llm only adds LLM functionality
- [ ] Both modules can be imported and run
- [ ] DRY principles maintained

## Lessons Learned
1. ALWAYS check dependencies before renaming
2. ALWAYS verify module integration
3. NEVER fix modules in isolation
4. ALWAYS maintain holistic view