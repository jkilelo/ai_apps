# Migration Guide: Enhancing Your html.py

This guide shows how to gradually add advanced features to your existing `html.py` without breaking current functionality.

## Quick Wins (Easy to Implement)

### 1. Add CSRF Protection (5 minutes)
```python
# In FormWizard.__init__, add:
import secrets
self.csrf_token = secrets.token_urlsafe(32)

# In generate_html(), add after <form> tag:
<input type="hidden" name="csrf_token" value="{self.csrf_token}">
```

### 2. Add Real-time Validation (10 minutes)
```python
# Add to _generate_scripts():
document.querySelectorAll('input, select, textarea').forEach(field => {
    let timeout;
    field.addEventListener('input', (e) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            if (!e.target.checkValidity()) {
                e.target.classList.add('error');
            } else {
                e.target.classList.remove('error');
            }
        }, 500);
    });
});
```

### 3. Add Loading States (5 minutes)
```python
# Add to _generate_scripts():
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

// Add to form submission:
submitBtn.addEventListener('click', function() {
    showLoading(this);
});
```

## Medium Complexity (30 minutes each)

### 4. Add File Upload Support
```python
# Add new field type to FieldType enum:
FILE_DRAG = "file-drag"

# In FormField.render(), add:
elif self.type == FieldType.FILE_DRAG:
    field_html += f'''
        <div class="file-upload-area" onclick="document.getElementById('{field_id}').click()">
            <input type="file" id="{field_id}" name="{self.name}" 
                   accept="{','.join(self.attributes.get('accept', []))}" 
                   style="display: none;" onchange="handleFileSelect(this)">
            <p>Click or drag files here</p>
            <div id="{field_id}_preview"></div>
        </div>
    '''
```

### 5. Add Autocomplete Fields
```python
# Add to FieldType enum:
AUTOCOMPLETE = "autocomplete"

# Add data source to FormField:
autocomplete_source: Optional[Union[List[str], str]] = None

# In render():
elif self.type == FieldType.AUTOCOMPLETE:
    field_html += f'''
        <input type="text" id="{field_id}" name="{self.name}" 
               list="{field_id}_list" {attrs_str}>
        <datalist id="{field_id}_list">
            {"".join(f'<option value="{opt}">' for opt in self.autocomplete_source)}
        </datalist>
    '''
```

### 6. Add Progress Auto-save
```python
# In _generate_scripts(), modify saveProgress():
function saveProgress() {
    if (typeof(Storage) !== "undefined") {
        localStorage.setItem('formWizardData', JSON.stringify(formData));
        localStorage.setItem('formWizardStep', currentStep);
        
        // Show save indicator
        const indicator = document.createElement('div');
        indicator.className = 'save-indicator';
        indicator.textContent = 'Saved';
        document.body.appendChild(indicator);
        setTimeout(() => indicator.remove(), 2000);
    }
}

// Auto-save every 30 seconds
setInterval(saveProgress, 30000);
```

## Advanced Features (1-2 hours)

### 7. Add Form Analytics
```python
# Add to FormWizard:
def __init__(self, ..., enable_analytics=False):
    self.enable_analytics = enable_analytics
    self.analytics_endpoint = "/api/analytics"

# Add tracking script:
if self.enable_analytics:
    scripts += '''
    const analytics = {
        startTime: Date.now(),
        track(event, data) {
            fetch('{self.analytics_endpoint}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({event, data, formId: '{self.csrf_token[:8]}'})
            });
        }
    };
    
    // Track form start
    analytics.track('form_start', {step: 0});
    
    // Track step changes
    const originalChangeStep = changeStep;
    changeStep = function(direction) {
        analytics.track('step_change', {
            from: currentStep,
            to: currentStep + direction
        });
        originalChangeStep(direction);
    };
    '''
```

