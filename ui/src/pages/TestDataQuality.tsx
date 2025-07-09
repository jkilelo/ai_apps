import React from 'react';
import { DataQualityApp } from '../components/apps/DataQuality/DataQualityApp';

export const TestDataQuality: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <DataQualityApp onClose={() => console.log('Closed')} />
    </div>
  );
};