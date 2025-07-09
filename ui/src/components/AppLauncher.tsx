import React, { Suspense, lazy } from 'react';
import { App, SubApp } from '../types/app';

// Lazy load custom app components
const DataQualityApp = lazy(() => import('./apps/DataQuality/DataQualityApp'));

interface AppLauncherProps {
  app: App;
  subApp?: SubApp;
  onClose?: () => void;
}

// Map of custom app components that don't follow the workflow pattern
const customAppComponents: Record<string, React.ComponentType<any>> = {
  'data_quality_ai': DataQualityApp,
  'data_quality_Ai': DataQualityApp,  // Alternative mapping
};

export const AppLauncher: React.FC<AppLauncherProps> = ({ app, subApp, onClose }) => {
  // Check if this is a custom component-based app
  const customKey = subApp ? `${app.name}_${subApp.name}` : app.name;
  console.log('AppLauncher - app.name:', app.name, 'subApp?.name:', subApp?.name, 'customKey:', customKey);
  const CustomComponent = customAppComponents[customKey];
  
  if (CustomComponent) {
    return (
      <Suspense 
        fallback={
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        }
      >
        <CustomComponent onClose={onClose} />
      </Suspense>
    );
  }
  
  // Return null if no custom component found (handled by workflow system)
  return null;
};