### 8. Add Conditional Fields
```python
# In FormField, add:
show_if: Optional[Dict[str, Any]] = None

# In render():
if self.show_if:
    # Add data attributes for conditional display
    field_html = field_html.replace(
        'class="form-field',
        f'class="form-field conditional-field" data-show-if=\'{json.dumps(self.show_if)}\''
    )

# Add to JavaScript:
function updateConditionalFields() {
    document.querySelectorAll('.conditional-field').forEach(field => {
        const condition = JSON.parse(field.dataset.showIf);
        let shouldShow = true;
        
        for (const [fieldName, expectedValue] of Object.entries(condition)) {
            if (formData[fieldName] !== expectedValue) {
                shouldShow = false;
                break;
            }
        }
        
        field.style.display = shouldShow ? 'block' : 'none';
    });
}

// Call after each input change
form.addEventListener('change', updateConditionalFields);
```

### 9. Add Multi-language Support
```python
# Add to FormWizard:
def __init__(self, ..., translations=None):
    self.translations = translations or {}
    self.current_lang = 'en'

def translate(self, key, lang=None):
    lang = lang or self.current_lang
    return self.translations.get(lang, {}).get(key, key)

# Usage in templates:
<button>{self.translate('next_button', 'Next')}</button>
```

### 10. Add Export/Import
```python
# Add methods to FormWizard:
def export_config(self) -> dict:
    """Export form configuration"""
    return {
        'title': self.title,
        'steps': [
            {
                'title': step.title,
                'fields': [
                    {
                        'name': field.name,
                        'type': field.type.value,
                        'label': field.label,
                        'validation': [vars(rule) for rule in field.validation_rules]
                    }
                    for field in step.fields
                ]
            }
            for step in self.steps
        ]
    }

@classmethod
def import_config(cls, config: dict):
    """Create FormWizard from configuration"""
    # Implementation to recreate form from config
    pass
```

## CSS Enhancements

Add these styles to make forms look more modern:

```css
/* Modern form styles */
.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
    outline: none;
    border-color: #2196F3;
    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}

/* Smooth transitions */
.form-field input,
.form-field select,
.form-field textarea {
    transition: all 0.3s ease;
}

/* Validation states */
.form-field input.error {
    border-color: #f44336;
    background-color: rgba(244, 67, 54, 0.05);
}

.form-field input:valid {
    border-color: #4CAF50;
}

/* Loading animation */
.loading {
    position: relative;
    opacity: 0.6;
    pointer-events: none;
}

.loading::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    top: 50%;
    left: 50%;
    margin: -10px;
    border: 2px solid #2196F3;
    border-radius: 50%;
    border-top-color: transparent;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Save indicator */
.save-indicator {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
```

## Testing Your Enhancements

After adding each feature:

1. **Test existing forms** still work
2. **Check browser console** for errors
3. **Test on mobile devices**
4. **Verify accessibility** with screen readers
5. **Test with slow network** conditions

## Recommended Implementation Order

1. **Week 1**: Security (CSRF) + Real-time validation
2. **Week 2**: File uploads + Autocomplete
3. **Week 3**: Analytics + Conditional fields
4. **Week 4**: Multi-language + Import/Export

## Performance Tips

- **Lazy load** advanced features only when needed
- **Debounce** validation and auto-save
- **Compress** JavaScript for production
- **Use CDN** for common libraries
- **Enable gzip** compression

## Backward Compatibility

All enhancements are designed to be **opt-in**:

```python
# Old code still works
wizard = FormWizard(title="My Form", steps=[...])

# New features are optional
wizard = FormWizard(
    title="My Form",
    steps=[...],
    enable_analytics=True,
    enable_csrf=True,
    theme="modern"
)
```

## Need Help?

- Start with **Quick Wins** for immediate improvements
- Test thoroughly after each enhancement
- Keep the original `html.py` as backup
- Consider version control for tracking changes

Your enhanced `html.py` will be a powerful, modern form generator while maintaining its original simplicity!