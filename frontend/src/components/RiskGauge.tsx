

// frontend/src/components/RiskGauge.tsx
'use client';

import React, { useEffect, useState } from 'react';

// ============================================================
// 1. TYPE DEFINITIONS - What data the component needs
// ============================================================

interface RiskGaugeProps {
  score: number;              // Risk score: 0 to 100
  level: 'low' | 'medium' | 'high' | 'critical';  // Risk level
  className?: string;         // Extra CSS classes (optional)
  showDetails?: boolean;      // Show description? (optional)
  size?: 'small' | 'medium' | 'large';  // Size variant (optional)
}

// ============================================================
// 2. MAIN COMPONENT
// ============================================================

export function RiskGauge({ 
  score, 
  level, 
  className = '', 
  showDetails = true,
  size = 'medium'
}: RiskGaugeProps) {
  
  // ---------- STATE FOR ANIMATION ----------
  const [rotation, setRotation] = useState(0);
  const [animate, setAnimate] = useState(false);

  // ---------- ANIMATION EFFECT ----------
  useEffect(() => {
    setAnimate(true);
    // Map score (0-100) to angle (0-180 degrees)
    const angle = (score / 100) * 180;
    setTimeout(() => setRotation(angle), 100);
  }, [score]);

  // ============================================================
  // 3. HELPER FUNCTIONS
  // ============================================================

  // Get text color based on risk level
  const getLevelColor = () => {
    switch (level) {
      case 'low': return 'text-green-500';
      case 'medium': return 'text-yellow-500';
      case 'high': return 'text-orange-500';
      case 'critical': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  // Get badge background color
  const getLevelBg = () => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'high': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'critical': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  // Get gradient for the gauge arc
  const getGradient = () => {
    if (score <= 30) return 'from-green-400 via-green-300 to-green-200';
    if (score <= 60) return 'from-yellow-400 via-yellow-300 to-yellow-200';
    if (score <= 80) return 'from-orange-400 via-orange-300 to-orange-200';
    return 'from-red-400 via-red-300 to-red-200';
  };

  // Get icon for the level
  const getLevelIcon = () => {
    switch (level) {
      case 'low': return '✅';
      case 'medium': return '⚠️';
      case 'high': return '🚨';
      case 'critical': return '🔴';
      default: return '❓';
    }
  };

  // Get user-friendly description
  const getLevelDescription = () => {
    switch (level) {
      case 'low': return 'Document appears authentic. No issues detected.';
      case 'medium': return 'Some verification flags. Additional checks recommended.';
      case 'high': return 'Multiple risk indicators. Immediate investigation needed.';
      case 'critical': return 'Fraud alert! Take immediate action.';
      default: return 'Unknown risk level.';
    }
  };

  // Get emoji status
  const getStatusEmoji = () => {
    switch (level) {
      case 'low': return '✅ Verified';
      case 'medium': return '⚠️ Review Needed';
      case 'high': return '🚨 Flagged';
      case 'critical': return '🔴 Fraud Alert';
      default: return '❓ Unknown';
    }
  };

  // ============================================================
  // 4. SIZE CONFIGURATIONS
  // ============================================================

  const getSizeClasses = () => {
    switch (size) {
      case 'small':
        return {
          container: 'w-48 h-24',
          needle: 'w-0.5 h-20',
          circle: 'w-3 h-3',
          score: 'text-3xl',
          badge: 'text-xs px-3 py-1',
          description: 'text-xs'
        };
      case 'large':
        return {
          container: 'w-80 h-40',
          needle: 'w-1.5 h-36',
          circle: 'w-7 h-7',
          score: 'text-6xl',
          badge: 'text-base px-6 py-2',
          description: 'text-base'
        };
      default: // medium
        return {
          container: 'w-64 h-32',
          needle: 'w-1 h-28',
          circle: 'w-5 h-5',
          score: 'text-5xl',
          badge: 'text-sm px-4 py-1.5',
          description: 'text-sm'
        };
    }
  };

  const sizeClasses = getSizeClasses();

  // ============================================================
  // 5. UI RENDER
  // ============================================================

  return (
    <div className={`flex flex-col items-center ${className}`}>
      
      {/* ====== THE GAUGE ====== */}
      <div className={`relative ${sizeClasses.container} overflow-visible`}>
        
        {/* Colored background arc */}
        <div className={`
          absolute w-full h-full rounded-t-full
          bg-gradient-to-r ${getGradient()}
          opacity-80
        `} />
        
        {/* White overlay (creates the gauge shape) */}
        <div className="absolute w-full h-1/2 bg-white top-1/2" />
        
        {/* ====== THE NEEDLE ====== */}
        <div
          className={`absolute bottom-0 left-1/2 transition-all duration-1000 ease-out ${
            animate ? 'opacity-100' : 'opacity-0'
          }`}
          style={{
            transform: `translateX(-50%) rotate(${rotation}deg)`,
            transformOrigin: 'bottom center'
          }}
        >
          {/* Needle line */}
          <div className={`${sizeClasses.needle} bg-gray-800 rounded-full mx-auto shadow-lg`} />
          {/* Needle center circle */}
          <div className={`${sizeClasses.circle} bg-gray-800 rounded-full mx-auto -mt-1 shadow-lg border-2 border-white`} />
        </div>

        {/* ====== SCALE MARKS ====== */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between px-4">
          <span className="text-[10px] font-bold text-gray-500">0</span>
          <span className="text-[10px] font-bold text-gray-500">25</span>
          <span className="text-[10px] font-bold text-gray-500">50</span>
          <span className="text-[10px] font-bold text-gray-500">75</span>
          <span className="text-[10px] font-bold text-gray-500">100</span>
        </div>

        {/* ====== RISK LEVEL LABELS ====== */}
        <div className="absolute bottom-4 left-0 right-0 flex justify-between px-3">
          <span className="text-[8px] font-bold text-green-500">LOW</span>
          <span className="text-[8px] font-bold text-yellow-500">MED</span>
          <span className="text-[8px] font-bold text-orange-500">HIGH</span>
          <span className="text-[8px] font-bold text-red-500">CRIT</span>
        </div>
      </div>

      {/* ====== SCORE DISPLAY ====== */}
      <div className="mt-6 text-center w-full">
        
        {/* Big Score Number */}
        <div className="flex items-baseline justify-center gap-1">
          <span className={`${sizeClasses.score} font-bold ${getLevelColor()} transition-all duration-1000`}>
            {score}
          </span>
          <span className={`${size === 'small' ? 'text-lg' : size === 'large' ? 'text-3xl' : 'text-2xl'} font-semibold text-gray-400`}>
            / 100
          </span>
        </div>
        
        {/* ====== RISK LEVEL BADGE ====== */}
        <div className="mt-2 flex items-center justify-center gap-2">
          <span className={`
            ${sizeClasses.badge} rounded-full font-bold uppercase border-2 ${getLevelBg()}
            flex items-center gap-1
          `}>
            {getLevelIcon()} {level} Risk
          </span>
        </div>

        {/* ====== STATUS ====== */}
        <div className="mt-1">
          <span className="text-xs font-medium text-gray-500">
            {getStatusEmoji()}
          </span>
        </div>

        {/* ====== DESCRIPTION (Optional) ====== */}
        {showDetails && (
          <div className="mt-3 max-w-xs mx-auto">
            <p className={`${sizeClasses.description} text-gray-600 leading-relaxed`}>
              {getLevelDescription()}
            </p>
          </div>
        )}

        {/* ====== DETAILED BREAKDOWN (Optional extra) ====== */}
        {showDetails && score > 50 && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-xs text-gray-500">
              {level === 'high' && '⚠️ This document requires additional verification.'}
              {level === 'critical' && '🚨 This document has been flagged for fraud investigation.'}
              {level === 'medium' && '📋 Please review the verification details carefully.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}