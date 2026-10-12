import type { Dict, LanguageCode, LanguageOption, PartialDict, TranslationKey } from './types';
import { en } from './en';
import { te } from './te';
import { hi } from './hi';
import { ta } from './ta';
import { kn } from './kn';
import { ml } from './ml';
import { bn } from './bn';
import { mr } from './mr';
import { gu } from './gu';
import { pa } from './pa';
import { ur } from './ur';
import { or } from './or';

export * from './types';
export { en };

/**
 * Languages offered by MediMitra AI.
 *
 * `support` is intentionally honest: only English and Telugu are complete.
 * Everything else is a partial translation whose missing strings fall back to
 * English. We never claim a language is fully supported when it is not.
 */
export const LANGUAGES: LanguageOption[] = [
  { code: 'en', label: 'English', nativeLabel: 'English', speechCode: 'en-IN', support: 'complete' },
  { code: 'te', label: 'Telugu', nativeLabel: 'తెలుగు', speechCode: 'te-IN', support: 'complete' },
  { code: 'hi', label: 'Hindi', nativeLabel: 'हिन्दी', speechCode: 'hi-IN', support: 'partial' },
  { code: 'ta', label: 'Tamil', nativeLabel: 'தமிழ்', speechCode: 'ta-IN', support: 'partial' },
  { code: 'kn', label: 'Kannada', nativeLabel: 'ಕನ್ನಡ', speechCode: 'kn-IN', support: 'partial' },
  { code: 'ml', label: 'Malayalam', nativeLabel: 'മലയാളം', speechCode: 'ml-IN', support: 'partial' },
  { code: 'bn', label: 'Bengali', nativeLabel: 'বাংলা', speechCode: 'bn-IN', support: 'partial' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'मराठी', speechCode: 'mr-IN', support: 'partial' },
  { code: 'gu', label: 'Gujarati', nativeLabel: 'ગુજરાતી', speechCode: 'gu-IN', support: 'partial' },
  { code: 'pa', label: 'Punjabi', nativeLabel: 'ਪੰਜਾਬੀ', speechCode: 'pa-IN', support: 'partial' },
  { code: 'ur', label: 'Urdu', nativeLabel: 'اردو', speechCode: 'ur-IN', support: 'partial' },
  { code: 'or', label: 'Odia', nativeLabel: 'ଓଡ଼ିଆ', speechCode: 'or-IN', support: 'partial' },
];

const LOCALES: Record<LanguageCode, PartialDict> = {
  en,
  te,
  hi,
  ta,
  kn,
  ml,
  bn,
  mr,
  gu,
  pa,
  ur,
  or,
};

export const getLanguage = (code: LanguageCode): LanguageOption =>
  LANGUAGES.find((l) => l.code === code) || LANGUAGES[0];

/** The full, always-complete English dictionary (useful for fallback + search). */
export const ENGLISH: Dict = en;

/** Every language resolved against the English fallback (never has gaps). */
export const TRANSLATIONS: Record<LanguageCode, Dict> = (
  Object.keys(LOCALES) as LanguageCode[]
).reduce((acc, code) => {
  acc[code] = { ...en, ...LOCALES[code] } as Dict;
  return acc;
}, {} as Record<LanguageCode, Dict>);

/**
 * Translate a key. Missing keys in a partial locale fall back to English, and
 * then to the key name itself so the UI never renders blank text.
 */
export const t = (lang: LanguageCode, key: TranslationKey): string => {
  const dict = LOCALES[lang];
  return dict?.[key] ?? en[key] ?? key;
};

/** True when the given language has a complete translation. */
export const isComplete = (code: LanguageCode): boolean => getLanguage(code).support === 'complete';

export type { Dict, LanguageCode, LanguageOption, PartialDict, TranslationKey };
