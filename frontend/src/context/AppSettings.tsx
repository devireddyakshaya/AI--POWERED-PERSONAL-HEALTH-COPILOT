import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { VoiceType } from '../types';

export interface AppSettingsState {
  simpleMode: boolean;
  highContrast: boolean;
  largeText: boolean;
  reduceMotion: boolean;
  spokenLabels: boolean;
  voiceType: VoiceType;
}

export interface AppSettingsContextValue extends AppSettingsState {
  update: (patch: Partial<AppSettingsState>) => void;
  reset: () => void;
}

export const DEFAULT_SETTINGS: AppSettingsState = {
  simpleMode: false,
  highContrast: false,
  largeText: false,
  reduceMotion: false,
  spokenLabels: false,
  voiceType: 'system'
};

const STORAGE_KEY = 'mm_settings';

const AppSettingsContext = createContext<AppSettingsContextValue | null>(null);

const readStored = (): AppSettingsState => {
  if (typeof localStorage === 'undefined') return DEFAULT_SETTINGS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_SETTINGS;
    const parsed = JSON.parse(raw) as Partial<AppSettingsState>;
    return { ...DEFAULT_SETTINGS, ...parsed };
  } catch {
    return DEFAULT_SETTINGS;
  }
};

/**
 * AppSettingsProvider applies accessibility preferences to the document root so
 * that Simple Mode, contrast, text size and reduced motion are consistent across
 * every page. Preferences persist locally in the browser.
 */
export const AppSettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppSettingsState>(readStored);

  useEffect(() => {
    if (typeof document === 'undefined') return;
    const root = document.documentElement;
    root.classList.toggle('a11y-simple', state.simpleMode);
    root.classList.toggle('a11y-contrast', state.highContrast);
    root.classList.toggle('a11y-large-text', state.largeText);
    root.classList.toggle('a11y-reduce-motion', state.reduceMotion);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      /* storage unavailable */
    }
  }, [state]);

  const update = useCallback((patch: Partial<AppSettingsState>) => {
    setState((prev) => ({ ...prev, ...patch }));
  }, []);

  const reset = useCallback(() => setState(DEFAULT_SETTINGS), []);

  const value = useMemo<AppSettingsContextValue>(
    () => ({ ...state, update, reset }),
    [state, update, reset]
  );

  return <AppSettingsContext.Provider value={value}>{children}</AppSettingsContext.Provider>;
};

export const useAppSettings = (): AppSettingsContextValue => {
  const ctx = useContext(AppSettingsContext);
  if (!ctx) {
    throw new Error('useAppSettings must be used within an AppSettingsProvider');
  }
  return ctx;
};
